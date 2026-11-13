#!/usr/bin/env python3
"""Guard GvG Korea first real Arena availability vs later constructed release, including all 20 token parent links."""
from __future__ import annotations
import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from date_schema import read_card, resolve

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def main():
    audited = load("tools/gvg-first-use-verification-20261113.json")
    source = load("manifest.json")
    policy = load("release-policy.json")
    compiled = {x["id"]:x for x in load("cards-date.json")["cards"]}
    original_catalog = {x["id"]:x for x in load("cards.json")["cards"]}
    records = audited["cards"]
    assert audited["schema"] == 1
    assert audited["timezone"] == policy["timezone"] == "Asia/Seoul"
    arena = audited["availabilityByMode"]["arena"]
    deck = audited["availabilityByMode"]["constructed"]
    assert (arena["date"],deck["date"]) == ("2014-12-05","2014-12-10")
    assert arena["status"] == "verified-first-pool-availability"
    assert deck["status"] == "verified-first-acquisition-and-deck-use"
    assert all(s.startswith("https://") for s in arena["sources"]+deck["sources"])
    assert date.fromisoformat(arena["date"]) < date.fromisoformat(deck["date"])
    assert policy["default"] == {"date":"2014-12-10","status":"verified"}
    assert policy["cards"] == {}
    assert len(compiled) == len(original_catalog) == len(records) == source["sourceRecords"] == 143
    assert source["collectible"] == 123 and source["uncollectible"] == 20
    assert source["pendingReleaseIds"] == []
    assert {p.stem for p in (ROOT / "data").glob("*.json")} == set(compiled)
    assert {p.stem for p in (ROOT / "metadata").glob("*.json")} == set(compiled)
    assert {r["id"] for r in records} == set(compiled)
    counts=Counter()
    confirmed_parents=set()
    for row in records:
        cid=row["id"]
        card=compiled[cid]
        old=original_catalog[cid]
        timeline,meta=read_card(ROOT,cid)
        assert row["dbfId"] == card["dbfId"] == old["dbfId"],cid
        assert row["name"] == card["name"],cid
        assert row["collectible"] == card["collectible"] == old["collectible"],cid
        assert row["firstConfirmedArenaAvailabilityKst"] == arena["date"],cid
        assert row["firstConfirmedDeckAcquisitionAvailabilityKst"] == deck["date"],cid
        assert card["releasedAt"] == old["releasedAt"] == deck["date"],cid
        assert card["releaseStatus"] == old["releaseStatus"] == "verified",cid
        assert meta["release"] == {"date":deck["date"],"status":"verified"},cid
        assert meta["originalSource"]["card"]["dbfId"] == card["dbfId"],cid
        assert list(timeline)[0] == deck["date"],cid
        assert resolve(timeline,meta,(date.fromisoformat(deck["date"])-timedelta(days=1)).isoformat()) is None,cid
        assert resolve(timeline,meta,deck["date"])["id"] == cid
        counts[row["category"]]+=1
        if not card["collectible"]:
            parent_ids=row["parentCardIds"]
            assert parent_ids and len(parent_ids)==len(set(parent_ids)),cid
            for pid in parent_ids:
                assert pid in compiled and compiled[pid]["collectible"],(cid,pid)
                assert compiled[pid]["releasedAt"] == deck["date"],(cid,pid)
                _, parent_meta=read_card(ROOT,pid)
                assert card["dbfId"] in parent_meta["originalSource"]["relatedIds"],(cid,pid)
                confirmed_parents.add(pid)
        else:
            assert row["category"]=="collectible" and "parentCardIds" not in row,cid
    assert counts==Counter({"collectible":123,"sparePart":7,"chooseOne":6,"generatedEffect":7}),counts
    assert len(confirmed_parents)==15
    assert audited["counts"]["uniqueGvgSourceParents"]==len(confirmed_parents)
    assert audited["results"]["unmatchedNoncollectibleIDs"]==[]
    assert audited["results"]["wrongCanonicalConstructedDates"]==[]
    assert audited["results"]["missingManifestIDs"]==[]
    assert audited["results"]["changedExistingGameplayData"] is False
    print(json.dumps({"result":"pass","allIDs":len(records),"collectible":counts["collectible"],
        "tokens":len(records)-counts["collectible"],"parentSources":len(confirmed_parents),
        "spareParts":7,"choiceOptions":6,"generatedEffects":7,
        "arenaPreviewKst":arena["date"],"constructedKst":deck["date"],
        "canonicalReleaseDateMutations":0},ensure_ascii=False))

if __name__=="__main__":
    main()
