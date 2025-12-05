from youtube_transcript_api import YouTubeTranscriptApi

# video_id = "hrgR1vc5CXM"
video_id = "HndOkrEtSd4"
ytt_api = YouTubeTranscriptApi()

try:
    transcript = ytt_api.fetch(video_id, languages=['ar'])
    text = "\n".join([snippet.text for snippet in transcript])

    # print(text)

    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("Transcript saved")

except Exception as e:
    print(f"Error: {e}.\nArabic transcript may not be available for this video.")