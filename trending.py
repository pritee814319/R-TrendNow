from datetime import datetime, timezone

from youtube_service import (
    search_recent_videos,
    get_video_statistics
)


def calculate_trending_score(
    views,
    likes,
    comments,
    hours_old
):
    """
    Calculate a TrendHub score.

    Recent videos with strong view velocity
    and engagement receive higher scores.
    """

    hours_old = max(hours_old, 0.5)

    views_per_hour = views / hours_old

    engagement = likes + (comments * 2)

    recency_factor = 1 / (1 + hours_old / 24)

    score = (
        (views_per_hour * 0.60)
        +
        (engagement * 0.25)
        +
        (views * 0.10)
        +
        (recency_factor * 100000)
    )

    return score


def get_trending_videos(
    keywords,
    region_code="CA",
    hours=24,
    limit=5,
    category_id=None
):
    """
    Get recently published videos and rank them
    using the TrendHub trending algorithm.
    """

    all_videos = []

    # Search using multiple keywords
    for keyword in keywords:

        videos = search_recent_videos(
            query=keyword,
            region_code=region_code,
            hours=hours,
            max_results=25,
            category_id=category_id
        )

        all_videos.extend(videos)

    # Remove duplicate videos
    unique_videos = {}

    for video in all_videos:

        video_id = (
            video.get("id", {})
            .get("videoId")
        )

        if video_id:
            unique_videos[video_id] = video

    videos = list(unique_videos.values())

    if not videos:
        return []

    video_ids = list(unique_videos.keys())

    statistics = get_video_statistics(
        video_ids
    )

    results = []

    now = datetime.now(timezone.utc)

    for video in videos:

        video_id = (
            video.get("id", {})
            .get("videoId")
        )

        snippet = video.get(
            "snippet",
            {}
        )

        stats = statistics.get(
            video_id,
            {}
        )

        published_string = snippet.get(
            "publishedAt"
        )

        if not published_string:
            continue

        published_at = datetime.fromisoformat(
            published_string.replace(
                "Z",
                "+00:00"
            )
        )

        hours_old = (
            now - published_at
        ).total_seconds() / 3600

        hours_old = max(hours_old, 0.5)

        views = stats.get(
            "viewCount",
            0
        )

        likes = stats.get(
            "likeCount",
            0
        )

        comments = stats.get(
            "commentCount",
            0
        )

        score = calculate_trending_score(
            views=views,
            likes=likes,
            comments=comments,
            hours_old=hours_old
        )

        views_per_hour = views / hours_old

        results.append({
            "id": video_id,

            "title": snippet.get(
                "title",
                "Untitled"
            ),

            "channel": snippet.get(
                "channelTitle",
                "Unknown"
            ),

            "published": published_at,

            "hours_old": hours_old,

            "views": views,

            "likes": likes,

            "comments": comments,

            "views_per_hour": views_per_hour,

            "trend_score": score,

            "thumbnail": (
                snippet
                .get("thumbnails", {})
                .get("high", {})
                .get("url", "")
            ),

            "url":
                f"https://www.youtube.com/watch?v={video_id}"
        })

    # Highest TrendHub score first
    results.sort(
        key=lambda x: x["trend_score"],
        reverse=True
    )

    return results[:limit]
