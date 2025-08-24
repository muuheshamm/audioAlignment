import os
import pytubefix
import ffmpeg
import time
from datetime import datetime

# Ensure output folder exists
output_dir = "audios"
os.makedirs(output_dir, exist_ok=True)

# YouTube video URL
youtube_url = "https://www.youtube.com/watch?v=HndOkrEtSd4"

# Generate unique filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
filename = os.path.join(output_dir, f"audio_{timestamp}.wav")

time.sleep(2)

print("Downloading audio from YouTube...")
yt = pytubefix.YouTube(youtube_url)

print("Fetching audio stream...")
stream = yt.streams.filter(only_audio=True).first()
stream_url = stream.url

print("Converting audio stream to WAV with ffmpeg...")
ffmpeg.input(stream_url).output(filename, format="wav", loglevel="error").run()

# Save the filename for later use
with open("filename_audio.txt", "w") as f:
    f.write(filename)

print(f"✅ Audio downloaded and saved as: {filename}")
