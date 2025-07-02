import streamlit as st
import json
from summarizer import summarize_video, parse_watch_history_html
from embedder import get_embedding
from search import add_to_index, search_memory, clear_memory
import zipfile

# Set up the Streamlit page
st.set_page_config(page_title="RecallAI", page_icon="🧠", layout="centered")
st.title("RecallAI 🔍")
st.write("Upload your YouTube watch history and search it using vague memories!")

# Dummy user ID — replace with real login later
user_id = "demo-user"

# File upload section
st.header("1. Upload Your YouTube Watch History")
uploaded_file = st.file_uploader(
    "Upload 'watch-history.html', 'watch-history.json' or ZIP file",
    type=["html", "zip", "json"]
)

data = None

if uploaded_file:
    try:
        with st.spinner("Reading your file..."):
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
                                data = parse_watch_history_html(html_bytes)
                            break
                    if data is None:
                        st.error("Could not find a valid history file inside ZIP.")
                        st.stop()

            elif uploaded_file.name.endswith(".html"):
                html_bytes = uploaded_file.read()
                data = parse_watch_history_html(html_bytes)

            elif uploaded_file.name.endswith(".json"):
                data = json.load(uploaded_file)

        if data:
            st.success(f"✅ Loaded {len(data)} watch entries!")

            # Clear existing memory
            clear_memory(user_id)

            # Progress bar and summarization
            st.info("Starting summarization and embedding...")
            progress_bar = st.progress(0, text="Summarizing and indexing...")

            total = len(data)
            for i, entry in enumerate(data):
                if "title" in entry and "titleUrl" in entry:
                    title = entry["title"]
                    url = entry["titleUrl"]
                    summary = summarize_video(title)
                    embedding = get_embedding(summary)
                    add_to_index(user_id, title, summary, url, embedding)
                progress_bar.progress((i + 1) / total, text=f"Processed {i + 1} of {total} videos...")

            st.success("🎉 Memory updated with your YouTube history!")

        else:
            st.warning("No data found.")

    except Exception as e:
        st.error(f"Error: {e}")

# Search section
st.header("2. Search Your Memories")
query = st.text_input("What do you remember?")

if query:
    query_embedding = get_embedding(query)
    results = search_memory(user_id, query_embedding)

    if results:
        st.subheader("🔍 Top Matches")
        for res in results:
            st.markdown(f"### [{res['title']}]({res['url']})")
            st.markdown(f"**Summary:** {res['summary']}")
            st.markdown("---")
    else:
        st.warning("😕 No matches found.")
