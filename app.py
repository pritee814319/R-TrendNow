
import streamlit as st

from categories import CATEGORIES
    from trending import get_trending_videos


# ============================================================
# PAGE CONFIG
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

st.caption(
    "Discover the most interesting and fast-growing YouTube videos."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("TrendHub Settings")


# Country
countries = {
    "🇨🇦 Canada": "CA",
    "🇺🇸 United States": "US",
    "🇬🇧 United Kingdom": "GB",
    "🇮🇳 India": "IN",
    "🇦🇺 Australia": "AU",
    "🇳🇿 New Zealand": "NZ",
    "🇩🇪 Germany": "DE",
    "🇫🇷 France": "FR",
    "🇮🇹 Italy": "IT",
    "🇪🇸 Spain": "ES",
    "🇧🇷 Brazil": "BR",
    "🇲🇽 Mexico": "MX",
    "🇯🇵 Japan": "JP",
    "🇰🇷 South Korea": "KR",
    "🇨🇳 China": "CN",
    "🇸🇬 Singapore": "SG",
    "🇦🇪 United Arab Emirates": "AE",
    "🇸🇦 Saudi Arabia": "SA",
    "🇿🇦 South Africa": "ZA",
}


selected_country = st.sidebar.selectbox(
    "🌎 Country",
    list(countries.keys())
)

region_code = countries[
    selected_country
]


# Time window
time_windows = {
    "Last 6 hours": 6,
    "Last 12 hours": 12,
    "Last 24 hours": 24,
    "Last 48 hours": 48,
    "Last 7 days": 168,
}


selected_time = st.sidebar.selectbox(
    "⏱️ Time Window",
    list(time_windows.keys()),
    index=2
)

hours = time_windows[
    selected_time
]


# Category
selected_category = st.sidebar.selectbox(
    "📂 Category",
    list(CATEGORIES.keys())
)


# Number
number_of_videos = st.sidebar.selectbox(
    "🏆 Number of Videos",
    [5, 10],
    index=0
)


# Refresh
refresh = st.sidebar.button(
    "🔄 Refresh Trends",
    width="stretch"
)


# ============================================================
# CATEGORY DATA
# ============================================================

category_data = CATEGORIES.get(
    selected_category,
    {}
)

keywords = category_data.get(
    "keywords",
    []
)

category_id = category_data.get(
    "category_id"
)


# General trending uses YouTube's
# regional mostPopular chart.
is_general_trending = (
    selected_category
    == "🔥 Trending"
)


# ============================================================
# INFORMATION
# ============================================================

st.info(
    f"Showing **{number_of_videos}** "
    f"top videos for **{selected_category}** "
    f"in **{selected_country}** "
    f"from the **{selected_time}**."
)


# ============================================================
# LOAD VIDEOS
# ============================================================

try:

    with st.spinner(
        "🔎 Finding trending videos..."
    ):

        videos = get_trending_videos(
            keywords=keywords,
            region_code=region_code,
            hours=hours,
            limit=number_of_videos,
            category_id=category_id,
            use_popular=is_general_trending
        )

except Exception as e:

    st.error(
        "❌ Unable to load trending videos."
    )

    st.exception(e)

    st.stop()


# ============================================================
# NO RESULTS
# ============================================================

if not videos:

    st.warning(
        "No matching videos were found "
        "for this country, category and time window."
    )

    st.stop()


# ============================================================
# RESULTS
# ============================================================

st.success(
    f"🔥 Found {len(videos)} trending videos"
)


for index, video in enumerate(
    videos,
    start=1
):

    st.markdown(
        f"## #{index} — {video['title']}"
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    # --------------------------------------------------------
    # THUMBNAIL
    # --------------------------------------------------------

    with col1:

        if video.get(
            "thumbnail"
        ):

            st.image(
                video["thumbnail"],
                width="stretch"
            )


    # --------------------------------------------------------
    # INFORMATION
    # --------------------------------------------------------

    with col2:

        st.write(
            f"📺 **Channel:** "
            f"{video['channel']}"
        )

        st.write(
            f"👁️ **Views:** "
            f"{video['views']:,}"
        )

        st.write(
            f"❤️ **Likes:** "
            f"{video['likes']:,}"
        )

        st.write(
            f"💬 **Comments:** "
            f"{video['comments']:,}"
        )

        st.write(
            f"⏱️ **Age:** "
            f"{video['hours_old']:.1f} hours"
        )

        st.write(
            f"🚀 **Views/hour:** "
            f"{video['views_per_hour']:,.0f}"
        )

        st.write(
            f"🔥 **Trend Score:** "
            f"{video['trend_score']:,.0f}"
        )

        st.link_button(
            "▶️ Watch on YouTube",
            f"https://www.youtube.com/watch?v={video['video_id']}",
            width="content"
        )

    st.divider()

