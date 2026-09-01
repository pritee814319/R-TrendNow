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

    # Search API:
    # "id": {"kind": "youtube#video", "videoId": "..."}
    if isinstance(video_id, dict):

        return video_id.get("videoId")

    # Videos API:
    # "id": "..."
    if isinstance(video_id, str):

        return video_id

    return None


# ============================================================
# TRENDING SCORE
# ============================================================

def calculate_trending_score(
    views,
    likes,
    comments,
    hours_old
):

    views = max(
        int(views or 0),
        0
    )

    likes = max(
        int(likes or 0),
        0
    )

    comments = max(
        int(comments or 0),
        0
    )

    hours_old = max(
        float(hours_old or 0),
        0.5
    )


    # --------------------------------------------------------
    # VIEW VELOCITY
    # --------------------------------------------------------

    views_per_hour = (
        views / hours_old
    )


    # --------------------------------------------------------
    # ENGAGEMENT
    # --------------------------------------------------------

    engagement = (
        likes +
        (comments * 2)
    )


    # --------------------------------------------------------
    # RECENCY
    # --------------------------------------------------------

    recency_factor = (
        1 /
        (1 + hours_old / 24)
    )


    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

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
# GET TRENDING VIDEOS
# ============================================================

def get_trending_videos(
    keywords,
    region_code="CA",
    hours=24,
    limit=5,
    category_id=None
):

    all_videos = []


    # ========================================================
    # VALIDATE REGION
    # ========================================================

    if not region_code:

        region_code = "CA"

    region_code = str(
        region_code
    ).upper()


    # ========================================================
    # VALIDATE KEYWORDS
    # ========================================================

    if not isinstance(
        keywords,
        list
    ):

        keywords = []


    # ========================================================
    # 1. COUNTRY POPULAR VIDEOS
    # ========================================================

    try:

        popular_videos = get_most_popular_videos(

            region_code=region_code,

            max_results=50,

            category_id=category_id

        )

        if isinstance(
            popular_videos,
            list
        ):

            all_videos.extend(
                popular_videos
            )

    except Exception:

        # Continue with recent-video search.
        pass


    # ========================================================
    # 2. RECENT VIDEOS
    # ========================================================

    for keyword in keywords:

        if not isinstance(
            keyword,
            str
        ):

            continue

        keyword = keyword.strip()

        if not keyword:

            continue


        try:

            recent_videos = search_recent_videos(

                query=keyword,

                region_code=region_code,

                hours=hours,

                max_results=25,

                category_id=category_id

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
    # 3. REMOVE DUPLICATES
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
    # 4. GET STATISTICS
    # ========================================================

    video_ids = list(
        unique_videos.keys()
    )


    statistics = get_video_statistics(
        video_ids
    )


    if not isinstance(
        statistics,
        dict
    ):

        statistics = {}


    # ========================================================
    # 5. CALCULATE TREND SCORE
    # ========================================================

    results = []


    now = datetime.now(
        timezone.utc
    )


    for video in videos:

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


        # ----------------------------------------------------
        # SNIPPET
        # ----------------------------------------------------

        snippet = video.get(
            "snippet",
            {}
        )


        if not isinstance(
            snippet,
            dict
        ):

            continue


        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        stats = statistics.get(
            video_id,
            {}
        )


        if not isinstance(
            stats,
            dict
        ):

            stats = {}


        # ----------------------------------------------------
        # PUBLISHED DATE
        # ----------------------------------------------------

        published_string = snippet.get(
            "publishedAt"
        )


        if not published_string:

            continue


        try:

            published_at = datetime.fromisoformat(

                published_string.replace(
                    "Z",
                    "+00:00"
                )

            )

        except (
            ValueError,
            TypeError
        ):

            continue


        # ----------------------------------------------------
        # AGE
        # ----------------------------------------------------

        hours_old = (

            now - published_at

        ).total_seconds() / 3600


        hours_old = max(
            hours_old,
            0.5
        )


        # ----------------------------------------------------
        # IMPORTANT:
        # REMOVE VIDEOS OLDER THAN SELECTED WINDOW
        # ----------------------------------------------------

        # Popular videos can be much older than the selected
        # time window. Do not let them dominate recent results.

        if hours_old > hours:

            continue


        # ----------------------------------------------------
        # STATISTICS VALUES
        # ----------------------------------------------------

        try:

            views = int(
                stats.get(
                    "viewCount",
                    0
                ) or 0
            )

        except (
            ValueError,
            TypeError
        ):

            views = 0


        try:

            likes = int(
                stats.get(
                    "likeCount",
                    0
                ) or 0
            )

        except (
            ValueError,
            TypeError
        ):

            likes = 0


        try:

            comments = int(
                stats.get(
                    "commentCount",
                    0
                ) or 0
            )

        except (
            ValueError,
            TypeError
        ):

            comments = 0


        # ----------------------------------------------------
        # VIEW VELOCITY
        # ----------------------------------------------------

        views_per_hour = (

            views /
            hours_old

        )


        # ----------------------------------------------------
        # TREND SCORE
        # ----------------------------------------------------

        score = calculate_trending_score(

            views=views,

            likes=likes,

            comments=comments,

            hours_old=hours_old

        )


        # ----------------------------------------------------
        # THUMBNAIL
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


        high_thumbnail = thumbnails.get(
            "high",
            {}
        )


        if not isinstance(
            high_thumbnail,
            dict
        ):

            high_thumbnail = {}


        thumbnail_url = high_thumbnail.get(
            "url",
            ""
        )


        # ----------------------------------------------------
        # RESULT
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
                score,

            "thumbnail":
                thumbnail_url,

            "url":
                f"https://www.youtube.com/watch?v={video_id}"

        })


    # ========================================================
    # 6. SORT
    # ========================================================

    results.sort(

        key=lambda video:
            video.get(
                "trend_score",
                0
            ),

        reverse=True

    )


    # ========================================================
    # 7. RETURN TOP RESULTS
    # ========================================================

    return results[:limit]
