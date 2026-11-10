import json
import urllib.parse
import urllib.request


def get_json(url):
    headers = {"User-Agent": "AI-Study-Planner/1.0 (college project)"}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def wikipedia_summary(query):
    """Returns the Wikipedia summary for a query, or None if not found / no internet."""
    try:
        search_url = ("https://en.wikipedia.org/w/api.php?action=query&list=search"
                      "&format=json&srlimit=1&srsearch=" + urllib.parse.quote(query))
        hits = get_json(search_url)["query"]["search"]
        if not hits:
            return None

        title = hits[0]["title"]
        summary_url = ("https://en.wikipedia.org/api/rest_v1/page/summary/"
                       + urllib.parse.quote(title.replace(" ", "_")))
        data = get_json(summary_url)
        return {
            "title": data.get("title", title),
            "answer": data.get("extract", ""),
            "link": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        }
    except Exception:
        return None
