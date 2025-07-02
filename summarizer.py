import re
import urllib.parse
from bs4 import BeautifulSoup, Tag
from typing import cast

def summarize_video(title: str) -> str:
    title = re.sub(r'[^\u0000-\u00ff\w\s]', '', title)
    words = title.split()
    if not words:
        return "No summary available"
    summary = " ".join(words[:8])
    keywords = [w for w in words if len(w) > 5][:3]
    if keywords:
        summary += ". Keywords: " + ", ".join(keywords)
    return summary.strip()

def extract_video_id(url):
    parsed = urllib.parse.urlparse(url)
    qs = urllib.parse.parse_qs(parsed.query)
    return qs.get('v', [None])[0]

def parse_watch_history_html(html_bytes):
    soup = BeautifulSoup(html_bytes, "html.parser")
    entries = []
    for div in soup.find_all("div", class_="content-cell"):
        if isinstance(div, Tag):
            a_tag = div.find("a")
            if isinstance(a_tag, Tag) and "href" in a_tag.attrs:
                url = a_tag["href"]
                title = a_tag.text.strip()
                entries.append({
                    "title": title,
                    "titleUrl": url
                })
    return entries