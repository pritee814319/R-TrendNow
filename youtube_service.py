import requests
import streamlit as st
from datetime import datetime, timedelta, timezone


BASE_URL = "https://www.googleapis.com/youtube/v3"


def get_api_key():
    return st.secrets["YOUTUBE_API_KEY"]


def search_recent_videos(
    query,
    region_code="CA",
    hours=24,
    max_results=25,
    category_id=None
):
    """
    Search YouTube for videos published recently.
    """

    api_key = get_api_key()

    published_after = (
        datetime.now(timezone.utc)
        - timedelta(hours=hours)
    ).isoformat()

    url = f"{BASE_URL}/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "date",
        "publishedAfter": published_after,
        "regionCode": region_code,
        "maxResults": max_results,
        "safeSearch": "moderate",
        "key": api_key,
    }

    if category_id:
        params["videoCategoryId"] = category_id

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

    return response.json().get("items", [])


def get_video_statistics(video_ids):
    """
    Get current statistics for videos.
    """

    if not video_ids:
        return {}

    api_key = get_api_key()

    url = f"{BASE_URL}/videos"

    params = {
        "part": "statistics,contentDetails",
        "id": ",".join(video_ids),
        "key": api_key,
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(
            f"YouTube statistics error: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    data = response.json()

    statistics = {}

    for item in data.get("items", []):

        statistics[item["id"]] = {
            "viewCount": int(
                item.get("statistics", {}).get(
                    "viewCount", 0
                )
            ),

            "likeCount": int(
                item.get("statistics", {}).get(
                    "likeCount", 0
                )
            ),

            "commentCount": int(
                item.get("statistics", {}).get(
                    "commentCount", 0
                )
            )
        }

    return statistics
