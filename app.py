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
    "TrendHub ranks recent videos using views, engagement, "
    "recency and view velocity."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ TrendHub Settings")


# ============================================================
# LOCATION
# ============================================================

region_options = {
    "United States": "US",
    "Canada": "CA",
    "United Kingdom": "GB",
    "India": "IN",
    "Australia": "AU",
    "New Zealand": "NZ",
    "Germany": "DE",
    "France": "FR",
    "Italy": "IT",
    "Spain": "ES",
    "Brazil": "BR",
    "Mexico": "MX",
    "Japan": "JP",
    "South Korea": "KR",
    "China": "CN",
    "Singapore": "SG",
    "United Arab Emirates": "AE",
    "Saudi Arabia": "SA",
    "South Africa": "ZA",
}

selected_region = st.sidebar.selectbox(
    "🌎 Location",
    list(region_options.keys())
)

region_code = region_options[selected_region]


# ============================================================
# TIME WINDOW
# ============================================================

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


# ============================================================
# CATEGORY
# ============================================================

selected_category = st.sidebar.selectbox(
    "📂 Category",
    list(CATEGORIES.keys())
)


# ============================================================
# NUMBER OF VIDEOS
# ============================================================

number_of_videos = st.sidebar.selectbox(
    "🏆 Number of videos",
    [5, 10],
    index=0
)


# ============================================================
# REFRESH
# ============================================================

refresh_clicked = st.sidebar.button(
    "🔄 Refresh Trending",
    width="stretch"
)

if refresh_clicked:
    st.cache_data.clear()
    st.rerun()


# ============================================================
# CATEGORY DATA
# ============================================================

category_data = CATEGORIES.get(
    selected_category,
    {}
)

if not isinstance(category_data, dict):
    st.error(
        f"Invalid category configuration for "
        f"'{selected_category}'."
    )
    st.stop()


keywords = category_data.get(
    "keywords",
    []
)

category_id = category_data.get(
    "category_id"
)


# ============================================================
# MAIN INFORMATION
# ============================================================

st.markdown("---")

st.subheader(
    f"{selected_category} — Trending Now"
)

st.write(
    f"📍 Location: **{selected_region} ({region_code})**"
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
        f"🔎 Searching YouTube for "
        f"{selected_category} in {selected_region}..."
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
            "Try increasing the time window to "
            "48 hours or 7 days."
        )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    else:

        st.success(
            f"🔥 Found {len(videos)} trending videos "
            f"for {selected_region}"
        )

        for index, video in enumerate(
            videos,
            start=1
        ):

            title = video.get(
                "title",
                "Untitled"
            )

            channel = video.get(
                "channel",
                "Unknown"
            )

            views = int(
                video.get(
                    "views",
                    0
                ) or 0
            )

            likes = int(
                video.get(
                    "likes",
                    0
                ) or 0
            )

            comments = int(
                video.get(
                    "comments",
                    0
                ) or 0
            )

            views_per_hour = float(
                video.get(
                    "views_per_hour",
                    0
                ) or 0
            )

            hours_old = float(
                video.get(
                    "hours_old",
                    0
                ) or 0
            )

            trend_score = float(
                video.get(
                    "trend_score",
                    0
                ) or 0
            )

            thumbnail = video.get(
                "thumbnail",
                ""
            )

            url = video.get(
                "url",
                ""
            )


            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            st.markdown(
                f"## #{index} {title}"
            )


            col1, col2 = st.columns(
                [1, 2]
            )


            # ------------------------------------------------
            # THUMBNAIL
            # ------------------------------------------------

            with col1:

                if thumbnail:

                    st.image(
                        thumbnail,
                        width="stretch"
                    )


            # ------------------------------------------------
            # VIDEO INFORMATION
            # ------------------------------------------------

            with col2:

                st.markdown(
                    f"**📺 Channel:** {channel}"
                )

                st.markdown(
                    f"👀 **Views:** {views:,}"
                )

                st.markdown(
                    f"🚀 **Views per hour:** "
                    f"{views_per_hour:,.0f}"
                )

                st.markdown(
                    f"👍 **Likes:** {likes:,}"
                )

                st.markdown(
                    f"💬 **Comments:** {comments:,}"
                )

                st.markdown(
                    f"⏱️ **Published:** "
                    f"{hours_old:.1f} hours ago"
                )

                st.metric(
                    label="🔥 TrendHub Score",
                    value=f"{trend_score:,.0f}"
                )

                if url:

                    st.link_button(
                        "▶️ Watch on YouTube",
                        url,
                        width="content"
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
        "1. YouTube Data API v3 is enabled."
    )

    st.write(
        "2. Your Streamlit Secret is named exactly:"
    )

    st.code(
        "YOUTUBE_API_KEY"
    )

    st.write(
        "3. Your API key is valid."
    )

    st.write(
        "4. Your API key has permission to use "
        "YouTube Data API v3."
    )

    st.write(
        "5. If API restrictions are enabled, "
        "YouTube Data API v3 is allowed."
    )

    st.markdown("---")

    st.warning(
        "Send me the exact error shown above if the "
        "problem continues."
    )
