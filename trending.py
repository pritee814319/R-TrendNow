
from datetime import datetime, timezone

from youtube_service import (
    search_recent_videos,
    get_most_popular_videos,
    get_video_statistics,
)


# ============================================================
# VIDEO ID
# ============================================================

def get_video_id(video):

    video_id = video.get("id")

    # Search API format
    if isinstance(video_id, dict):

        return video_id.get("videoId")

    # Videos API format
    if isinstance(video_id, str):

        return video_id

    return None


# ============================================================
# SAFE INTEGER
# ============================================================

def safe_int(value):

    try:
        return int(value)
    except (
        TypeError,
        ValueError
    ):
        return 0


# ============================================================
# HOURS SINCE PUBLISHED
# ============================================================

def hours_since_published(video):

    try:

        published = video.get(
            "snippet",
            {}
        ).get(
            "publishedAt"
        )

        if not published:
            return 999999

        published_dt = datetime.fromisoformat(
            published.replace(
                "Z",
                "+00:00"
            )
        )

        now = datetime.now(
            timezone.utc
        )

        hours = (
            now - published_dt
        ).total_seconds() / 3600

        return max(
            hours,
            0.01
        )

    except Exception:

        return 999999


# ============================================================
# KEYWORD RELEVANCE
# ============================================================

def is_relevant_video(
    video,
    keywords
):

    if not keywords:
        return True

    snippet = video.get(
        "snippet",
        {}
    )

    title = snippet.get(
        "title",
        ""
    ).lower()

    description = snippet.get(
        "description",
        ""
    ).lower()

    channel = snippet.get(
        "channelTitle",
        ""
    ).lower()

    text = (
        title
        + " "
        + description
        + " "
        + channel
    )

    for keyword in keywords:

        if keyword.lower() in text:
            return True

    return False


# ============================================================
# TREND SCORE
# ============================================================

def calculate_trending_score(
    views,
    likes,
    comments,
    hours_old
):

    hours_old = max(
        hours_old,
        0.1
    )

    views_per_hour = (
        views / hours_old
    )

    like_rate = (
        likes / views
        if views > 0
        else 0
    )

    comment_rate = (
        comments / views
        if views > 0
        else 0
    )

    score = (

        views_per_hour * 0.60

        + views * 0.20

        + like_rate * 100000 * 0.10

        + comment_rate * 100000 * 0.10
    )

    return score


# ============================================================
# MAIN TRENDING FUNCTION
# ============================================================

def get_trending_videos(
    keywords,
    region_code="CA",
    hours=24,
    limit=5,
    category_id=None,
    use_popular=False
):

    videos = []

    # --------------------------------------------------------
    # GENERAL TRENDING
    # --------------------------------------------------------

    if use_popular:

        popular = get_most_popular_videos(
            region_code=region_code,
            max_results=50,
            category_id=category_id
        )

        videos.extend(
            popular
        )

    # --------------------------------------------------------
    # CATEGORY SEARCH
    # --------------------------------------------------------

    # Use only the first 3 keywords.
    # This keeps the app fast and reduces API quota usage.

    search_keywords = keywords[:3]

    for keyword in search_keywords:

        try:

            results = search_recent_videos(
                query=keyword,
                region_code=region_code,
                hours=hours,
                max_results=20,
                category_id=category_id
            )

            videos.extend(
                results
            )

        except Exception:
            continue

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_videos = {}

    for video in videos:

        video_id = get_video_id(
            video
        )

        if video_id:

            unique_videos[
                video_id
            ] = video

    videos = list(
        unique_videos.values()
    )

    # --------------------------------------------------------
    # FILTER BY TIME
    # --------------------------------------------------------

    filtered_videos = []

    for video in videos:

        age_hours = (
            hours_since_published(
                video
            )
        )

        if age_hours <= hours:

            filtered_videos.append(
                video
            )

    videos = filtered_videos

    # --------------------------------------------------------
    # CATEGORY RELEVANCE
    # --------------------------------------------------------

    if not use_popular:

        videos = [
            video
            for video in videos
            if is_relevant_video(
                video,
                keywords
            )
        ]

    # --------------------------------------------------------
    # GET STATISTICS
    # --------------------------------------------------------

    video_ids = [
        get_video_id(video)
        for video in videos
    ]

    video_ids = [
        video_id
        for video_id in video_ids
        if video_id
    ]

    statistics = get_video_statistics(
        video_ids
    )

    # --------------------------------------------------------
    # BUILD RESULTS
    # --------------------------------------------------------

    final_results = []

    for video in videos:

        video_id = get_video_id(
            video
        )

        if not video_id:
            continue

        snippet = video.get(
            "snippet",
            {}
        )

        stats = statistics.get(
            video_id,
            {}
        )

        views = safe_int(
            stats.get(
                "viewCount",
                video.get(
                    "statistics",
                    {}
                ).get(
                    "viewCount",
                    0
                )
            )
        )

        likes = safe_int(
            stats.get(
                "likeCount",
                video.get(
                    "statistics",
                    {}
                ).get(
                    "likeCount",
                    0
                )
            )
        )

        comments = safe_int(
            stats.get(
                "commentCount",
                video.get(
                    "statistics",
                    {}
                ).get(
                    "commentCount",
                    0
                )
            )
        )

        age_hours = hours_since_published(
            video
        )

        views_per_hour = (
            views / max(
                age_hours,
                0.1
            )
        )

        trend_score = calculate_trending_score(
            views=views,
            likes=likes,
            comments=comments,
            hours_old=age_hours
        )

        # Small relevance bonus
        if is_relevant_video(
            video,
            keywords
        ):
            trend_score *= 1.15

        final_results.append({

            "video_id": video_id,

            "title": snippet.get(
                "title",
                "Untitled"
            ),

            "description": snippet.get(
                "description",
                ""
            ),

            "channel": snippet.get(
                "channelTitle",
                "Unknown"
            ),

            "thumbnail": (
                snippet
                .get("thumbnails", {})
                .get("high", {})
                .get("url")
            ),

            "published_at": snippet.get(
                "publishedAt"
            ),

            "views": views,

            "likes": likes,

            "comments": comments,

            "hours_old": age_hours,

            "views_per_hour": views_per_hour,

            "trend_score": trend_score,

        })

    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

    final_results.sort(
        key=lambda x: x["trend_score"],
        reverse=True
    )

    return final_results[
        :limit
    ]
