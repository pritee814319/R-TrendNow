import requests
import streamlit as st

from datetime import datetime, timedelta, timezone


BASE_URL = "https://www.googleapis.com/youtube/v3"


# ============================================================
# API KEY
# ============================================================

def get_api_key():

    try:
        return st.secrets["YOUTUBE_API_KEY"]

    except Exception:
        raise Exception(
            "YOUTUBE_API_KEY is missing from Streamlit Secrets."
        )


# ============================================================
# SAFE API REQUEST
# ============================================================

def youtube_request(endpoint, params):

    api_key = get_api_key()

    params = dict(params)

    params["key"] = api_key

    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:

        try:
            error_data = response.json()

            message = (
                error_data
                .get("error", {})
                .get("message", response.text)
            )

        except Exception:

            message = response.text

        raise Exception(
            f"YouTube API error "
            f"{response.status_code}: {message}"
        )

    try:

        return response.json()

    except Exception:

        raise Exception(
            "YouTube returned an invalid response."
        )


# ============================================================
# SEARCH RECENT VIDEOS
# ============================================================

def search_recent_videos(
    query,
    region_code="CA",
    hours=24,
    max_results=25,
    category_id=None
):

    if not query:

        return []

    # --------------------------------------------------------
    # Calculate date/time
    # --------------------------------------------------------

    published_after = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    ).isoformat()

    # --------------------------------------------------------
    # Search parameters
    # --------------------------------------------------------

    params = {

        "part": "snippet",

        "q": str(query),

        "type": "video",

        "order": "date",

        "publishedAfter": published_after,

        "regionCode": region_code,

        "maxResults": min(
            int(max_results),
            50
        ),

        "safeSearch": "moderate"
    }

    # --------------------------------------------------------
    # Category filter
    #
    # IMPORTANT:
    # videoCategoryId is valid only for video searches.
    # We already specify type=video.
    # --------------------------------------------------------

    if category_id:

        params["videoCategoryId"] = str(
            category_id
        )

    data = youtube_request(
        "search",
        params
    )

    items = data.get(
        "items",
        []
    )

    if not isinstance(items, list):

        return []

    # --------------------------------------------------------
    # Keep only proper dictionaries
    # --------------------------------------------------------

    videos = []

    for item in items:

        if not isinstance(item, dict):

            continue

        video_id = item.get(
            "id",
            {}
        )

        # Search API normally returns:
        #
        # "id": {
        #     "kind": "youtube#video",
        #     "videoId": "xxxxx"
        # }

        if not isinstance(video_id, dict):

            continue

        if not video_id.get("videoId"):

            continue

        videos.append(item)

    return videos


# ============================================================
# GET COUNTRY'S MOST POPULAR VIDEOS
# ============================================================

def get_most_popular_videos(
    region_code="CA",
    max_results=25,
    category_id=None
):

    params = {

        "part": "snippet,statistics",

        "chart": "mostPopular",

        "regionCode": region_code,

        "maxResults": min(
            int(max_results),
            50
        )
    }

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    if category_id:

        params["videoCategoryId"] = str(
            category_id
        )

    data = youtube_request(
        "videos",
        params
    )

    items = data.get(
        "items",
        []
    )

    if not isinstance(items, list):

        return []

    videos = []

    for item in items:

        if not isinstance(item, dict):

            continue

        if not item.get("id"):

            continue

        videos.append(item)

    return videos


# ============================================================
# GET VIDEO STATISTICS
# ============================================================

def get_video_statistics(video_ids):

    if not video_ids:

        return {}

    # --------------------------------------------------------
    # Remove invalid IDs
    # --------------------------------------------------------

    clean_ids = []

    for video_id in video_ids:

        if isinstance(video_id, str):

            video_id = video_id.strip()

            if video_id:

                clean_ids.append(video_id)

    if not clean_ids:

        return {}

    statistics = {}

    # --------------------------------------------------------
    # YouTube allows maximum 50 IDs
    # per videos.list request
    # --------------------------------------------------------

    for start in range(
        0,
        len(clean_ids),
        50
    ):

        batch = clean_ids[
            start:start + 50
        ]

        params = {

            "part": "statistics",

            "id": ",".join(batch)
        }

        data = youtube_request(
            "videos",
            params
        )

        items = data.get(
            "items",
            []
        )

        if not isinstance(items, list):

            continue

        for item in items:

            if not isinstance(item, dict):

                continue

            video_id = item.get("id")

            if not video_id:

                continue

            stats = item.get(
                "statistics",
                {}
            )

            if not isinstance(stats, dict):

                stats = {}

            # ------------------------------------------------
            # Some videos may not expose likes/comments.
            # ------------------------------------------------

            try:

                views = int(
                    stats.get(
                        "viewCount",
                        0
                    )
                )

            except Exception:

                views = 0

            try:

                likes = int(
                    stats.get(
                        "likeCount",
                        0
                    )
                )

            except Exception:

                likes = 0

            try:

                comments = int(
                    stats.get(
                        "commentCount",
                        0
                    )
                )

            except Exception:

                comments = 0

            statistics[video_id] = {

                "viewCount": views,

                "likeCount": likes,

                "commentCount": comments
            }

    return statistics
