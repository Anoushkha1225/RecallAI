import streamlit as st
import json
from summarizer import summarize_video
from embedder import get_embedding
from search import add_to_index, search_memory, clear_memory
import zipfile
import io
# Set up page
st.set_page_config(page_title="RecallAI", page_icon="🧠", layout="centered")
st.title("RecallAI 🔍")
st.write("Upload your YouTube watch history (Google Takeout JSON) and search with vague memories!")

# Simulated user ID (replace with login-based later)
user_id = "demo-user"

# Step 1: Upload history
# Step 1: Upload watch history JSON or ZIP
st.header("1. Upload your YouTube Watch History")
uploaded_file = st.file_uploader(
    "Upload your 'watch-history.json' or ZIP file from Google Takeout", 
    type=["json", "zip"]
)

if uploaded_file:
    # Determine file type
    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file) as z:
            data = None
            for name in z.namelist():
                if "watch-history.json" in name:
                    with z.open(name) as f:
                        data = json.load(f)
                    break
            if data is None:
                st.error("Could not find 'watch-history.json' inside the ZIP file.")
                st.stop()
    else:
        # Assume JSON
        data = json.load(uploaded_file)
    
    # Process watch history
    clear_memory(user_id)  # Reset memory
    st.success("Processing and summarizing your history...")

    for entry in data:
        if "titleUrl" in entry and "title" in entry:
            url = entry["titleUrl"]
            title = entry["title"]
            summary = summarize_video(title)
            embedding = get_embedding(summary)
            add_to_index(user_id, title, summary, url, embedding)

    st.success("Memory updated with your watch history!")


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
