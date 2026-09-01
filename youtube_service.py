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
    Search YouTube for recently published videos.
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
            f"YouTube search error: "
            f"{response.status_code} - "
            f"{response.text}"
        )

    return response.json().get("items", [])


def get_video_statistics(video_ids):
    """
    Get current statistics for YouTube videos.

    YouTube allows a maximum of 50 video IDs
    in one videos.list request, so we process
    the IDs in batches of 50.
    """

    if not video_ids:
        return {}

    api_key = get_api_key()

    statistics = {}

    # --------------------------------------------------------
    # PROCESS VIDEO IDS IN BATCHES OF 50
    # --------------------------------------------------------

    for start in range(
        0,
        len(video_ids),
        50
    ):

        batch = video_ids[
            start:start + 50
        ]

        url = f"{BASE_URL}/videos"

        params = {
            "part": "statistics,contentDetails",
            "id": ",".join(batch),
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
                "viewCount": int(
                    stats.get(
                        "viewCount",
                        0
                    )
                ),

                "likeCount": int(
                    stats.get(
                        "likeCount",
                        0
                    )
                ),

                "commentCount": int(
                    stats.get(
                        "commentCount",
                        0
                    )
                )
            }

    return statistics
