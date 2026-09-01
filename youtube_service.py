
import requests
import streamlit as st


BASE_URL = "https://www.googleapis.com/youtube/v3"


def get_api_key():
    return st.secrets["YOUTUBE_API_KEY"]


def search_videos(query, max_results=10):
    api_key = get_api_key()

    url = f"{BASE_URL}/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "order": "viewCount",
        "maxResults": max_results,
        "key": api_key,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json().get("items", [])


def get_video_statistics(video_ids):
    if not video_ids:
        return {}

    api_key = get_api_key()

    url = f"{BASE_URL}/videos"

    params = {
        "part": "statistics",
        "id": ",".join(video_ids),
        "key": api_key,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    statistics = {}

    for item in data.get("items", []):
        statistics[item["id"]] = item.get("statistics", {})

    return statistics
