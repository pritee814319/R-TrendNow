import requests
import streamlit as st

from datetime import datetime, timedelta, timezone


BASE_URL = "https://www.googleapis.com/youtube/v3"


# --------------------------------------------------
# GET API KEY
# --------------------------------------------------

def get_api_key():

    return st.secrets["YOUTUBE_API_KEY"]


# --------------------------------------------------
# YOUTUBE API REQUEST
# --------------------------------------------------

def youtube_request(endpoint, params):

    params = dict(params)

    params["key"] = get_api_key()

    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:

        raise Exception(
            f"YouTube API error: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    return response.json()


# --------------------------------------------------
# SEARCH RECENT VIDEOS
# --------------------------------------------------

def search_recent_videos(
    query,
    region_code="CA",
    hours=24,
    max_results=25,
    category_id=None
):

    published_after = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    ).isoformat()


    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "date",
        "publishedAfter": published_after,
        "regionCode": region_code,
        "maxResults": max_results,
        "safeSearch": "moderate"
    }


    if category_id:

        params["videoCategoryId"] = category_id


    data = youtube_request(
        "search",
        params
    )


    return data.get(
        "items",
        []
    )


# --------------------------------------------------
# MOST POPULAR VIDEOS
# --------------------------------------------------

def get_most_popular_videos(
    region_code="CA",
    max_results=25,
    category_id=None
):

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region_code,
        "maxResults": max_results
    }


    if category_id:

        params["videoCategoryId"] = category_id


    data = youtube_request(
        "videos",
        params
    )


    return data.get(
        "items",
        []
    )


# --------------------------------------------------
# SAFE INTEGER
# --------------------------------------------------

def safe_int(
    value,
    default=0
):

    try:

        return int(value)

    except (
        TypeError,
        ValueError
    ):

        return default


# --------------------------------------------------
# GET VIDEO STATISTICS
# --------------------------------------------------

def get_video_statistics(
    video_ids
):

    if not video_ids:

        return {}


    statistics = {}


    # YouTube allows a maximum of 50 IDs
    # in one videos.list request.

    for start in range(
        0,
        len(video_ids),
        50
    ):

        batch = video_ids[
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


        for item in data.get(
            "items",
            []
        ):

            video_id = item.get(
                "id"
            )


            stats = item.get(
                "statistics",
                {}
            )


            statistics[video_id] = {

                "viewCount": safe_int(
                    stats.get(
                        "viewCount",
                        0
                    )
                ),

                "likeCount": safe_int(
                    stats.get(
                        "likeCount",
                        0
                    )
                ),

                "commentCount": safe_int(
                    stats.get(
                        "commentCount",
                        0
                    )
                )
            }


    return statistics
