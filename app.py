```python
import streamlit as st
import requests

st.set_page_config(
    page_title="TrendHub API Test",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 TrendHub")
st.success("Streamlit is working!")

# ------------------------------------------------------------
# GET API KEY
# ------------------------------------------------------------

try:
    API_KEY = st.secrets["YOUTUBE_API_KEY"]
    st.success("✅ YOUTUBE_API_KEY was found in Streamlit Secrets.")
except Exception as e:
    st.error("❌ YOUTUBE_API_KEY was NOT found.")
    st.code(str(e))
    st.stop()


# ------------------------------------------------------------
# TEST YOUTUBE API
# ------------------------------------------------------------

st.write("Testing YouTube API...")

url = "https://www.googleapis.com/youtube/v3/videos"

params = {
    "part": "snippet,statistics",
    "chart": "mostPopular",
    "regionCode": "CA",
    "maxResults": 5,
    "key": API_KEY,
}

try:

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    st.write("YouTube API HTTP status:", response.status_code)

    if response.status_code != 200:

        st.error("❌ YouTube API returned an error.")

        st.code(
            response.text,
            language="json"
        )

        st.stop()

    data = response.json()

    videos = data.get("items", [])

    st.success(
        f"✅ YouTube API is working! Found {len(videos)} videos."
    )

    # --------------------------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------------------------

    for video in videos:

        video_id = video.get("id")

        snippet = video.get(
            "snippet",
            {}
        )

        statistics = video.get(
            "statistics",
            {}
        )

        title = snippet.get(
            "title",
            "No title"
        )

        channel = snippet.get(
            "channelTitle",
            "Unknown channel"
        )

        views = statistics.get(
            "viewCount",
            "0"
        )

        st.subheader(title)

        st.write(
            f"📺 Channel: {channel}"
        )

        st.write(
            f"👁️ Views: {int(views):,}"
        )

        if video_id:

            st.video(
                f"https://www.youtube.com/watch?v={video_id}"
            )

        st.divider()


except Exception as e:

    st.error("❌ Something went wrong while connecting to YouTube.")

    st.exception(e)
```
