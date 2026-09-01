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
    "TrendHub ranks videos using views, engagement, "
    "recency and view velocity."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "⚙️ TrendHub Settings"
)


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

    list(
        region_options.keys()
    )
)


region_code = region_options[
    selected_region
]


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

    list(
        time_options.keys()
    ),

    index=2
)


hours = time_options[
    selected_time
]


# ============================================================
# CATEGORY
# ============================================================

selected_category = st.sidebar.selectbox(

    "📂 Category",

    list(
        CATEGORIES.keys()
    )
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
# CATEGORY INFORMATION
# ============================================================

category_data = CATEGORIES.get(
    selected_category,
    {}
)


if not isinstance(
    category_data,
    dict
):

    category_data = {}


keywords = category_data.get(
    "keywords",
    []
)


category_id = category_data.get(
    "category_id"
)


# ============================================================
# GENERAL TRENDING?
# ============================================================

is_general_trending = (
    selected_category == "🔥 Trending"
)


# ============================================================
# HEADER INFORMATION
# ============================================================

st.markdown("---")


st.subheader(
    f"{selected_category} — Trending Now"
)


st.write(
    f"📍 **Trending region:** "
    f"{selected_region}"
)


st.write(
    f"⏰ **Time window:** "
    f"{selected_time}"
)


if is_general_trending:

    st.info(
        f"🔥 Showing YouTube's popular/trending "
        f"content for the {selected_region} region."
    )

else:

    st.info(
        f"🎯 Showing recent "
        f"**{selected_category}** videos "
        f"for the {selected_region} region."
    )


# ============================================================
# LOAD VIDEOS
# ============================================================

try:

    with st.spinner(
        f"🔎 Finding {selected_category} videos..."
    ):

        videos = get_trending_videos(

            keywords=keywords,

            region_code=region_code,

            hours=hours,

            limit=number_of_videos,

            category_id=category_id,

            use_popular=is_general_trending
        )


    # ========================================================
    # NO RESULTS
    # ========================================================

    if not videos:

        st.warning(
            "⚠️ No matching videos were found."
        )

        st.info(
            "Try increasing the time window "
            "to 48 hours or 7 days."
        )


    # ========================================================
    # RESULTS
    # ========================================================

    else:

        st.success(
            f"🔥 Found {len(videos)} "
            f"trending {selected_category} videos"
        )


        for index, video in enumerate(
            videos,
            start=1
        ):

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            title = video.get(
                "title",
                "Untitled"
            )

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

                thumbnail = video.get(
                    "thumbnail",
                    ""
                )

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
                    f"**📺 Channel:** "
                    f"{video.get('channel', 'Unknown')}"
                )


                st.markdown(
                    f"👀 **Views:** "
                    f"{video.get('views', 0):,}"
                )


                st.markdown(
                    f"🚀 **Views per hour:** "
                    f"{video.get('views_per_hour', 0):,.0f}"
                )


                st.markdown(
                    f"👍 **Likes:** "
                    f"{video.get('likes', 0):,}"
                )


                st.markdown(
                    f"💬 **Comments:** "
                    f"{video.get('comments', 0):,}"
                )


                st.markdown(
                    f"⏱️ **Published:** "
                    f"{video.get('hours_old', 0):.1f} "
                    f"hours ago"
                )


                st.metric(

                    label="🔥 TrendHub Score",

                    value=f"{video.get('trend_score', 0):,.0f}"
                )


                st.link_button(

                    "▶️ Watch on YouTube",

                    video.get(
                        "url",
                        "#"
                    ),

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
        "1. YouTube Data API v3 is enabled "
        "in your Google Cloud project."
    )

    st.write(
        "2. Your Streamlit Secret is named exactly:"
    )

    st.code(
        "YOUTUBE_API_KEY"
    )

    st.write(
        "3. The API key is correctly entered "
        "in Streamlit Secrets."
    )

    st.write(
        "4. The API key belongs to the same "
        "Google Cloud project where YouTube Data API "
        "is enabled."
    )

    st.write(
        "5. If API restrictions are enabled, "
        "YouTube Data API v3 must be allowed."
    )

    st.markdown("---")

    st.warning(
        "If you see a 400, 403, quotaExceeded, "
        "API_KEY_INVALID or other error, "
        "send me the exact error message."
    )
