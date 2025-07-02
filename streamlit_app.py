import streamlit as st
import json
from summarizer import summarize_video, parse_watch_history_html
from embedder import get_embedding
from search import add_to_index, search_memory, clear_memory
import zipfile

# Page config
st.set_page_config(page_title="RecallAI", page_icon="🧠", layout="centered")
st.title("RecallAI 🔍")
st.write("Upload your YouTube watch history (Google Takeout HTML/JSON/ZIP) and search with vague memories!")

user_id = "demo-user"

# Choose number of videos
num_videos = st.slider("How many videos do you want to process?", min_value=5, max_value=100, value=20, step=5)

# Step 1: Upload history
st.header("1. Upload your YouTube Watch History")
uploaded_file = st.file_uploader("Upload your YouTube 'watch-history.html', 'watch-history.json' or ZIP", type=["html", "zip", "json"])

data = None

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".zip"):
            with zipfile.ZipFile(uploaded_file) as z:
                for name in z.namelist():
                    if "watch-history.json" in name:
                        with z.open(name) as f:
                            data = json.load(f)
                        break
                    elif "watch-history.html" in name:
                        with z.open(name) as f:
                            html_bytes = f.read()
                            data = parse_watch_history_html(html_bytes)[:num_videos]
                        break
                if data is None:
                    st.error("Could not find watch-history file inside the ZIP.")
                    st.stop()

        elif uploaded_file.name.endswith(".html"):
            html_bytes = uploaded_file.read()
            data = parse_watch_history_html(html_bytes)[:num_videos]

        elif uploaded_file.name.endswith(".json"):
            data = json.load(uploaded_file)

        if data:
            clear_memory(user_id)
            with st.spinner("Summarizing and updating memory..."):
                progress = st.progress(0)
                total = min(len(data), num_videos if uploaded_file.name.endswith((".html", ".zip")) else len(data))
                
                for i, entry in enumerate(data[:total]):
                    if "titleUrl" in entry and "title" in entry:
                        url = entry["titleUrl"]
                        title = entry["title"]
                        summary = summarize_video(title)
                        embedding = get_embedding(summary)
                        add_to_index(user_id, title, summary, url, embedding)
                    progress.progress((i + 1) / total)

            st.success("Memory updated with your watch history!")

        else:
            st.warning("No data found in the file.")

    except Exception as e:
        st.error(f"Failed to process file: {e}")

# Step 2: Search
st.header("2. Search your memories")
query = st.text_input("What do you remember about the video?")

if query:
    with st.spinner("Searching..."):
        query_embedding = get_embedding(query)
        results = search_memory(user_id, query_embedding)

    if results:
        st.subheader("Top Matches")
        for res in results:
            st.markdown(f"### [{res['title']}]({res['url']})")
            st.markdown(f"**Summary:** {res['summary']}")
            st.markdown("---")
    else:
        st.warning("No matches found.")
