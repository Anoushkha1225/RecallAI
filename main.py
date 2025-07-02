import streamlit as st
from summarizer import summarize_video
from embedder import get_embedding
from search import add_to_index, search_memory
import os

# Mock user_id for session
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = 'demo-user'
user_id = st.session_state['user_id']

st.title("RecallAI")

# Section 1: Add YouTube video to memory
st.header("Add YouTube Video to Memory")
with st.form("add_video_form"):
    video_id = st.text_input("YouTube Video ID")
    title = st.text_input("Video Title")
    submitted = st.form_submit_button("Summarize and Add to Memory")
    if submitted and video_id and title:
        with st.spinner("Summarizing video..."):
            summary = summarize_video(video_id)
        if summary.startswith("Transcript unavailable") or summary.startswith("An error occurred"):
            st.error(summary)
        else:
            embedding = get_embedding(summary)
            add_to_index(user_id, video_id, title, summary, embedding)
            st.success("Video summary added to memory!")
            st.write("**Summary:**", summary)

# Section 2: Search memory
st.header("Search Memory")
with st.form("search_form"):
    query = st.text_input("Enter your search query")
    search_submitted = st.form_submit_button("Search")
    if search_submitted and query:
        with st.spinner("Searching memory..."):
            results = search_memory(user_id, query)
        if not results:
            st.info("No results found.")
        else:
            for result in results:
                st.subheader(result['title'])
                st.image(f"https://img.youtube.com/vi/{result['video_id']}/0.jpg", width=320)
                st.write(result['summary'])

# Section 3: Clear memory
st.header("Memory Management")
if st.button("Clear My Memory"):
    index_path = f"index_{user_id}.faiss"
    memory_path = f"memory_{user_id}.json"
    removed = False
    if os.path.exists(index_path):
        os.remove(index_path)
        removed = True
    if os.path.exists(memory_path):
        os.remove(memory_path)
        removed = True
    if removed:
        st.success("Your memory has been cleared!")
    else:
        st.info("No memory to clear.")
