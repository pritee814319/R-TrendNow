
import streamlit as st

from categories import CATEGORIES
from trending import get_trending_videos


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TrendHub",
    page_icon="🔥",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("🔥 TrendHub")

st.markdown(
    "### Discover what is trending on YouTube right now"
)

st.caption(
    "TrendHub ranks recently published videos using "
    "views, engagement, recency and view velocity."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ TrendHub Settings")


# Location
region_options = {
    "🇨🇦 Canada": "CA",
    "🇺🇸 United States": "US",
    "🇮🇳 India": "IN",
    "🇬🇧 United Kingdom": "GB",
    "🇦🇺 Australia": "AU"
}

selected_region = st.sidebar.selectbox(
    "🌎 Location",
    list(region_options.keys())
)

region_code = region_options[selected_region]


# Time window
time_options = {
    "Last 6 hours": 6,
    "Last 12 hours": 12,
    "Last 24 hours": 24,
    "Last 48 hours": 48,
    "Last 7 days": 168
}

selected_time = st.sidebar.selectbox(
    "⏰ Search recent videos from",
    list(time_options.keys()),
    index=2
)

hours = time_options[selected_time]


# Category
selected_category = st.sidebar.selectbox(
    "📂 Category",
    list(CATEGORIES.keys())
)


# Number of videos
number_of_videos = st.sidebar.selectbox(
    "🏆 Number of videos",
    [5, 10],
    index=0
)


# Refresh
refresh_clicked = st.sidebar.button(
    "🔄 Refresh Trending",
    use_container_width=True
)


if refresh_clicked:
    st.cache_data.clear()
    st.rerun()


# ============================================================
# CATEGORY
# ============================================================

category_data = CATEGORIES[selected_category]

keywords = category_data.get("keywords", [])

category_id = category_data.get("category_id")


# ============================================================
# MAIN INFORMATION
# ============================================================

st.markdown("---")

st.subheader(
    f"{selected_category} — Trending Now"
)

st.write(
    f"📍 Location: **{selected_region}**"
)

st.write(
    f"⏰ Time window: **{selected_time}**"
)

st.write(
    "🔥 Videos are ranked by the TrendHub algorithm, "
    "not simply by lifetime view count."
)


# ============================================================
# LOAD VIDEOS
# ============================================================

try:

    with st.spinner(
        "🔎 Searching YouTube for recent videos..."
    ):

        videos = get_trending_videos(
            keywords=keywords,
            region_code=region_code,
            hours=hours,
            limit=number_of_videos,
            category_id=category_id
        )


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not videos:

        st.warning(
            "⚠️ No recent videos were found."
        )

        st.info(
            "Try increasing the time window "
            "to 48 hours or 7 days."
        )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    else:

        st.success(
            f"🔥 Found {len(videos)} trending videos"
        )


        for index, video in enumerate(
            videos,
            start=1
        ):

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            st.markdown(
                f"## #{index} {video['title']}"
            )


            col1, col2 = st.columns(
                [1, 2]
            )


            # ------------------------------------------------
            # THUMBNAIL
            # ------------------------------------------------

            with col1:

                if video.get("thumbnail"):

                    st.image(
                        video["thumbnail"],
                        use_container_width=True
                    )


            # ------------------------------------------------
            # VIDEO INFORMATION
            # ------------------------------------------------

            with col2:

                st.markdown(
                    f"**📺 Channel:** "
                    f"{video['channel']}"
                )


                st.markdown(
                    f"👀 **Views:** "
                    f"{video['views']:,}"
                )


                st.markdown(
                    f"🚀 **Views per hour:** "
                    f"{video['views_per_hour']:,.0f}"
                )


                st.markdown(
                    f"👍 **Likes:** "
                    f"{video['likes']:,}"
                )


                st.markdown(
                    f"💬 **Comments:** "
                    f"{video['comments']:,}"
                )


                st.markdown(
                    f"⏱️ **Published:** "
                    f"{video['hours_old']:.1f} hours ago"
                )


                st.metric(
                    label="🔥 TrendHub Score",
                    value=f"{video['trend_score']:,.0f}"
                )


                st.link_button(
                    "▶️ Watch on YouTube",
                    video["url"]
                )


            st.divider()


# ============================================================
# ERROR HANDLING
# ============================================================

except Exception as e:

    st.error(
        "❌ Unable to load YouTube data."
    )

    st.markdown(
        "### 🔧 Error Details"
    )

    st.code(
        str(e),
        language="text"
    )

    st.markdown(
        "### ✅ Please check:"
    )

    st.write(
        "1. **YouTube Data API** is enabled "
        "in your Google Cloud project."
    )

    st.write(
        "2. Your Streamlit Secret is named exactly:"
    )

    st.code(
        "YOUTUBE_API_KEY"
    )

    st.write(
        "3. Your API key is inside quotation marks "
        "in Streamlit Secrets."
    )

    st.write(
        "4. The API key belongs to the same "
        "Google Cloud project where YouTube Data API "
        "is enabled."
    )

    st.write(
        "5. If you restricted the API key, make sure "
        "**YouTube Data API** is allowed."
    )

    st.markdown("---")

    st.warning(
        "If the error above says **403**, **400**, "
        "**quotaExceeded**, **API_KEY_INVALID**, or "
        "something else, send me that exact error. "
        "We can then fix the specific problem."
    )
```

