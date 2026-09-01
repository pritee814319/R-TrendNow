
from youtube_service import search_videos, get_video_statistics


def get_trending_videos(query, limit=5):
    videos = search_videos(query, max_results=10)

    if not videos:
        return []

    video_ids = [
        video["id"]["videoId"]
        for video in videos
        if "videoId" in video.get("id", {})
    ]

    statistics = get_video_statistics(video_ids)

    results = []

    for video in videos:
        video_id = video.get("id", {}).get("videoId")

        if not video_id:
            continue

        snippet = video.get("snippet", {})
        stats = statistics.get(video_id, {})

        results.append({
            "id": video_id,
            "title": snippet.get("title", "Untitled"),
            "channel": snippet.get("channelTitle", "Unknown"),
            "published": snippet.get("publishedAt", ""),
            "thumbnail": snippet.get("thumbnails", {})
                .get("high", {})
                .get("url", ""),
            "views": int(stats.get("viewCount", 0)),
            "likes": int(stats.get("likeCount", 0)),
            "url": f"https://www.youtube.com/watch?v={video_id}",
        })

    results.sort(
        key=lambda video: video["views"],
        reverse=True
    )

    return results[:limit]
