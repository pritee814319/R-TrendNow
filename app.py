import streamlit as st

from categories import CATEGORIES
from trending import get_trending_videos


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="TrendHub",
    page_icon="🔥",
    layout="wide"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🔥 TrendHub")

st.write(
    "Discover what is trending on YouTube right now."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("⚙️ TrendHub Settings")


region_options = {
    "🇨🇦 Canada": "CA",
    "🇺🇸 United States": "US",
    "🇮🇳 India": "IN",
    "🇬🇧 United Kingdom": "GB",
    "🇦🇺 Australia": "AU",
    "🌎 Worldwide": "US"
}


selected_region = st.sidebar.selectbox(
    "🌎 Location",
    list(region_options.keys())
)


region_code = region_options[
    selected_region
]


time_options = {
    "Last 6 hours": 6,
    "Last 12 hours": 12,
    "Last 24 hours": 24,
    "Last 48 hours": 48,
    "Last 7 days": 168
}


selected_time = st.sidebar.selectbox(
    "⏰ Find videos from",
    list(time_options.keys()),
    index=2
)


hours = time_options[
    selected_time
]


selected_category = st.sidebar.selectbox(
    "📂 Category",
    list(CATEGORIES.keys())
)


if st.sidebar.button(
    "🔄 Refresh Trending",
    use_container_width=True
):
    st.cache_data.clear()
    st.rerun()


# --------------------------------------------------
# CATEGORY INFORMATION
# --------------------------------------------------

category_data = CATEGORIES[
    selected_category
]

keywords = category_data[
    "keywords"
]

category_id = category_data.get(
    "category_id"
)


st.markdown(
    f"## {selected_category}"
)

st.caption(
    f"Showing videos published within "
    f"the {selected_time.lower()}."
)


# --------------------------------------------------
# GET TRENDING VIDEOS
# --------------------------------------------------

try:

    with st.spinner(
        "🔥 Finding what is trending..."
    ):

        videos = get_trending_videos(
            keywords=keywords,
            region_code=region_code,
            hours=hours,
            limit=5,
            category_id=category_id
        )


    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    if not videos:

        st.warning(
            "No recent videos were found."
        )

        st.info(
            "Try selecting a longer time window."
        )

    else:

        st.success(
            f"Found {len(videos)} trending videos."
        )


        for index, video in enumerate(
            videos,
            start=1
        ):

            st.markdown(
                f"## #{index} {video['title']}"
            )


            col1, col2 = st.columns(
                [1, 2]
            )


            # ------------------------------------------
            # THUMBNAIL
            # ------------------------------------------

            with col1:

                if video["thumbnail"]:

                    st.image(
                        video["thumbnail"],
                        use_container_width=True
                    )


            # ------------------------------------------
            # INFORMATION
            # ------------------------------------------

            with col2:

                st.write(
                    f"**📺 Channel:** "
                    f"{video['channel']}"
                )


                st.write(
                    f"👀 **Views:** "
                    f"{video['views']:,}"
                )


                st.write(
                    f"🚀 **Views/hour:** "
                    f"{video['views_per_hour']:,.0f}"
                )


                st.write(
                    f"👍 **Likes:** "
                    f"{video['likes']:,}"
                )


                st.write(
                    f"💬 **Comments:** "
                    f"{video['comments']:,}"
                )


                st.write(
                    f"⏱️ **Published:** "
                    f"{video['hours_old']:.1f} "
                    f"hours ago"
                )


                st.metric(
                    "🔥 TrendHub Score",
                    f"{video['trend_score']:,.0f}"
                )


                st.link_button(
                    "▶️ Watch on YouTube",
                    video["url"]
                )


            st.divider()


except Exception as e:

    st.error(
        "❌ Unable to load YouTube data."
    )

    st.write(
        "Please check your YouTube API key "
        "and Streamlit Secrets."
    )

    st.code(
        str(e)
    )
