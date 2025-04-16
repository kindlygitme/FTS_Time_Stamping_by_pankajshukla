import streamlit as st
import zipfile
import os
import tempfile
import moviepy.editor as mp
import whisper
import srt
import datetime

st.set_page_config(page_title="Welcome to Aakash", layout="centered")
st.title("🎓 Welcome to Aakash")
st.write("Upload a ZIP file containing videos. This app will extract transcripts (SRT) for each one.")

uploaded_zip = st.file_uploader("Upload a ZIP file with videos", type=["zip"])

if uploaded_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "videos.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        video_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.lower().endswith((".mp4", ".mkv", ".avi"))
        ]

        if not video_files:
            st.warning("No video files found in the ZIP.")
        else:
            st.success(f"Found {len(video_files)} video file(s). Starting transcription...")

        model = whisper.load_model("base")
        srt_links = []

        for video_path in video_files:
            st.write(f"🎬 Processing: `{os.path.basename(video_path)}`")

            # Extract audio
            audio_path = os.path.join(temp_dir, "audio.wav")
            video = mp.VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)

            # Transcribe
            result = model.transcribe(audio_path)

            # Create SRT content
            subtitles = []
            for i, segment in enumerate(result["segments"]):
                start = datetime.timedelta(seconds=int(segment["start"]))
                end = datetime.timedelta(seconds=int(segment["end"]))
                content = segment["text"].strip()
                subtitles.append(srt.Subtitle(index=i+1, start=start, end=end, content=content))
            srt_content = srt.compose(subtitles)

            # Save SRT
            srt_filename = os.path.basename(video_path).rsplit(".", 1)[0] + ".srt"
            srt_path = os.path.join(temp_dir, srt_filename)
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

            # Add download link
            with open(srt_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download SRT for {os.path.basename(video_path)}",
                    data=f,
                    file_name=srt_filename,
                    mime="text/plain"
                )
