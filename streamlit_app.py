import streamlit as st
import json
from summarizer import summarize_video
from embedder import get_embedding
from search import add_to_index, search_memory, clear_memory

# Page configuration
st.set_page_config(page_title="RecallAI", page_icon="🔍", layout="centered")

st.title("RecallAI 🔍")
st.markdown("**Your AI-powered memory for videos you've watched.**")
st.markdown("💡 Describe the vibe, person, topic — and RecallAI will help you remember.")

# Step 0: Username input (simulates login)
st.header("👤 User Login")
user_id = st.text_input("Enter your username (e.g., anshu123)", value="demo-user")

# Step 1: Upload watch history JSON
st.header("1. Upload your YouTube Watch History")
uploaded_file = st.file_uploader("Upload your 'watch-history.json' file", type="json")

if uploaded_file:
    try:
        data = json.load(uploaded_file)
    except Exception:
        st.error("❌ Failed to read the JSON file. Please upload a valid YouTube watch-history.json.")
        st.stop()

    if not any("title" in entry and "titleUrl" in entry for entry in data):
        st.error("This doesn't look like a valid YouTube watch-history file.")
        st.stop()

    clear_memory(user_id)
    count = 0
    with st.spinner("Processing and summarizing your history..."):
        for entry in data:
            if "titleUrl" in entry and "title" in entry:
                url = entry["titleUrl"]
                title = entry["title"]
                summary = summarize_video(title)
                embedding = get_embedding(summary)
                add_to_index(user_id, title, summary, url, embedding)
                count += 1

    st.success(f"✅ Added {count} videos to your memory.")

st.markdown("📥 [How to Download Your Watch History from Google Takeout](https://takeout.google.com/)")

# Step 2: Search from memory
st.header("2. Search with a vague description")
query = st.text_input("What do you remember about the video?")

if query:
    query_embedding = get_embedding(query)
    results = search_memory(user_id, query_embedding, top_k=5)

    if results:
        st.subheader("🔍 Top Matches:")
        for result in results:
            st.markdown(f"### [{result['title']}]({result['url']})")
            st.markdown(f"**Summary:** {result['summary']}")
            st.markdown("---")
    else:
        st.warning("😕 No matches found. Try describing the topic, emotion, or keywords more clearly.")