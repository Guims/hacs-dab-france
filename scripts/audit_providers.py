import asyncio, json, re, os
from urllib.parse import urlsplit, quote
from datetime import datetime, timezone
import aiohttp

def candidates(station):
    for stream in station.get("streams", []):
        p = urlsplit(stream["url"])
        host = p.hostname or ""
        if host in ("listen.radioking.com", "play.radioking.io", "www.radioking.com"):
            m = re.fullmatch(r"/radio/(\d+)/stream/\d+/?", p.path)
            slug = m.group(1) if m else p.path.removeprefix("/play/").strip("/")
            if re.fullmatch(r"[a-zA-Z0-9_-]+", slug):
                yield "radioking", f"https://api.radioking.io/widget/radio/{quote(slug)}/track/current?format=json", ""
        if p.scheme == "https" and host and not p.username and not p.password:
            yield "icecast", f"https://{p.netloc}/status-json.xsl", p.path

def clean(value):
    s = str(value or "").strip()
    if not any(c.isalpha() for c in s):
        return ""
    if re.fullmatch(r"[A-Z]{1,5}[-_]?\d+(?:\s*-\s*[A-Z]{1,5}[-_]?\d+)?", s, re.I):
        return ""
    return s[:300]

async def probe(session, candidate):
    provider, url, mount = candidate
    out = {"provider": provider, "endpoint": url, "mount": mount, "observed": datetime.now(timezone.utc).isoformat()}
    try:
        async with asyncio.timeout(10):
            async with session.get(url, allow_redirects=False) as response:
                out["http"] = response.status
                response.raise_for_status()
                if response.status != 200:
                    return out
                chunks = bytearray()
                async for chunk in response.content.iter_chunked(8192):
                    chunks.extend(chunk)
                    if len(chunks)>262144:
                        raise ValueError("oversized_response")
                data = json.loads(chunks)
                if provider == "icecast":
                    sources = data.get("icestats", {}).get("source", [])
                    if isinstance(sources, dict):
                        sources = [sources]
                    data = next((x for x in sources if urlsplit(x.get("listenurl", "")).path == mount), {})
                out["fields"] = list(data) if isinstance(data, dict) else []
                if isinstance(data, dict):
                    artist = clean(data.get("artist"))
                    title = clean(data.get("title"))
                    out["title"] = f"{artist} - {title}" if artist and title else title
                    out["source_timestamp"] = data.get("started_at") or data.get("start_time")
    except Exception as e:
        out["error"] = type(e).__name__
    return out

async def main():
    stations = json.load(open("catalog/stations.json", encoding="utf-8"))["stations"]
    sem = asyncio.Semaphore(8)
    async with aiohttp.ClientSession(trust_env=False) as session:
        async def check(s):
            result = []
            for candidate in dict.fromkeys(candidates(s)):
                async with sem:
                    result.append(await probe(session, candidate))
            print(s["id"], len(result), sum(bool(x.get("title")) for x in result), flush=True)
            return {"id":s["id"],"results":result}
        rounds=[]
        for i in range(3):
            rounds.append(await asyncio.gather(*(check(s) for s in stations)))
            if i<2:
                await asyncio.sleep(180)
    with open("provider-audit.json","w",encoding="utf-8") as f:
        json.dump(rounds,f,ensure_ascii=False,indent=2)
    for provider in ("radioking","icecast"):
        ids={s["id"] for batch in rounds for s in batch for x in s["results"] if x["provider"]==provider and x.get("title")}
        print(provider, "stations with candidate titles:", len(ids), flush=True)

if __name__ == "__main__":
    asyncio.run(main())
