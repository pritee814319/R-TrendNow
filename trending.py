import math

from datetime import datetime, timezone

from youtube_service import (
    search_recent_videos,
    get_most_popular_videos,
    get_video_statistics
)


# --------------------------------------------------
# GET VIDEO ID
# --------------------------------------------------

def get_video_id(video):

    video_id = video.get("id")

    if isinstance(video_id, dict):

        return video_id.get("videoId")

    if isinstance(video_id, str):

        return video_id

    return None


# --------------------------------------------------
# SAFE INTEGER
# --------------------------------------------------

def safe_int(value, default=0):

    try:

        return int(value)

    except (TypeError, ValueError):

        return default


# --------------------------------------------------
# HOURS SINCE PUBLISHED
# --------------------------------------------------

def hours_since_published(published_at):

    try:

        published = datetime.fromisoformat(
            published_at.replace(
                "Z",
                "+00:00"
            )
        )

        now = datetime.now(
            timezone.utc
        )

        seconds = (
            now - published
        ).total_seconds()

        hours = seconds / 3600

        return max(
            hours,
            0.01
        )

    except Exception:

        return 999999


# --------------------------------------------------
# CHECK IF VIDEO IS RECENT
# --------------------------------------------------

def is_recent(video, hours):

    snippet = video.get(
        "snippet",
        {}
    )

    published_at = snippet.get(
        "publishedAt"
    )

    if not published_at:

        return False

    age_hours = hours_since_published(
        published_at
    )

    return age_hours <= hours


# --------------------------------------------------
# TRENDING SCORE
# --------------------------------------------------

def calculate_trending_score(
    views,
    likes,
    comments,
    age_hours
):

    age_hours = max(
        age_hours,
        0.1
    )

    views_per_hour = (
        views / age_hours
    )

    engagement = (
        likes + comments
    )

    score = (

        math.log10(
            views + 1
        ) * 20

        +

        math.log10(
            views_per_hour + 1
        ) * 35

        +

        math.log10(
            engagement + 1
        ) * 10
    )

    return round(
        score,
        2
    )


# --------------------------------------------------
# MAIN TRENDING FUNCTION
# --------------------------------------------------

def get_trending_videos(
    keywords,
    region_code="CA",
    hours=24,
    limit=5,
    category_id=None
):

    videos = []


    # ==================================================
    # GENERAL TRENDING
    # ==================================================

    if category_id is None:

        try:

            popular_videos = (
                get_most_popular_videos(
                    region_code=region_code,
                    max_results=50
                )
            )

            for video in popular_videos:

                if is_recent(
                    video,
                    hours
                ):

                    videos.append(
                        video
                    )

        except Exception:

            pass


        # --------------------------------------------------
        # SEARCH RECENT TRENDING TERMS
        # --------------------------------------------------

        for keyword in keywords[:3]:

            try:

                search_results = (
                    search_recent_videos(
                        query=keyword,
                        region_code=region_code,
                        hours=hours,
                        max_results=25
                    )
                )

                videos.extend(
                    search_results
                )

            except Exception:

                continue


    # ==================================================
    # CATEGORY TRENDING
    # ==================================================

    else:

        for keyword in keywords[:3]:

            try:

                search_results = (
                    search_recent_videos(
                        query=keyword,
                        region_code=region_code,
                        hours=hours,
                        max_results=25,
                        category_id=category_id
                    )
                )

                videos.extend(
                    search_results
                )

            except Exception:

                continue


    # ==================================================
    # REMOVE DUPLICATES
    # ==================================================

    unique_videos = {}


    for video in videos:

        video_id = get_video_id(
            video
        )

        if not video_id:

            continue

        if not is_recent(
            video,
            hours
        ):

            continue

        unique_videos[
            video_id
        ] = video


    if not unique_videos:

        return []


    # ==================================================
    # GET VIDEO STATISTICS
    # ==================================================

    video_ids = list(
        unique_videos.keys()
    )


    statistics = (
        get_video_statistics(
            video_ids
        )
    )


    # ==================================================
    # BUILD RESULTS
    # ==================================================

    results = []


    for video_id, video in unique_videos.items():

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


        published_at = snippet.get(
            "publishedAt"
        )


        age_hours = (
            hours_since_published(
                published_at
            )
        )


        views_per_hour = (
            views /
            max(
                age_hours,
                0.1
            )
        )


        trend_score = (
            calculate_trending_score(
                views=views,
                likes=likes,
                comments=comments,
                age_hours=age_hours
            )
        )


        thumbnails = snippet.get(
            "thumbnails",
            {}
        )


        thumbnail = None


        if thumbnails.get("high"):

            thumbnail = (
                thumbnails["high"].get(
                    "url"
                )
            )

        elif thumbnails.get("medium"):

            thumbnail = (
                thumbnails["medium"].get(
                    "url"
                )
            )

        elif thumbnails.get("default"):

            thumbnail = (
                thumbnails["default"].get(
                    "url"
                )
            )


        result = {

            "id": video_id,

            "title": snippet.get(
                "title",
                "Untitled"
            ),

            "channel": snippet.get(
                "channelTitle",
                "Unknown"
            ),

            "thumbnail": thumbnail,

            "published_at": published_at,

            "views": views,

            "likes": likes,

            "comments": comments,

            "age_hours": round(
                age_hours,
                1
            ),

            "views_per_hour": round(
                views_per_hour,
                0
            ),

            "trend_score": trend_score
        }


        results.append(
            result
        )


    # ==================================================
    # SORT RESULTS
    # ==================================================

    results.sort(
        key=lambda video:
            video.get(
                "trend_score",
                0
            ),
        reverse=True
    )


    # ==================================================
    # RETURN TOP VIDEOS
    # ==================================================

    return results[:limit]
