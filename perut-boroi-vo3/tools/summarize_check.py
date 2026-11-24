import json, sys
d = json.load(open(sys.argv[1]))
def findings(x, path=""):
    if isinstance(x, dict):
        if "findings" in x and isinstance(x["findings"], list):
            for f in x["findings"]:
                yield path, f
        for k, v in x.items():
            if k != "findings":
                yield from findings(v, path + "/" + k)
    elif isinstance(x, list):
        for v in x:
            yield from findings(v, path)
print({k: (v if not isinstance(v, (dict, list)) else "...") for k, v in d.items()})
for sec in d:
    if isinstance(d[sec], dict) and "ok" in d[sec]:
        print(sec, "ok=", d[sec]["ok"], "err", d[sec].get("errorCount"), "warn", d[sec].get("warningCount"))
for p, f in findings(d):
    sev = f.get("severity"); code = f.get("code") or f.get("rule") or f.get("kind")
    if sev == "info": continue
    msg = f.get("message") or f.get("detail") or ""
    print(f"[{sev}] {code} {p} :: {f.get('file','')} {f.get('selector','') or f.get('elementId','')} t={f.get('time','')} :: {msg[:260]}")
    if f.get("fixHint") or f.get("fix"): print("     fix:", (f.get("fixHint") or f.get("fix"))[:200])
