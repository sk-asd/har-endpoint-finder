import json
import sys
from urllib.parse import urlparse

# when a site renders in the browser but the html has no data, the data is
# coming from some xhr/fetch call. open devtools -> network, save a .har, and
# this pulls the endpoints that actually carry the data out of the noise
# (css, images, trackers, the html itself).

STATIC = (".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff",
          ".woff2", ".ttf", ".ico", ".mp4", ".webp")
API_HINTS = ("/api", "/graphql", "/gql", "/v1", "/v2", "/rest", "/rpc",
             "/data", "/query", "/search", ".json")


def score(entry):
    req = entry["request"]
    res = entry["response"]
    url = req["url"]
    path = urlparse(url).path.lower()
    mime = (res.get("content", {}).get("mimeType") or "").lower()
    size = res.get("content", {}).get("size", 0) or 0

    if any(path.endswith(e) for e in STATIC):
        return 0, []

    pts, why = 0, []

    if "json" in mime:
        pts += 5; why.append("json response")
    if any(h in path for h in API_HINTS):
        pts += 3; why.append("api-ish path")
    if req.get("queryString"):
        pts += 1; why.append("has query params")
    if req["method"] != "GET":
        pts += 1; why.append(req["method"].lower())

    body = res.get("content", {}).get("text")
    if body:
        try:
            data = json.loads(body)
            if isinstance(data, list) and data:
                pts += 4; why.append(f"returns a list of {len(data)}")
            elif isinstance(data, dict):
                keys = len(data)
                if keys:
                    pts += 3; why.append(f"json object, {keys} keys")
        except (ValueError, TypeError):
            pass

    if size > 2000:
        pts += 1; why.append(f"{size//1000}kb body")

    return pts, why


def find(har_path):
    with open(har_path, encoding="utf-8") as f:
        har = json.load(f)

    hits = []
    for e in har["log"]["entries"]:
        pts, why = score(e)
        if pts >= 5:
            hits.append((pts, e["request"]["method"], e["request"]["url"], why))

    hits.sort(key=lambda x: x[0], reverse=True)
    return hits


def main():
    if len(sys.argv) < 2:
        print("usage: python harfind.py <file.har>")
        sys.exit(1)

    hits = find(sys.argv[1])
    if not hits:
        print("no data-looking endpoints found")
        return

    print(f"{len(hits)} candidate endpoint(s), best first:\n")
    for pts, method, url, why in hits:
        print(f"[{pts:>2}] {method:<4} {url}")
        print(f"     {', '.join(why)}\n")


if __name__ == "__main__":
    main()
