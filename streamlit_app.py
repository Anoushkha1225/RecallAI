import streamlit as st
import json
from summarizer import summarize_video
from embedder import get_embedding
from search import add_to_index, search_memory, clear_memory

# Set up page
st.set_page_config(page_title="RecallAI", page_icon="🧠", layout="centered")
st.title("RecallAI 🔍")
st.write("Upload your YouTube watch history (Google Takeout JSON) and search with vague memories!")

# Simulated user ID (replace with login-based later)
user_id = "demo-user"

# Step 1: Upload history
st.header("1. Upload YouTube Watch History JSON")
uploaded_file = st.file_uploader("Upload 'watch-history.json'", type="json")

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        clear_memory(user_id)
        st.success("Processing your watch history...")

        for entry in data:
            if "title" in entry and "titleUrl" in entry:
                title = entry["title"]
                url = entry["titleUrl"]
                summary = summarize_video(title)
                embedding = get_embedding(summary)
                add_to_index(user_id, title, summary, url, embedding)

        st.success("Memory updated with your watch history!")

    except Exception as e:
        st.error(f"Failed to process file: {e}")

# Step 2: Search
st.header("2. Search your memories")
query = st.text_input("What do you remember about the video?")

if query:
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
