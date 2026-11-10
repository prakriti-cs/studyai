from shared.common.topic_search import (match_topics, get_topic_resources,
                                        search_links, live_youtube_videos)
from shared.common.fuzzy import fuzzy_confidence


def recommend_resources(query, level=None, top_n=3):
    if not query or not query.strip():
        return {"status": "error", "message": "Please enter a topic."}

    corrected, matches = match_topics(query, top_n=top_n, level=level)

    if matches:
        resources = []
        for topic, score in matches:
            item = get_topic_resources(topic)
            item["similarity_score"] = round(score, 3)
            item["confidence"] = fuzzy_confidence(score)
            resources.append(item)
        return {"status": "success", "query": query,
                "understood_as": corrected, "resources": resources}

    # topic not in our list, so search YouTube directly
    videos = live_youtube_videos(corrected)
    if videos:
        message = "This topic is not in our list, so these are the top YouTube results."
    else:
        message = "This topic is not in our list and YouTube could not be reached. Try the search links."

    return {"status": "not_found", "message": message, "query": query,
            "videos": videos, "search_links": search_links(query)}


if __name__ == "__main__":
    topic = input("Enter a topic: ")
    result = recommend_resources(topic)

    print("\nResource Recommender:")
    if result["status"] == "success":
        print("Understood as:", result["understood_as"])
        for item in result["resources"]:
            print(f"\n{item['topic']} ({item['level']}) score={item['similarity_score']}")
            for video in item["videos"]:
                print(f"  - {video['title']}: {video['link']}")
            print("  - More videos:", item["search_links"]["youtube"])
    else:
        print(result.get("message"))
        for video in result.get("videos", []):
            print(f"  - {video['title']} ({video['channel']}, {video['duration']}): {video['link']}")
        for name, link in result.get("search_links", {}).items():
            print(f"  {name}: {link}")
