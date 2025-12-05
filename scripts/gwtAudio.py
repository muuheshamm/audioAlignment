import os
import pytubefix
import ffmpeg
import time
from datetime import datetime

# Ensure output folder exists
output_dir = "audios"
os.makedirs(output_dir, exist_ok=True)

# YouTube video URL
youtube_url = "https://www.youtube.com/watch?v=LRdVZn5_2dQ"

# Generate unique filename with timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
filename_wav = os.path.join(output_dir, f"audio_{timestamp}.wav")
filename_mp4 = os.path.join(output_dir, f"audio_{timestamp}.mp4")

time.sleep(2)

print("🎬 Downloading audio from YouTube...")
yt = pytubefix.YouTube(youtube_url)

print("📥 Fetching best audio stream...")
stream = yt.streams.filter(only_audio=True).first()

# Download as mp4 (original container)
print("⬇️ Downloading audio stream...")
stream.download(filename=filename_mp4)

# Convert with ffmpeg to WAV
print("🔄 Converting to WAV with ffmpeg...")
ffmpeg.input(filename_mp4).output(filename_wav, format="wav", loglevel='error').run()

# Optionally remove the intermediate mp4
os.remove(filename_mp4)

# Save the filename for later use
with open("filename_audio.txt", "w") as f:
    f.write(filename_wav)

print(f"✅ Audio downloaded and saved as: {filename_wav}")
