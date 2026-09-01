import streamlit as st

from categories import CATEGORIES
from trending import get_trending_videos


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="TrendHub",
    page_icon="🔥",
    layout="wide"
)


# ==================================================
# TITLE
# ==================================================

st.title("🔥 TrendHub")

st.caption(
    "Discover the most trending YouTube videos by "
    "country, category and time period."
)


# ==================================================
# COUNTRIES
# ==================================================

COUNTRIES = {

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
    "🇿🇦 South Africa": "ZA"
}


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.header(
    "⚙️ TrendHub Settings"
)


# --------------------------------------------------
# COUNTRY
# --------------------------------------------------

selected_country = st.sidebar.selectbox(
    "🌎 Country",
    list(COUNTRIES.keys())
)

region_code = COUNTRIES[
    selected_country
]


# --------------------------------------------------
# TIME PERIOD
# --------------------------------------------------

time_options = {

    "Last 6 hours": 6,
    "Last 12 hours": 12,
    "Last 24 hours": 24,
    "Last 48 hours": 48,
    "Last 7 days": 168
}


selected_time = st.sidebar.selectbox(
    "⏱️ Time Period",
    list(time_options.keys()),
    index=2
)

hours = time_options[
    selected_time
]


# --------------------------------------------------
# CATEGORY
# --------------------------------------------------

category_names = list(
    CATEGORIES.keys()
)


selected_category = st.sidebar.selectbox(
    "📂 Category",
    category_names
)


# --------------------------------------------------
# NUMBER OF VIDEOS
# --------------------------------------------------

number_of_videos = st.sidebar.selectbox(
    "🏆 Number of Videos",
    [5, 10],
    index=0
)


# --------------------------------------------------
# REFRESH
# --------------------------------------------------

refresh = st.sidebar.button(
    "🔄 Refresh Trends"
)


# ==================================================
# CATEGORY DATA
# ==================================================

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


mode = category_data.get(
    "mode",
    "search"
)


# ==================================================
# SHOW SETTINGS
# ==================================================

st.info(
    f"Showing **{selected_category}** videos for "
    f"**{selected_country}** from "
    f"**{selected_time}**."
)


# ==================================================
# LOAD VIDEOS
# ==================================================

try:

    with st.spinner(
        "🔎 Finding the latest trending videos..."
    ):

        videos = get_trending_videos(

            keywords=keywords,

            region_code=region_code,

            hours=hours,

            limit=number_of_videos,

            category_id=category_id,

            mode=mode
        )


except Exception as e:

    st.error(
        f"❌ Unable to load YouTube trends:\n\n{e}"
    )

    st.stop()


# ==================================================
# NO RESULTS
# ==================================================

if not videos:

    st.warning(
        "No videos were found for the selected "
        "country, category and time period."
    )

    st.stop()


# ==================================================
# RESULTS COUNT
# ==================================================

st.success(
    f"🔥 Found {len(videos)} trending videos"
)


# ==================================================
# DISPLAY VIDEOS
# ==================================================

for index, video in enumerate(
    videos,
    start=1
):

    video_id = video.get(
        "id"
    )

    title = video.get(
        "title",
        "Untitled video"
    )

    channel = video.get(
        "channel",
        "Unknown channel"
    )

    thumbnail = video.get(
        "thumbnail"
    )

    views = video.get(
        "views",
        0
    )

    likes = video.get(
        "likes",
        0
    )

    comments = video.get(
        "comments",
        0
    )

    age_hours = video.get(
        "age_hours",
        0
    )

    views_per_hour = video.get(
        "views_per_hour",
        0
    )

    trend_score = video.get(
        "trend_score",
        0
    )


    # ==================================================
    # VIDEO CONTAINER
    # ==================================================

    with st.container():

        col1, col2 = st.columns(
            [1, 3]
        )


        # --------------------------------------------------
        # THUMBNAIL
        # --------------------------------------------------

        with col1:

            if thumbnail:

                st.image(
                    thumbnail,
                    width="stretch"
                )


        # --------------------------------------------------
        # INFORMATION
        # --------------------------------------------------

        with col2:

            st.subheader(
                f"#{index} {title}"
            )

            st.write(
                f"📺 **Channel:** {channel}"
            )

            st.write(
                f"👁️ **Views:** {views:,}   "
                f"❤️ **Likes:** {likes:,}   "
                f"💬 **Comments:** {comments:,}"
            )

            st.write(
                f"⏱️ **Age:** {age_hours:.1f} hours   "
                f"🚀 **Views/hour:** {views_per_hour:,.0f}"
            )

            st.write(
                f"🔥 **Trend Score:** {trend_score}"
            )


            if video_id:

                youtube_url = (
                    "https://www.youtube.com/watch?v="
                    + video_id
                )

                st.link_button(
                    "▶️ Watch on YouTube",
                    youtube_url
                )


        st.divider()


# ==================================================
# FOOTER
# ==================================================

st.caption(
    "TrendHub uses the YouTube Data API to discover "
    "and rank trending videos."
)
