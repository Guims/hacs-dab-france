import json, urllib.request, urllib.parse, concurrent.futures, pathlib, datetime, unicodedata
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
    def norm(value):
        return "".join(c for c in unicodedata.normalize("NFKD",value.lower()) if c.isalnum())
    regional = json.loads((ROOT / "catalog/regions-candidates.json").read_text())
    for entry in regional:
        if not entry.get("verified"): continue
        old_station = next((s for s in previous["stations"] if s["id"] == entry["id"]), {})
        streams = list(old_station.get("streams", []))
        logo = old_station.get("logo")
        for query in entry["queries"]:
            try:
                params = urllib.parse.urlencode({"name":query,"nameExact":"true","countrycode":"FR","hidebroken":"true","limit":30})
                items = fetch("https://de1.api.radio-browser.info/json/stations/search?"+params)
                matches = [x for x in items if norm(x["name"]) == norm(query) and x.get("url_resolved","").startswith("https://")]
                urls = {x["url_resolved"] for x in matches}
                # Ambiguous matches require manual review rather than guessing.
                if len(urls) != 1: continue
                x = matches[0]
                if not any(t["url"] == x["url_resolved"] for t in streams):
                    streams.append(dict(url=x["url_resolved"], codec=x.get("codec"), bitrate=x.get("bitrate"), format="hls" if x.get("hls") else "icecast",ok=False))
                logo = logo or x.get("favicon")
                break
            except Exception as exc:
                print(entry["name"], str(exc))
        stations.append(dict(id=entry["id"],name=entry["name"],dab=entry["dab"],region=entry["region"],type="locale",genres=[],logo=logo,streams=streams))
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
