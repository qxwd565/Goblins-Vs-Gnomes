#!/usr/bin/env python3
"""Validate the bounded GvG audit without conflating client observations and live dates."""
from pathlib import Path
from datetime import date,timedelta
import copy,hashlib,importlib.util,json,re,subprocess,sys
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text())
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
spec=importlib.util.spec_from_file_location('builder',R/'tools/wrapper_api_reference.py');B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
fixtures=load('tools/gvg-current-fixtures.json')['cards'];obs=load('tools/gvg-client-numeric.json')['cards']
current={c['id']:c for c in load('cards.json')['cards']};render={c['id']:c for c in load('render.json')['cards']};legacy=load('history.json')['cards']
from date_schema import compatibility_card,read_card
docs={}
for p in (R/'data').glob('*.json'):
 timeline,meta=read_card(R,p.stem);doc=copy.deepcopy(meta['originalSource']);doc['card']=compatibility_card(R,p.stem);docs[p.stem]=doc;audit=load('tools/gvg-release-audit.json');policy=load('release-policy.json')
assert len(docs)==143 and set(docs)==set(current)==set(render)==set(fixtures)==set(obs)
assert sum(c['collectible'] for c in current.values())==123
for p in R.rglob('*.json'):json.loads(p.read_text())
def norm(s):return re.sub(r'<br\s*/?>\s*(?:</br\s*>)?|</br\s*>|\\r\\n|\\n|/n|\r\n|[\r\n]','<br></br>',s,flags=re.I)
def display(x):
 if isinstance(x,dict):
  for k,v in x.items():
   if k in ('nativeTags','nativeRawText'):continue
   if k in ('name','text','flavor') and isinstance(v,str):assert norm(v)==v,(k,v)
   else:display(v)
 elif isinstance(x,list):
  for v in x:display(v)
def forward(c,day):
 if day<c['releasedAt']:return None
 s={k:copy.deepcopy(c[k]) for k in B.SPEC_FIELDS if k in c};s['legacyArt']=c.get('legacyArt',False)
 for p in c['patches']:
  if p['date']<=day:s.update(p['changes'])
 return s
def reverse(c,day):
 if day<c['releasedAt']:return None
 s={k:copy.deepcopy(c[k]) for k in B.SPEC_FIELDS if k in c};s['legacyArt']=c.get('legacyArt',False)
 found=[h for h in c.get('history',[]) if ('from' not in h or h['from']<=day) and ('before' not in h or day<h['before'])]
 assert len(found)<=1,(c['id'],day)
 for h in found:s.update(h['changes'])
 return s
checks=0
numeric_changes={
 'GVG_006':((29,0),{'cost':4,'attack':4,'health':4}),
 'GVG_009':((27,2),{'attack':3}),
 'GVG_046':((27,2),{'cost':3,'attack':1,'health':5}),
 'GVG_050':((27,2),{'cost':2}),
 'GVG_053':((20,2,2),{'cost':5}),
 'GVG_056t':((10,0),{'cost':6}),
 'GVG_073':((27,2),{'cost':4}),
 'GVG_109':((20,0),{'cost':3,'attack':3}),
 'GVG_114':((32,0),{'cost':7}),
 # Client-only 27.2.2 observation, NOT actual gameplay health date.
 'GVG_123':((27,2,2),{'health':4})}
for root,cost in [('GVG_030',2),('GVG_032',3),('GVG_041',6)]:
 for suffix in 'ab':numeric_changes[root+suffix]=((14,2),{'cost':cost})
tribes={14:'MURLOC',15:'DEMON',17:'MECHANICAL',18:'ELEMENTAL',20:'BEAST',21:'TOTEM',23:'PIRATE',24:'DRAGON'}
classes={0:'NEUTRAL',12:'NEUTRAL',2:'DRUID',3:'HUNTER',4:'MAGE',5:'PALADIN',6:'PRIEST',7:'ROGUE',8:'SHAMAN',9:'WARLOCK',10:'WARRIOR'}
for cid,doc in docs.items():
 c=doc['card'];f=fixtures[cid]
 assert doc['schemaVersion']==2 and 'history' not in c
 assert c['initialSpecStatus']=='partially_verified'
 assert c['releasedAt']==current[cid]['releasedAt']==policy['default']['date']=='2014-12-10'
 assert c['releaseStatus']==current[cid]['releaseStatus']=='verified'
 assert c['dbfId']==current[cid]['dbfId']==f['dbfId']
 assert digest({k:c.get(k) for k in ('nativeTags','nativeRawText')})==f['nativeSourceHash'],cid
 assert digest(current[cid].get('nativeTags'))==f['currentNativeTagsHash'],cid
 actual=copy.deepcopy(current[cid]);actual.pop('history',None)
 assert digest(actual)==f['expectedNormalizedCurrentHash'],('unexpected current semantic change',cid)
 for card in (c,current[cid],render[cid]):display(card)
 # Latest raw names and text agree after established client-control formatting.
 latest=doc['historicalTextObservations'][-1]
 assert latest.get('lastObservedBuild',latest['build'])=='37.0.2.256589'
 def comparable(t):return re.sub(r'\s+','',norm(t).replace('<br></br>','').replace('[x]','').replace('$','').replace('_','').replace('#','').replace('&','').replace('{0}','1/1'))
 assert latest['name']==current[cid]['name']
 assert comparable(latest['rawText'])==comparable(current[cid]['text']),cid
 B.read_patches(c,cid)
 for p in c['patches']:assert p['date'] in c['patchSources']
 dates={c['releasedAt'],'2026-11-09','2099-12-31'}|{p['date'] for p in c['patches']}
 for d in dates:
  for offset in (-1,0,1):
   day=(date.fromisoformat(d)+timedelta(days=offset)).isoformat();assert forward(c,day)==reverse(render[cid],day),(cid,day);checks+=1
 assert legacy.get(str(c['dbfId']),{}).get('history',[])==render[cid].get('history',[])
 assert forward(c,'2099-12-31')==reverse(current[cid],'2099-12-31')
 first=obs[cid][0];assert first[0]=='2.0.0.7234'
 assert [c[k] for k in ('cost','attack','health','durability')]==first[1:5],cid
 assert c['type']=={4:'MINION',5:'SPELL',7:'WEAPON'}[first[6]]
 assert c['collectible']==bool(first[9])
 assert c['cardClass']==classes[first[8]]
 assert c['races']==([tribes[first[5]]] if first[5] else [])
 for o in obs[cid]:
  build=tuple(map(int,o[0].split('.')));state={k:c[k] for k in ('cost','attack','health','durability')}
  if cid in numeric_changes:
   threshold,changes=numeric_changes[cid]
   if build>=threshold:state.update(changes)
  assert list(state.values())==o[1:5],(cid,o[0],state,o[1:5])
  assert c['type']=={4:'MINION',5:'SPELL',7:'WEAPON'}[o[6]]
  assert c['cardClass']==classes[o[8]] and c['collectible']==bool(o[9])
def at(cid,d):return forward(docs[cid]['card'],d)
assert at('GVG_123','2023-08-22')['health']==3
assert '전투의 함성' not in at('GVG_123','2023-08-22')['text']
assert '전투의 함성' in at('GVG_123','2023-08-23')['text']
assert at('GVG_123','2023-09-06')['health']==3 and at('GVG_123','2023-09-07')['health']==4
assert at('GVG_056t','2015-08-18')['name']=='잠복한 지뢰' and at('GVG_056t','2015-08-19')['name']=='거미 지뢰'
assert at('GVG_056t','2017-12-06')['cost']==0 and at('GVG_056t','2017-12-07')['cost']==6
assert '뽑을 때 시전' not in at('GVG_056t','2018-10-02')['text'] and '뽑을 때 시전' in at('GVG_056t','2018-10-03')['text']
assert at('GVG_018','2019-07-01')['name']=='고통의 여제' and at('GVG_018','2019-07-02')['name']=='고통의 여왕'
assert '생명력 흡수' not in at('GVG_018','2017-08-08')['text'] and '생명력 흡수' in at('GVG_018','2017-08-09')['text']
for cid in ['GVG_030','GVG_034','GVG_048','GVG_076']:
 assert at(cid,'2023-02-14')['races']==['MECHANICAL'] and set(at(cid,'2023-02-15')['races'])=={'MECHANICAL','BEAST'}
assert at('GVG_042','2017-04-04')['races']==[] and at('GVG_042','2017-04-05')['races']==['ELEMENTAL']
assert '전투의 함성' in at('GVG_046','2023-08-22')['text'] and '전투의 함성' not in at('GVG_046','2023-08-23')['text']
assert '캐릭터' in at('GVG_072','2018-08-02')['text'] and '하수인' in at('GVG_072','2018-08-03')['text']
assert at('GVG_109','2021-03-25')['cost']==4 and at('GVG_109','2021-03-26')['cost']==3
assert at('GVG_114','2025-03-18')['cost']==8 and at('GVG_114','2025-03-19')['cost']==7
assert at('GVG_006','2024-03-11')['health']==3 and at('GVG_006','2024-03-12')['health']==4
for cid in ('GVG_091','GVG_122'):
 assert '모면' not in at(cid,'2024-03-11')['text'] and '모면' in at(cid,'2024-03-12')['text']
# The aura grants Elusive; do not invent an intrinsic Elusive mechanic for Wee Spellstopper.
assert 'ELUSIVE' not in current['GVG_122'].get('mechanics',[])
assert all(not p['date'].startswith('2015-12') for p in docs['GVG_075']['card']['patches'])
assert sum(not c['initialDisplayMatchesRelease'] for c in audit['cards'])==load('manifest.json')['partialInitialDisplayCardCount']
paths=[R/p for p in ('cards.json','render.json','history.json','cards-date.json','render-date.json','history-date.json')]+list((R/'data').glob('*.json'))
before={p:p.read_bytes() for p in paths}
for _ in range(2):
 subprocess.run([sys.executable,str(R/'tools/build-api.py')],check=True,capture_output=True)
 assert all(p.read_bytes()==b for p,b in before.items()),'non-idempotent builder'
print(json.dumps({'cards':143,'collectible':123,'tokensAndOptions':20,'datedEvents':sum(len(d['card']['patches']) for d in docs.values()),'forwardReverseBoundaryChecks':checks,'clientNumericObservations':sum(map(len,obs.values())),'partialInitialDisplays':load('manifest.json')['partialInitialDisplayCardCount'],'currentSemanticChanges':0,'rawEvidencePreserved':True,'twoBuildsIdempotent':True}))
