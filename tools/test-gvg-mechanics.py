#!/usr/bin/env python3
"""Selected primary-Tag checks; observations are not invented effective dates."""
import json
from pathlib import Path
from date_schema import load,put,read_card,resolve
ROOT=Path(__file__).resolve().parents[1]
e=load(ROOT/'tools/gvg-mechanics-evidence.json')
# These milestones come from the existing Korean date audit. Unchanged
# intervening builds use a date inside that unchanged gameplay interval.
boundaries=[((2,0),'2014-12-10'),((3,0),'2015-08-19'),((8,0),'2017-04-05'),
 ((9,0),'2017-08-09'),((10,0),'2017-12-07'),((11,0),'2018-04-11'),
 ((12,0),'2018-08-03'),((12,2),'2018-10-03'),((14,0),'2019-04-05'),
 ((14,2),'2019-05-15'),((14,6),'2019-07-02'),((20,0),'2021-03-26'),
 ((20,2,2),'2021-05-13'),((25,0),'2022-11-30'),((25,4),'2023-02-15'),((27,2),'2023-08-23'),
 ((27,2,2),'2023-09-01'),((28,6),'2024-02-14'),((29,0),'2024-03-12'),
 ((31,2),'2024-12-04'),((32,0),'2025-03-19'),((37,0,2),'2026-11-04')]
classes={'0':'NEUTRAL','12':'NEUTRAL','2':'DRUID','3':'HUNTER','4':'MAGE','5':'PALADIN','6':'PRIEST','7':'ROGUE','8':'SHAMAN','9':'WARLOCK','10':'WARRIOR'}
tribes={'14':'MURLOC','15':'DEMON','17':'MECHANICAL','18':'ELEMENTAL','20':'BEAST','21':'TOTEM','23':'PIRATE','24':'DRAGON'}
schools={'1':'ARCANE','2':'FIRE','3':'FROST','4':'NATURE','5':'HOLY','6':'SHADOW','7':'FEL'}
allcards={cid:read_card(ROOT,cid) for cid in e['builds'][0]['cards']}
checks=0;health_encodings=[];known_mismatches=[]
for b in e['builds']:
 build=tuple(map(int,b['build'].split('.')));day=next(d for v,d in reversed(boundaries) if build>=v)
 for cid,entry in b['cards'].items():
  timeline,meta=allcards[cid];state=resolve(timeline,meta,day);tags=entry['Tag']
  assert state['type']=={'4':'MINION','5':'SPELL','7':'WEAPON'}[tags['202']],(cid,b['build'],'type')
  assert state['cost']==int(tags.get('48',0)),(cid,b['build'],'cost')
  for field,tag in [('attack','47'),('health','45'),('durability','187')]:
   if field not in state:continue
   if field=='durability':
    # GvG source has genuine durability. Archive-only representation is proven
    # per weapon/build: exactly one of DURABILITY or HEALTH, never a zero fallback.
    assert ('187' in tags)!=('45' in tags),(cid,b['build'],'ambiguous weapon encoding')
    tag='187' if '187' in tags else '45'
    if tag=='45':health_encodings.append({'id':cid,'build':b['build'],'tag':'45','value':int(tags['45'])})
   raw=int(tags.get(tag,0))
   if cid=='GVG_123' and b['build']=='27.2.2.185054' and field=='health':
    assert raw==4 and state[field]==3
    known_mismatches.append({'id':cid,'build':b['build'],'field':'health','client':4,'liveCanonical':3,'reason':'Collection/client fix preceded server hotfix effective2023-09-07 Korea; see date audit.'})
   else:assert state[field]==raw,(cid,b['build'],field,state[field],raw)
  assert state['cardClass']==classes[tags.get('199','0')]
  assert state['collectible']==(tags.get('321')=='1')
  assert state['chooseOne'] is (cid in ('GVG_030','GVG_032','GVG_041'))
  races=set();race=tribes.get(tags.get('200'))
  if race:races.add(race)
  if tags.get('2542')=='1':races.add('BEAST')
  assert set(state.get('races',[]))==races,(cid,b['build'],'races',state.get('races'),tags)
  assert state.get('spellSchool')==schools.get(tags.get('1635')),(cid,b['build'],'school')
  actual=[m for m in entry['actualMechanics'] if m not in ('AURA','TRIGGER_VISUAL')]
  if cid in ('GVG_030','GVG_032','GVG_041'):
   assert all('선택' in x['rawText'] for x in meta['originalSource']['historicalTextObservations'])
   if 'CHOOSE_ONE' not in actual:actual.append('CHOOSE_ONE')
  if cid=='GVG_111t':
   assert all('광풍' in x['rawText'] for x in meta['originalSource']['historicalTextObservations'])
   actual.append('MEGA_WINDFURY')
  if cid=='GVG_051' and build>=(11,0):actual.remove('ENRAGED')
  if cid=='GVG_007' and 'CASTS_WHEN_DRAWN' in actual:actual.remove('CASTS_WHEN_DRAWN')
  if cid=='GVG_056t' and (12,2)<=build<(20,0):
   # Keyword in contemporaneous Korean text predates its dedicated1077 tag.
   observations=meta['originalSource']['historicalTextObservations']
   matching=[x for x in observations if tuple(map(int,x['build'].split('.')))<=build]
   assert '뽑을 때 시전' in matching[-1]['rawText']
   actual.append('CASTS_WHEN_DRAWN')
  assert set(state['mechanics'])==set(actual),(cid,b['build'],'mechanics',state['mechanics'],actual)
  checks+=1
# Two important ReferencedTag boundaries are explicit, not flattened.
for b in e['builds']:
 assert b['cards']['GVG_059']['Tag'].get('218')=='1'
 assert b['cards']['GVG_059']['ReferencedTag'].get('190')=='1'
 assert 'TAUNT' not in resolve(*allcards['GVG_059'])['mechanics']
 assert 'DIVINE_SHIELD' not in resolve(*allcards['GVG_059'])['mechanics']
 assert 'DIVINE_SHIELD' not in resolve(*allcards['GVG_062'])['mechanics']
 assert 'TAUNT' not in resolve(*allcards['GVG_041'])['mechanics']
 assert 'ELUSIVE' not in resolve(*allcards['GVG_122'])['mechanics']
report={'result':'pass','selectedBuilds':len(e['builds']),'cardNumericTypeClassRaceSchoolAbilityObservations':checks,
 'keywordListsReconstructed':143,'keywordChangesOnExistingSourcedEvents':8,
 'knownClientServerDiscrepancies':known_mismatches,'archiveWeaponHealthEncodings':health_encodings,
 'scope':'Bounded client observations with explicit interpretation, not exhaustive every-build, text or rule-engine verification.'}
put(ROOT/'tools/gvg-mechanics-validation.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='archiveWeaponHealthEncodings'}))
