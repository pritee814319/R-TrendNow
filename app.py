import streamlit as st

from categories import CATEGORIES
from trending import get_trending_videos


st.set_page_config(
    page_title="TrendHub",
    page_icon="🔥",
    layout="wide",
)


st.title("🔥 TrendHub")
st.subheader("Discover what's trending on YouTube")


selected_category = st.selectbox(
    "Choose a category",
    list(CATEGORIES.keys())
)


category = CATEGORIES[selected_category]


st.write(
    f"### Top 5 {selected_category} Videos"
)


try:

    videos = get_trending_videos(
        category["query"],
        limit=5
    )

    if not videos:
        st.warning("No videos found.")
    else:

        for index, video in enumerate(videos, start=1):

            st.markdown(
                f"## #{index} {video['title']}"
            )

            col1, col2 = st.columns([1, 2])

            with col1:
                if video["thumbnail"]:
                    st.image(
                        video["thumbnail"],
                        use_container_width=True
                    )

            with col2:

                st.write(
                    f"**Channel:** {video['channel']}"
                )

                st.write(
                    f"👀 **Views:** "
                    f"{video['views']:,}"
                )

                if video["likes"]:
                    st.write(
                        f"👍 **Likes:** "
                        f"{video['likes']:,}"
                    )

                st.write(
                    f"📅 **Published:** "
                    f"{video['published'][:10]}"
                )

                st.link_button(
                    "▶️ Watch on YouTube",
                    video["url"]
                )

            st.divider()


except Exception as e:

    st.error(
        "Unable to load YouTube videos."
    )

    st.caption(
        f"Error details: {e}"
    )
