#!/usr/bin/env python3
"""One-time lossless GvG wrapper -> date-map migration, safe to rerun."""
from pathlib import Path
import json
import subprocess
from date_schema import load, put, migrate_document, validate_timeline
ROOT = Path(__file__).resolve().parents[1]


def main():
    catalog = load(ROOT/"cards.json")
    if catalog.get("set") != "Goblins Vs Gnomes":
        raise ValueError("GvG only")
    current = {c["id"]:c for c in catalog["cards"]}
    commit = subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    audit = {c["id"]: c for c in load(ROOT/"tools/gvg-release-audit.json")["cards"]}
    mechanics = load(ROOT/"tools/gvg-mechanics-evidence.json")
    changed = 0
    for path in sorted((ROOT/"data").glob("*.json")):
        document = load(path)
        if "card" not in document:
            validate_timeline(document)
            if not (ROOT/"metadata"/path.name).exists():
                raise ValueError(f"Missing metadata for {path.name}")
            continue
        sidecar = ROOT/"metadata"/path.name
        if sidecar.exists():
            raise ValueError(f"Refusing to overwrite migration evidence: {sidecar}")
        timeline, meta = migrate_document(document, current.get(path.stem), commit)
        reviewed = audit[path.stem]
        meta["baselineEvidence"] = {
            "numericTypeStatus": reviewed["initialNumericSpecStatus"],
            "initialDisplayMatchesRelease": reviewed["initialDisplayMatchesRelease"],
            "source": reviewed["releaseSnapshotSource"],
            "audit": "tools/gvg-release-audit.json",
        }
        meta["confidenceNote"] = "The Korean constructed release date and initial numeric/type data have source support. Exact historical Korean wording and all intermediate cosmetic edits are not fully verified. Existing partial evidence is preserved; strict lookup does not promote it."
        meta["currentOnlyFields"] = sorted(set(current[path.stem]) - set(meta["canonicalFields"]) - {"releasedAt", "releaseStatus"})
        if document.get("historicalTextObservations"):
            meta["undatedEvidence"] = {"historicalTextObservations": document["historicalTextObservations"], "reason": "Client observation ranges are not verified Korean effective dates."}
        meta["availabilityScope"] = "User-selected Korean normal-match play availability: constructed card acquisition/crafting on 2014-12-10, excluding early Arena, demos and client preloading."
        meta["abilityImplementationObservations"] = []
        previous = None
        for snapshot in mechanics["builds"]:
            entry = snapshot["cards"][path.stem]
            observed = {kind: {tag: value for tag, value in entry[kind].items() if tag in mechanics["mechanicTags"] or tag in ("296", "349", "350", "370", "377", "388", "389")} for kind in ("Tag", "ReferencedTag")}
            if observed != previous:
                meta["abilityImplementationObservations"].append({"build": snapshot["build"], "source": snapshot["source"], **observed, "dateStatus": "Client observation only; not a claimed Korean effective date."})
                previous = observed
            else:
                meta["abilityImplementationObservations"][-1]["lastObservedBuild"] = snapshot["build"]
        if path.stem == "GVG_111t":
            meta["fieldUncertainty"] = {
                "rarity": {"preservedValue": None, "meaning": "Unknown/provisional historical reconstruction, not verified historical absence or true null rarity.",
                    "observations": [
                        {"firstObservedBuild": "2.0.0.7234", "lastObservedBuild": "9.0.0.20457", "actualTag203": 5, "interpretation": "LEGENDARY raw tag"},
                        {"firstObservedBuild": "10.0.0.22611", "lastObservedBuild": "37.0.2.256589", "actualTag203Present": False}],
                    "unresolved": "Exact Korean effective date and token rarity/display semantics. No invented dated change. Initial specification remains incomplete.", "source": "tools/gvg-mechanics-evidence.json"}}
        if path.stem == "GVG_006":
            meta["formatAvailabilityObservations"] = load(ROOT/"tools/gvg-date-recheck.json")["formatLegality"]
        put(sidecar,meta)
        put(path,timeline)
        changed += 1
    print(json.dumps({"migrated":changed,"format":"date-map-1"}))


if __name__ == "__main__":
    main()
