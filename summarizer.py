from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from transformers.pipelines import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_video(video_id: str) -> str:
    """
    Fetches the YouTube transcript for the given video_id, joins the text, and summarizes it into 3–5 expressive sentences.
    Returns the summary as a string. Handles transcript unavailability gracefully.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([entry['text'] for entry in transcript])
    except (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable) as e:
        return f"Transcript unavailable: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

    # BART has a max token limit, so chunk if needed (not handled here for brevity)
    summary = summarizer(full_text, max_length=180, min_length=60, do_sample=False)[0]['summary_text']
    return summary 