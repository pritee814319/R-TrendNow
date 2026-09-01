import math

from datetime import datetime, timezone

from youtube_service import (
    search_recent_videos,
    get_most_popular_videos,
    get_video_statistics
)


# ==================================================
# GET VIDEO ID
# ==================================================

def get_video_id(video):

    video_id = video.get("id")

    if isinstance(video_id, dict):
        return video_id.get("videoId")

    if isinstance(video_id, str):
        return video_id

    return None


# ==================================================
# SAFE INTEGER
# ==================================================

def safe_int(value, default=0):

    try:
        return int(value)

    except (TypeError, ValueError):

        return default


# ==================================================
# HOURS SINCE PUBLISHED
# ==================================================

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


# ==================================================
# CHECK RECENT
# ==================================================

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


# ==================================================
# CATEGORY RELEVANCE
# ==================================================

def calculate_relevance(
    video,
    keywords
):

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

    text = f"{title} {description}"

    score = 0

    for keyword in keywords:

        keyword_lower = keyword.lower()

        # Strong match in title
        if keyword_lower in title:

            score += 5

        # Match in description
        elif keyword_lower in description:

            score += 2

    return score


# ==================================================
# TRENDING SCORE
# ==================================================

def calculate_trending_score(
    views,
    likes,
    comments,
    age_hours,
    relevance_score=0
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

        +

        relevance_score * 3
    )

    return round(
        score,
        2
    )


# ==================================================
# MAIN FUNCTION
# ==================================================

def get_trending_videos(
    keywords,
    region_code="CA",
    hours=24,
    limit=5,
    category_id=None,
    mode="trending"
):

    videos = []


    # ==================================================
    # MODE 1: GENERAL TRENDING
    # ==================================================

    if mode == "trending":

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

        except Exception as e:

            print(
                f"Trending API error: {e}"
            )


    # ==================================================
    # MODE 2: OFFICIAL YOUTUBE CATEGORY
    # ==================================================

    elif mode == "official":

        try:

            popular_videos = (
                get_most_popular_videos(
                    region_code=region_code,
                    max_results=50,
                    category_id=category_id
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

        except Exception as e:

            print(
                f"Official category API error: {e}"
            )


        # --------------------------------------------------
        # FALLBACK SEARCH
        # --------------------------------------------------

        if len(videos) < limit:

            try:

                query = "|".join(
                    keywords
                )

                search_results = (
                    search_recent_videos(
                        query=query,
                        region_code=region_code,
                        hours=hours,
                        max_results=50,
                        category_id=category_id
                    )
                )

                videos.extend(
                    search_results
                )

            except Exception as e:

                print(
                    f"Category search error: {e}"
                )


    # ==================================================
    # MODE 3: CUSTOM CATEGORY SEARCH
    # ==================================================

    elif mode == "search":

        try:

            # YouTube supports OR searches
            query = "|".join(
                keywords
            )

            search_results = (
                search_recent_videos(
                    query=query,
                    region_code=region_code,
                    hours=hours,
                    max_results=50
                )
            )

            videos.extend(
                search_results
            )

        except Exception as e:

            print(
                f"Custom category search error: {e}"
            )


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
    # GET STATISTICS
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


        # --------------------------------------------------
        # RELEVANCE
        # --------------------------------------------------

        relevance_score = 0

        if mode == "search":

            relevance_score = (
                calculate_relevance(
                    video,
                    keywords
                )
            )


            # Reject completely unrelated results

            if relevance_score == 0:

                continue


        # --------------------------------------------------
        # TREND SCORE
        # --------------------------------------------------

        trend_score = (
            calculate_trending_score(
                views=views,
                likes=likes,
                comments=comments,
                age_hours=age_hours,
                relevance_score=relevance_score
            )
        )


        # --------------------------------------------------
        # THUMBNAIL
        # --------------------------------------------------

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


        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

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

            "relevance_score": relevance_score,

            "trend_score": trend_score
        }


        results.append(
            result
        )


    # ==================================================
    # SORT
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
    # RETURN TOP RESULTS
    # ==================================================

    return results[:limit]
