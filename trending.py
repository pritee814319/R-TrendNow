from datetime import datetime, timezone

from youtube_service import (
    search_recent_videos,
    get_most_popular_videos,
    get_video_statistics
)


# ============================================================
# TRENDING SCORE
# ============================================================

def calculate_trending_score(
    views,
    likes,
    comments,
    hours_old
):

    hours_old = max(
        hours_old,
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
    # 1. COUNTRY'S MOST POPULAR VIDEOS
    # ========================================================

    popular_videos = get_most_popular_videos(

        region_code=region_code,

        max_results=50,

        category_id=category_id
    )

    all_videos.extend(
        popular_videos
    )


    # ========================================================
    # 2. RECENT VIDEOS
    # ========================================================

    for keyword in keywords:

        recent_videos = search_recent_videos(

            query=keyword,

            region_code=region_code,

            hours=hours,

            max_results=25,

            category_id=category_id
        )

        all_videos.extend(
            recent_videos
        )


    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    unique_videos = {}

    for video in all_videos:

        video_id = (
            video
            .get("id", {})
            .get("videoId")
        )

        # videos.list returns id as a string
        if not video_id:

            video_id = video.get(
                "id"
            )

        if video_id:

            unique_videos[
                video_id
            ] = video


    videos = list(
        unique_videos.values()
    )


    if not videos:

        return []


    # ========================================================
    # GET STATISTICS
    # ========================================================

    video_ids = list(
        unique_videos.keys()
    )

    statistics = get_video_statistics(
        video_ids
    )


    # ========================================================
    # CALCULATE SCORES
    # ========================================================

    results = []

    now = datetime.now(
        timezone.utc
    )


    for video in videos:

        video_id = (
            video
            .get("id", {})
            .get("videoId")
        )

        if not video_id:

            video_id = video.get(
                "id"
            )


        snippet = video.get(
            "snippet",
            {}
        )


        stats = statistics.get(
            video_id,
            {}
        )


        published_string = (
            snippet.get(
                "publishedAt"
            )
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


        hours_old = max(
            hours_old,
            0.5
        )


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


        views_per_hour = (
            views /
            hours_old
        )


        score = calculate_trending_score(

            views=views,

            likes=likes,

            comments=comments,

            hours_old=hours_old
        )


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

                snippet
                .get(
                    "thumbnails",
                    {}
                )
                .get(
                    "high",
                    {}
                )
                .get(
                    "url",
                    ""
                ),


            "url":

                f"https://www.youtube.com/watch?v={video_id}"
        })


    # ========================================================
    # SORT
    # ========================================================

    results.sort(

        key=lambda x:
            x["trend_score"],

        reverse=True
    )


    return results[:limit]
