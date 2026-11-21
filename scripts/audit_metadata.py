import asyncio, json, re, os
from datetime import datetime, timezone
from urllib.parse import urlsplit
import aiohttp

def stamp():
    return datetime.now(timezone.utc).isoformat()

async def probe(session, url):
    samples = []
    result = {"host": urlsplit(url).hostname, "samples": samples}
    try:
        async with asyncio.timeout(75):
            async with session.get(url, headers={"Icy-MetaData":"1"}, allow_redirects=True, max_redirects=4) as res:
                result["http"] = res.status
                res.raise_for_status()
                interval = int(res.headers.get("icy-metaint", 0))
                if not 0 < interval <= 524288:
                    result["error"] = "no_icy"
                    return result
                while True:
                    await res.content.readexactly(interval)
                    n = (await res.content.readexactly(1))[0]*16
                    if not n:
                        continue
                    raw = await res.content.readexactly(n)
                    match = re.search(r"StreamTitle='(.*?)';", raw.decode("utf-8", errors="replace"), re.S)
                    if match:
                        title = match.group(1).strip()[:300]
                        if title and (not samples or title != samples[-1]["title"]):
                            samples.append({"at": stamp(), "title": title})
    except TimeoutError:
        result["window_complete"] = True
    except Exception as exc:
        result["error"] = type(exc).__name__
    return result

async def main():
    stations = json.load(open("catalog/stations.json", encoding="utf-8"))["stations"]
    sem = asyncio.Semaphore(12)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None, connect=8, sock_read=10), trust_env=False) as session:
        async def station(s):
            urls = list(dict.fromkeys(t["url"] for t in s.get("streams", []) if t.get("ok") and t["url"].startswith("https://") and ".m3u8" not in t["url"].lower() and t.get("format") != "hls"))[:2]
            runs = []
            for url in urls:
                async with sem:
                    runs.append(await probe(session, url))
            return {"id": s["id"], "name": s["name"], "runs": runs}
        rounds = []
        for i in range(2):
            rounds.append(await asyncio.gather(*(station(s) for s in stations)))
            if i == 0:
                await asyncio.sleep(120)
    report=[]
    for a,b in zip(*rounds):
        titles={v["title"] for row in (a,b) for run in row["runs"] for v in run["samples"] if any(c.isalpha() for c in v["title"])}
        status="changed_unverified" if len(titles)>1 else "single_unverified" if titles else "no_usable_title"
        report.append({"id":a["id"],"name":a["name"],"status":status,"rounds":[a["runs"],b["runs"]]})
    with open("metadata-audit.json","w",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
    from collections import Counter
    counts=Counter(s["status"] for s in report)
    summary="## ICY catalogue audit (not audio verification)\n\n"+f"Stations: {len(report)}\n\n"+ "\n".join(f"- {k}: {v}" for k,v in counts.items())
    print(summary)
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as f: f.write(summary+"\n")
if __name__=="__main__":
    asyncio.run(main())
