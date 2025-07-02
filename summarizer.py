from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import urllib.parse

model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

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
    summary = summarize_text(full_text)
    return summary

def summarize_text(text: str) -> str:
    # Tokenize and prepare input
    tokens = tokenizer(text, truncation=True, padding="longest", return_tensors="pt")
    # Generate summary ids
    summary_ids = model.generate(**tokens, max_length=60, min_length=20, num_beams=4, early_stopping=True)
    # Decode summary
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

def extract_video_id(url):
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    return qs.get('v', [None])[0] 