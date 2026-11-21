import json, urllib.request, concurrent.futures, pathlib, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "catalog" / "stations.json"
SOURCE = "https://raw.githubusercontent.com/ekinox-ux/ondes-idf-catalogue/main/stations.json"
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"DAB-France/0.3"}), timeout=15) as response:
        return json.load(response)
def check(stream):
    try:
        req = urllib.request.Request(stream["url"], headers={"User-Agent":"DAB-France/0.3","Icy-MetaData":"0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            kind = response.headers.get("Content-Type","").lower()
            return bool(response.read(128)) and ("audio" in kind or "mpegurl" in kind or "octet-stream" in kind)
    except Exception:
        return False
def main():
    source = fetch(SOURCE)
    previous = json.loads(OUT.read_text()) if OUT.exists() else {"stations":[]}
    prior = {t["url"]:t for s in previous["stations"] for t in s["streams"]}
    stations = []
    for s in source["stations"]:
        if not s.get("dab"): continue
        streams = [dict(t) for t in s["streams"] if t["url"].startswith("https://") and "userConsentV2=" not in t["url"]]
        stations.append(dict(id=s["id"],name=s["name"],dab=s["dab"],logo=s.get("logo"),genres=s.get("genres",[]),type=s.get("type"),region="France" if s.get("dab") in ("M1","M2") else "Île-de-France",streams=streams))
    tasks = [t for s in stations for t in s["streams"]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for t, ok in zip(tasks,pool.map(check,tasks)):
            old = prior.get(t["url"],{})
            t["fails"] = 0 if ok else old.get("fails",0)+1
            t["ok"] = ok or (old.get("ok",t.get("ok",False)) and t["fails"]<3)
            t["lastChecked"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if not stations or not any(t["ok"] for t in tasks):
        raise RuntimeError("Catalogue vide ou aucun flux valide")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"schemaVersion":1,"stations":stations},ensure_ascii=False,indent=2)+"\n")
if __name__ == "__main__":
    main()
