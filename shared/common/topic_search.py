import json
import os
import urllib.parse
import urllib.request
from difflib import get_close_matches

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from shared.common.text_utils import preprocess, get_similarity_scores
from shared.database.topics_data import TOPICS

TOPIC_NAMES = list(TOPICS)
TOPIC_TEXTS = [preprocess(name + " " + data["keywords"]) for name, data in TOPICS.items()]

# all the words we know, used to fix spelling mistakes
VOCABULARY = sorted({word for text in TOPIC_TEXTS for word in text.split()})

# words that people add to a query but are not part of the topic
CHAT_WORDS = {"explain", "learn", "tutorial", "video", "videos", "course", "about", "please",
              "teach", "study", "basics", "introduction", "guide", "notes", "resources",
              "concept", "concepts", "topic", "topics", "lecture", "lectures"}

ALIASES = {"ml": "Machine Learning", "dp": "Dynamic Programming", "os": "Operating System Basics",
           "dbms": "DBMS Basics", "oop": "OOP", "oops": "OOP", "bst": "Trees", "ds": "Arrays"}

video_cache = {}


def correct_spelling(text):
    fixed = []
    for word in preprocess(text.replace("*", " star ")).split():
        if (len(word) < 4 or word in VOCABULARY or word in CHAT_WORDS
                or word in ENGLISH_STOP_WORDS):
            fixed.append(word)
            continue
        close = get_close_matches(word, VOCABULARY, n=1, cutoff=0.8)
        fixed.append(close[0] if close else word)
    return " ".join(fixed)


def match_topics(query, top_n=3, threshold=0.25, level=None):
    """Returns the corrected query and a list of (topic, score), best first."""
    corrected = correct_spelling(query)
    words = [w for w in corrected.split() if w not in CHAT_WORDS]
    scores = get_similarity_scores(TOPIC_TEXTS, " ".join(words))

    found = {}
    for word in words:
        if word in ALIASES:
            found[ALIASES[word]] = 1.0
    for score, name in sorted(zip(scores, TOPIC_NAMES), reverse=True):
        if score >= threshold:
            found.setdefault(name, float(score))

    matches = sorted(found.items(), key=lambda pair: pair[1], reverse=True)
    if matches:
        # ignore matches that are much weaker than the best one
        matches = [m for m in matches if m[1] >= 0.5 * matches[0][1]]
    if level:
        matches = [m for m in matches if TOPICS[m[0]]["level"] == level.lower()]
    return corrected, matches[:top_n]


def search_links(query):
    q = urllib.parse.quote_plus(query.strip())
    return {
        "youtube": "https://www.youtube.com/results?search_query=" + q + "+tutorial",
        "google": "https://www.google.com/search?q=" + q,
        "wikipedia": "https://en.wikipedia.org/w/index.php?search=" + q,
    }


def find_video_items(node, found):
    if isinstance(node, dict):
        if "videoRenderer" in node:
            found.append(node["videoRenderer"])
        for value in node.values():
            find_video_items(value, found)
    elif isinstance(node, list):
        for value in node:
            find_video_items(value, found)


def join_text(part):
    return "".join(run.get("text", "") for run in part.get("runs", []))


def parse_youtube_results(html, max_results=3):
    marker = "ytInitialData = "
    start = html.find(marker)
    if start == -1:
        return []
    data, _ = json.JSONDecoder().raw_decode(html[start + len(marker):])

    items = []
    find_video_items(data, items)

    videos = []
    for item in items:
        video_id = item.get("videoId")
        title = join_text(item.get("title", {}))
        if not video_id or not title:
            continue
        videos.append({
            "title": title,
            "link": "https://www.youtube.com/watch?v=" + video_id,
            "channel": join_text(item.get("ownerText", {})),
            "duration": item.get("lengthText", {}).get("simpleText", ""),
            "source": "YouTube search",
        })
        if len(videos) == max_results:
            break
    return videos


def youtube_api_search(query, max_results, api_key):
    url = ("https://www.googleapis.com/youtube/v3/search?part=snippet&type=video"
           "&maxResults=" + str(max_results) + "&q=" + urllib.parse.quote_plus(query)
           + "&key=" + api_key)
    with urllib.request.urlopen(url, timeout=6) as response:
        items = json.loads(response.read().decode("utf-8"))["items"]
    return [{"title": item["snippet"]["title"],
             "link": "https://www.youtube.com/watch?v=" + item["id"]["videoId"],
             "channel": item["snippet"].get("channelTitle", ""),
             "duration": "",
             "source": "YouTube search"} for item in items]


def youtube_page_search(query, max_results):
    url = ("https://www.youtube.com/results?sp=EgIQAQ%3D%3D&search_query="
           + urllib.parse.quote_plus(query))
    request = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "CONSENT=YES+1",
    })
    with urllib.request.urlopen(request, timeout=6) as response:
        html = response.read().decode("utf-8", errors="ignore")
    return parse_youtube_results(html, max_results)


def live_youtube_videos(query, max_results=3):
    """Top YouTube results for a query. Returns an empty list if YouTube can't be reached."""
    search_text = query.strip() + " tutorial"
    key = (search_text, max_results)
    if key in video_cache:
        return video_cache[key]

    videos = []
    try:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        if api_key:
            videos = youtube_api_search(search_text, max_results, api_key)
        if not videos:
            videos = youtube_page_search(search_text, max_results)
    except Exception:
        videos = []

    if videos:
        video_cache[key] = videos
    return videos


def get_topic_resources(topic):
    data = TOPICS.get(topic)
    if data:
        videos = [{"title": title, "link": link, "source": "curated"}
                  for title, link in data["videos"]]
        if len(videos) < 2:
            # not enough saved videos, add some from YouTube
            have = {v["link"] for v in videos}
            videos += [v for v in live_youtube_videos(topic) if v["link"] not in have]
            videos = videos[:3]
        level = data["level"]
        subtopics = data.get("subtopics", [])
        hours = data.get("hours")
    else:
        videos = live_youtube_videos(topic)
        level, subtopics, hours = None, [], None

    return {"topic": topic, "level": level, "hours": hours, "subtopics": subtopics,
            "videos": videos, "search_links": search_links(topic)}
