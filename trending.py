from datetime import datetime, timezone

from youtube_service import (
    search_recent_videos,
    get_most_popular_videos,
    get_video_statistics
)


# ============================================================
# GET VIDEO ID SAFELY
# ============================================================

def get_video_id(video):

    if not isinstance(video, dict):
        return None

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

    except Exception:
        return 0


# ============================================================
# CALCULATE TRENDING SCORE
# ============================================================

def calculate_trending_score(
    views,
    likes,
    comments,
    hours_old
):

    hours_old = max(
        float(hours_old),
        0.5
    )

    views_per_hour = (
        views / hours_old
    )

    engagement = (
        likes +
        (comments * 2)
    )

    recency_factor = (
        1 /
        (1 + hours_old / 24)
    )

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


# ============================================================
# CHECK KEYWORD RELEVANCE
# ============================================================

def is_relevant_video(
    video,
    keywords
):

    if not isinstance(video, dict):
        return False

    snippet = video.get(
        "snippet",
        {}
    )

    if not isinstance(snippet, dict):
        return False

    title = str(
        snippet.get(
            "title",
            ""
        )
    ).lower()

    description = str(
        snippet.get(
            "description",
            ""
        )
    ).lower()

    channel = str(
        snippet.get(
            "channelTitle",
            ""
        )
    ).lower()

    text = (
        title
        + " "
        + description
        + " "
        + channel
    )

    # --------------------------------------------------------
    # At least one category keyword should appear
    # --------------------------------------------------------

    for keyword in keywords:

        if not keyword:
            continue

        keyword = str(
            keyword
        ).lower().strip()

        if keyword in text:

            return True

    return False


# ============================================================
# GET TRENDING VIDEOS
# ============================================================

def get_trending_videos(
    keywords,
    region_code="CA",
    hours=24,
    limit=5,
    category_id=None,
    use_popular=False
):

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if not isinstance(keywords, list):

        keywords = []

    keywords = [
        str(keyword).strip()
        for keyword in keywords
        if keyword
    ]

    if not keywords:

        return []

    if not region_code:

        region_code = "CA"

    # --------------------------------------------------------
    # Collect videos
    # --------------------------------------------------------

    all_videos = []

    # ========================================================
    # OPTION 1
    # GENERAL TRENDING
    #
    # Only the "Trending" category should use the country's
    # mostPopular chart.
    # ========================================================

    if use_popular:

        try:

            popular_videos = (
                get_most_popular_videos(

                    region_code=region_code,

                    max_results=50,

                    category_id=None
                )
            )

            if isinstance(
                popular_videos,
                list
            ):

                all_videos.extend(
                    popular_videos
                )

        except Exception:

            pass

    # ========================================================
    # OPTION 2
    # CATEGORY SEARCH
    #
    # Food / Dance / Health / Music / Art / Paintings /
    # Kids / News use category-specific searches.
    #
    # We DO NOT add general popular videos here.
    # ========================================================

    for keyword in keywords:

        try:

            recent_videos = (
                search_recent_videos(

                    query=keyword,

                    region_code=region_code,

                    hours=hours,

                    max_results=25,

                    category_id=category_id
                )
            )

            if isinstance(
                recent_videos,
                list
            ):

                all_videos.extend(
                    recent_videos
                )

        except Exception:

            continue

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_videos = {}

    for video in all_videos:

        if not isinstance(
            video,
            dict
        ):

            continue

        video_id = get_video_id(
            video
        )

        if not video_id:
            continue

        unique_videos[
            video_id
        ] = video

    videos = list(
        unique_videos.values()
    )

    if not videos:

        return []

    # ========================================================
    # FILTER CATEGORY RESULTS
    #
    # Do this only for category searches.
    #
    # This prevents unrelated videos from appearing simply
    # because YouTube returned them for a broad search.
    # ========================================================

    if not use_popular:

        filtered_videos = []

        for video in videos:

            if is_relevant_video(
                video,
                keywords
            ):

                filtered_videos.append(
                    video
                )

        videos = filtered_videos

    if not videos:

        return []

    # ========================================================
    # FILTER BY SELECTED TIME WINDOW
    # ========================================================

    now = datetime.now(
        timezone.utc
    )

    recent_videos = []

    for video in videos:

        snippet = video.get(
            "snippet",
            {}
        )

        if not isinstance(
            snippet,
            dict
        ):

            continue

        published_string = (
            snippet.get(
                "publishedAt"
            )
        )

        if not published_string:

            continue

        try:

            published_at = (
                datetime.fromisoformat(
                    published_string.replace(
                        "Z",
                        "+00:00"
                    )
                )
            )

        except Exception:

            continue

        age_hours = (
            now - published_at
        ).total_seconds() / 3600

        # ----------------------------------------------------
        # General Trending:
        # Keep popular videos even if older.
        #
        # Category searches:
        # Respect the selected time window strictly.
        # ----------------------------------------------------

        if not use_popular:

            if age_hours > hours:

                continue

        recent_videos.append(
            video
        )

    videos = recent_videos

    if not videos:

        return []

    # ========================================================
    # GET STATISTICS
    # ========================================================

    video_ids = []

    for video in videos:

        video_id = get_video_id(
            video
        )

        if video_id:

            video_ids.append(
                video_id
            )

    statistics = (
        get_video_statistics(
            video_ids
        )
    )

    if not isinstance(
        statistics,
        dict
    ):

        statistics = {}

    # ========================================================
    # CALCULATE SCORES
    # ========================================================

    results = []

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

        if not isinstance(
            snippet,
            dict
        ):

            continue

        published_string = (
            snippet.get(
                "publishedAt"
            )
        )

        if not published_string:

            continue

        try:

            published_at = (
                datetime.fromisoformat(
                    published_string.replace(
                        "Z",
                        "+00:00"
                    )
                )
            )

        except Exception:

            continue

        hours_old = (
            now - published_at
        ).total_seconds() / 3600

        hours_old = max(
            hours_old,
            0.5
        )

        stats = statistics.get(
            video_id,
            {}
        )

        if not isinstance(
            stats,
            dict
        ):

            stats = {}

        views = safe_int(
            stats.get(
                "viewCount",
                0
            )
        )

        likes = safe_int(
            stats.get(
                "likeCount",
                0
            )
        )

        comments = safe_int(
            stats.get(
                "commentCount",
                0
            )
        )

        views_per_hour = (
            views / hours_old
        )

        trend_score = (
            calculate_trending_score(

                views=views,

                likes=likes,

                comments=comments,

                hours_old=hours_old
            )
        )

        # ----------------------------------------------------
        # Category relevance bonus
        #
        # Videos matching multiple keywords receive a small
        # additional score.
        # ----------------------------------------------------

        title = str(
            snippet.get(
                "title",
                ""
            )
        ).lower()

        keyword_matches = 0

        for keyword in keywords:

            if str(
                keyword
            ).lower() in title:

                keyword_matches += 1

        relevance_bonus = (
            keyword_matches * 50000
        )

        final_score = (
            trend_score
            + relevance_bonus
        )

        # ----------------------------------------------------
        # Thumbnail
        # ----------------------------------------------------

        thumbnails = snippet.get(
            "thumbnails",
            {}
        )

        if not isinstance(
            thumbnails,
            dict
        ):

            thumbnails = {}

        high_thumbnail = (
            thumbnails.get(
                "high",
                {}
            )
        )

        if not isinstance(
            high_thumbnail,
            dict
        ):

            high_thumbnail = {}

        thumbnail = (
            high_thumbnail.get(
                "url",
                ""
            )
        )

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        results.append({

            "id":
                video_id,

            "title":
                snippet.get(
                    "title",
                    "Untitled"
                ),

            "channel":
                snippet.get(
                    "channelTitle",
                    "Unknown"
                ),

            "published":
                published_at,

            "hours_old":
                hours_old,

            "views":
                views,

            "likes":
                likes,

            "comments":
                comments,

            "views_per_hour":
                views_per_hour,

            "trend_score":
                final_score,

            "thumbnail":
                thumbnail,

            "url":
                f"https://www.youtube.com/watch?v={video_id}"
        })

    # ========================================================
    # SORT
    # ========================================================

    results.sort(
        key=lambda item:
            item.get(
                "trend_score",
                0
            ),
        reverse=True
    )

    return results[:limit]
