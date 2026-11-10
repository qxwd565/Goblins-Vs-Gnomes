#!/usr/bin/env python3
"""Independent source replay, presence/type, all-date and preservation tests."""
from __future__ import annotations
import copy, hashlib, json, subprocess, sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from date_schema import (SPECS, REMOVE, apply, delta, fold, load, put, project,
                         read_card, resolve, validate_timeline, UncertainHistory, json_equal)
ROOT=Path(__file__).resolve().parents[1]
ABILITY_RELEASE=load(ROOT/"tools/gvg-mechanics-evidence.json")["builds"][0]["cards"]
SOURCE='0149620ba64f983ef09e715452d7581e3870b5fb'


def require_source_commit(root, commit):
    result=subprocess.run(['git','cat-file','-e',commit+':data'],cwd=root,capture_output=True)
    if result.returncode:
        raise RuntimeError('Pinned migration source commit unavailable: '+commit+
                           '. Fetch full history (checkout fetch-depth: 0) or explicitly fetch this commit; preservation checks cannot be skipped.')


def original(path):
    return json.loads(subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT))


def independent_expected(document, day):
    raw=copy.deepcopy(document['card'])
    if day is not None and day<raw['releasedAt']:return None
    for event in raw.get('patches',[]):
        effective = event['date']
        if raw['id'] in ('GVG_030','GVG_034','GVG_048','GVG_076') and effective=='2022-11-30':effective='2023-02-15'
        if day is None or effective<=day:
            raw.update(copy.deepcopy(event['changes']))
    # Reviewed Korean text snapshots for Piloted Shredder.  The archived
    # constructed card source contains only its modern display text.
    if raw['id']=='GVG_096':
        corrected=(
            ('2014-12-10','<b>죽음의 메아리:</b> 비용이 2인 무작위 하수인을 하나 소환합니다.'),
            ('2015-04-01','<b>죽음의 메아리:</b> 무작위로 선택된 비용 2짜리 하수인 하나를 소환합니다.'),
            ('2015-08-19','<b>죽음의 메아리:</b> 비용이 2인 하수인 하나를 무작위로 소환합니다.'),
            ('2016-08-10','<b>죽음의 메아리:</b> 비용이 2인 무작위 하수인을 하나 소환합니다.'),
            ('2018-10-03','<b>죽음의 메아리:</b><br></br>비용이 2인 무작위 하수인을 소환합니다.'),
        )
        for effective,text in corrected:
            if day is None or effective<=day:raw['text']=text
    # Independent field/presence oracle, not the migration's project/fold.
    fields={'id','dbfId','name','type','cardClass','classes','rarity','collectible',
            'cost','attack','health','durability','armor','text','races','race',
            'spellSchool','mechanics','legacyArt','chooseOne'}
    result={k:copy.deepcopy(v) for k,v in raw.items() if k in fields}
    keep={'MINION':{'cost','attack','health'},'SPELL':{'cost'},'WEAPON':{'cost','attack','durability'}}[raw['type']]
    for k in {'cost','attack','health','durability','armor'}-keep:result.pop(k,None)
    for k,empty in [('race',''),('races',[]),('spellSchool','')]:
        if k in result and result[k]==empty:del result[k]
    # Independent source-derived keyword oracle (not migration lookup).
    archive=ABILITY_RELEASE[raw['id']]
    result['mechanics']=[m for m in archive['actualMechanics'] if m not in ('AURA','TRIGGER_VISUAL')]
    if raw['id'] in ('GVG_030','GVG_032','GVG_041'):result['mechanics'].append('CHOOSE_ONE')
    if raw['id']=='GVG_111t':result['mechanics'].append('MEGA_WINDFURY')
    transitions={
        'GVG_018':('2017-08-09',['LIFESTEAL']),
        'GVG_051':('2018-04-11',[]),
        'GVG_056t':('2018-10-03',['CASTS_WHEN_DRAWN']),
        'GVG_007':('2023-08-23',['RUSH']),
        'GVG_046':('2023-08-23',['TAUNT']),
        'GVG_056':('2023-08-23',['DEATHRATTLE','BATTLECRY']),
        'GVG_123':('2023-08-23',['SPELLPOWER','BATTLECRY']),
        'GVG_091':('2024-03-12',['TAUNT','ELUSIVE']),
    }
    if raw['id'] in transitions:
        boundary,value=transitions[raw['id']]
        if day is None or day>=boundary:result['mechanics']=value
    return result


def reverse(record, day):
    if record['releaseStatus']=='verified' and day<record['releasedAt']:return None
    state=copy.deepcopy(record['current']);state.pop('art',None)
    matching=[r for r in record['history'] if r.get('from','0001-01-01')<=day<r.get('before','9999-12-31')]
    assert len(matching)<=1,('overlapping intervals',record['id'],day)
    for rev in matching:
        # Independent implementation of exact reverse operations.
        for field in rev['changes'].get('__remove',[]):state.pop(field,None)
        state.update({k:copy.deepcopy(v) for k,v in rev['changes'].items() if k!='__remove'})
    return state

def fixtures():
    states=[
        {'id':'TEST','type':'MINION','cost':1,'attack':0,'health':3,'text':'Taunt','mechanics':['TAUNT']},
        {'id':'TEST','type':'SPELL','cost':0,'text':'','mechanics':[]},
        {'id':'TEST','type':'WEAPON','cost':0,'attack':1,'durability':0,'text':''},
        {'id':'TEST','type':'HERO','cost':0,'armor':5,'text':''},
        {'id':'TEST','type':'LOCATION','cost':1,'durability':2,'text':''},
        {'id':'TEST','type':'HERO_POWER','cost':0,'text':''},
        {'id':'TEST','type':'ENCHANTMENT','text':'','effectData':{'amount':0},'explicitNull':None},
    ]
    timeline={};previous={}
    for i,state in enumerate(states,1):
        timeline[f'2020-01-0{i}']=delta(previous,state);previous=state
    validate_timeline(timeline)
    assert fold(timeline,'2019-12-31') is None
    for i,state in enumerate(states,1):assert fold(timeline,f'2020-01-0{i}')==state
    assert 'attack' not in fold(timeline,'2020-01-02')
    assert fold(timeline,'2020-01-01')['attack']==0
    assert fold(timeline,'2020-01-02')['text']==''
    assert fold(timeline,'2020-01-07')['explicitNull'] is None
    assert apply({'x':None},{})=={'x':None}
    assert apply({'x':None},{REMOVE:['x']})=={}
    for before,after in ((False,0),(True,1),({'nested':[False,{'x':True}]},{'nested':[0,{'x':1}]})):
        patch=delta({'effect':before},{'effect':after})
        assert patch=={'effect':after} and patch
        assert apply({'effect':before},patch,validate=True)=={'effect':after}
    assert project({'id':'BASE','type':'HERO','health':30,'attack':0,'armor':0},native_tags=[{'id':45,'value':30}])=={'id':'BASE','type':'HERO','health':30}
    assert project({'id':'EN','type':'ENCHANTMENT','attack':0,'text':''})['attack']==0
    effect={'id':'EN','type':'ENCHANTMENT','effectData':{'amount':0},'text':'','actualZero':0,'actualFalse':False,'nullableEffect':None}
    assert project(effect,gameplay_fields={'effectData','actualZero','actualFalse','nullableEffect'})==effect
    try:project(effect)
    except ValueError:pass
    else:raise AssertionError('Unclassified effect fields silently dropped or backdated')
    raw={'id':'RAW','type':'SPELL','cost':0,'nativeSetId':1635,'installed':True,
         'techLevel':0,'battlegroundsNormalDbfId':0,'isBattlegroundsBuddy':False,
         'nativeTags':[{'id':1720,'value':1}],'releasedAt':'2013-08-17','releaseStatus':'estimated'}
    assert project(raw)=={'id':'RAW','type':'SPELL','cost':0}
    for race in ('DEMON','BEAST'):
        spell={'id':'CHOICE','type':'SPELL','cost':0,'text':'','race':race,'races':[race]}
        assert project(spell)==spell
    assert project({'id':'NO','type':'SPELL','cost':0,'race':'','races':[],'spellSchool':''})=={'id':'NO','type':'SPELL','cost':0}
    # Attribute loss creates explicit removal, never a future empty placeholder.
    before=project({'id':'RACE','type':'MINION','race':'BEAST','races':['BEAST'],'cost':1,'attack':1,'health':1})
    after=project({'id':'RACE','type':'MINION','race':'','races':[],'cost':1,'attack':1,'health':1})
    assert delta(before,after)=={REMOVE:['race','races']}
    for bad in ({'2020-02-30':states[0]}, {'2020-01-01':states[0],'2020-01-02':{'attack':0}}, {'2020-01-01':states[0],'2020-01-02':{REMOVE:['missing']}}, {'2020-01-01':states[0],'2020-01-02':{REMOVE:['attack'],'attack':1}}):
        try:validate_timeline(bad)
        except ValueError:pass
        else:raise AssertionError('Invalid/redundant timeline accepted')
    for change in ({'id':'OTHER'}, {REMOVE:['id']}, {'dbfId':456}, {REMOVE:['dbfId']}):
        bad={'2020-01-01':dict(states[0],dbfId=123),'2020-01-02':change}
        try:validate_timeline(bad)
        except ValueError:pass
        else:raise AssertionError('Card identity mutation accepted')
    for field,value in (('nativeTags',[]),('installed',True),('nativeSetId',1635),('techLevel',0),('set','LEGACY')):
        try:validate_timeline({'2020-01-01':states[0],'2020-01-02':{field:value}})
        except ValueError:pass
        else:raise AssertionError('Current-only field dated directly: '+field)


def main():
    fixtures();require_source_commit(ROOT,SOURCE)
    current={c['id']:c for c in load(ROOT/'cards-date.json')['cards']}
    rendered={c['id']:c for c in load(ROOT/'render-date.json')['cards']}
    histories=load(ROOT/'history-date.json')['cards']
    source_catalog={c['id']:c for c in original('cards.json')['cards']}
    files=sorted((ROOT/'data').glob('*.json'))
    assert {p.stem for p in files}==set(current)==set(rendered)==set(source_catalog)
    assert len(current)==len(histories)==143
    assert len({c['dbfId'] for c in current.values()})==143
    assert {p.name for p in files}=={p.name for p in (ROOT/'metadata').glob('*.json')}
    originals={p.stem:original('data/'+p.name) for p in files}
    dates={'1900-01-01','2099-12-31','2026-11-09'}
    for doc in originals.values():
        for d in [doc['card']['releasedAt']]+[e['date'] for e in doc['card']['patches']]:
            dates.update((date.fromisoformat(d)+timedelta(days=n)).isoformat() for n in (-1,0,1))
    for when in ('2015-04-01','2015-08-19','2016-08-10','2018-10-03'):
        dates.update((date.fromisoformat(when)+timedelta(days=n)).isoformat() for n in (-1,0,1))
    # Include old and corrected boundary triples; preserving source evidence
    # does not require preserving a disproven effective date.
    for when in ('2023-02-15',):
        dates.update((date.fromisoformat(when)+timedelta(days=n)).isoformat() for n in (-1,0,1))
    # All pre-existing non-output JSON evidence stays byte-identical.
    tree=subprocess.check_output(['git','ls-tree','-r','--name-only',SOURCE],cwd=ROOT,text=True).splitlines()
    preserved=[]
    for path in tree:
        if path.endswith('.json') and not path.startswith('data/') and path not in ('cards.json','render.json','history.json'):
            assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',SOURCE+':'+path],cwd=ROOT),('evidence changed',path)
            preserved.append(path)
    checks=0;patches=0;types=Counter();losses=[]
    for p in files:
        cid=p.stem;timeline,meta=read_card(ROOT,cid);doc=originals[cid]
        assert meta['sourceCommit']==SOURCE
        assert '2014-12-10' in meta['availabilityScope'] and 'excluding early Arena' in meta['availabilityScope']
        assert json_equal(meta['originalSource'],doc),(cid,'original JSON loss')
        assert json_equal(meta['currentCatalog'],source_catalog[cid]),(cid,'current metadata loss')
        assert meta['baselineStatus']=='partially-verified'
        assert meta['legacyOmittedFields']==['mechanics']
        assert meta['abilityImplementationObservations']
        assert doc['card']['chooseOne'] is (cid in ('GVG_030','GVG_032','GVG_041')) and 'chooseOne' not in meta['currentCatalog']
        assert current[cid]['chooseOne'] is rendered[cid]['chooseOne'] is doc['card']['chooseOne']
        assert meta['chooseOneEvidence']['preservedOriginalValue'] is doc['card']['chooseOne']
        assert set(rendered[cid]['currentOnlyFields']).isdisjoint(set(meta['canonicalFields']))
        if cid=='GVG_111t':
            assert meta['fieldUncertainty']['rarity']['preservedValue'] is None
            assert 'provisional' in meta['fieldUncertainty']['rarity']['meaning']
            assert next(iter(timeline.values()))['rarity'] is None
        assert meta['release']=={'date':doc['card']['releasedAt'],'status':'verified'}
        assert list(timeline)==sorted(timeline)
        assert len(timeline)==1+len(doc['card']['patches'])+(4 if cid=='GVG_096' else 0)
        validate_timeline(timeline)
        patches+=len(timeline)-1
        for day in sorted(dates):
            expected=independent_expected(doc,day)
            actual=resolve(timeline,meta,day)
            assert json_equal(actual,expected),(cid,day,'source replay',actual,expected)
            assert json_equal(reverse(histories[str(current[cid]['dbfId'])],day),expected),(cid,day,'history-date')
            render_current={k:v for k,v in rendered[cid].items() if k in SPECS}
            render_record={**histories[str(current[cid]['dbfId'])],'current':render_current,'history':rendered[cid]['history']}
            assert json_equal(reverse(render_record,day),expected),(cid,day,'render-date')
            checks+=1
        expected=independent_expected(doc,None)
        assert json_equal({k:v for k,v in current[cid].items() if k in SPECS},expected),(cid,'current')
        assert current[cid]['id']==doc['card']['id'] and current[cid]['dbfId']==doc['card']['dbfId']
        for field,value in source_catalog[cid].items():
            if field not in SPECS:assert json_equal(current[cid][field],value),(cid,field,'current-only loss')
        assert all(field not in change for change in timeline.values() for field in ('nativeTags','nativeRawText','set','portrait','installed','relatedDbfIds','flavor','art'))
        state={}
        for day,changes in timeline.items():
            next_state=apply(state,changes)
            assert json_equal(delta(state,next_state),changes),(cid,day,'redundant delta')
            if 'UNDEAD' in next_state.get('races',[]):assert day>='2022-11-30'
            if next_state.get('spellSchool'):assert day>='2021-03-26'
            if cid in ('GVG_030','GVG_034','GVG_048','GVG_076') and 'BEAST' in next_state.get('races',[]):assert day>='2023-02-15'
            state=next_state
        types[state['type']]+=1
        try:resolve(timeline,meta,'2026-11-09',strict=True)
        except UncertainHistory:pass
        else:raise AssertionError('Incomplete baseline silently promoted')
        removed={k:v for k,v in doc['card'].items() if k in SPECS and k not in next(iter(timeline.values()))}
        losses.append({'id':cid,'sourcePlaceholdersExcludedFromCanonical':removed})
    assert sum(c['chooseOne'] is True for c in current.values())==3
    assert sum(c['chooseOne'] is False for c in current.values())==140
    assert all('chooseOne' not in c for c in source_catalog.values())
    assert patches==59  # four attested historic text/line-break revisions for GVG_096
    assert types=={'MINION':100,'SPELL':38,'WEAPON':5}
    # Real zeroes survive; spells have no invented combat fields, and the
    # five source weapons already have genuine durability (no Legacy decoder).
    assert current['GVG_039']['attack']==0
    for cid in ('GVG_024', 'GVG_036', 'GVG_043', 'GVG_054', 'GVG_059'):
        assert current[cid]['durability']>0 and 'health' not in current[cid]
    assert current['GVG_028t']['cost']==0 and 'attack' not in current['GVG_028t']
    for name in ('date_schema.py','build_date_api.py','legacy_projection.py'):
        s=(ROOT/'tools'/name).read_text()
        assert 'EX1_323' not in s and 'FP1_' not in s and 'WEAPON_HEALTH_ENCODED' not in s
    report={'result':'pass','sourceCommit':SOURCE,'cards':143,'sourceDocumentsPreserved':143,
            'events':patches,'releaseDatesVerified':143,'partialExactInitialTexts':99,
            'baselineFullyVerified':0,'globalDateSamples':len(dates),'exactSourceAndTransportChecks':checks,
            'types':dict(types),'historyDateCorrections':load(ROOT/'tools/gvg-date-recheck.json')['historyDateCorrections'],'preservedChooseOneBooleans':{'true':3,'false':140}, 'reconstructedKeywordLists':143,'keywordDeltasAddedToExistingEvents':8,
            'preservedPriorEvidenceFiles':preserved,'projectionChanges':losses,'presenceFixturesPassed':True}
    put(ROOT/'tools/date-schema-validation.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('projectionChanges','preservedPriorEvidenceFiles')}))

if __name__=='__main__':main()
