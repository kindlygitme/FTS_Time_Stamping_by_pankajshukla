import streamlit as st
import zipfile
import os
import tempfile
import whisper
import srt
import datetime

st.set_page_config(page_title="Aakash Subtitle Tool", layout="centered")

st.title("👋 Welcome to Aakash Subtitle Tool")
st.write("Upload a ZIP file of MP4 videos. We’ll transcribe each one and give you `.srt` subtitle files.")

uploaded_zip = st.file_uploader("📦 Upload ZIP file with videos", type=["zip"])

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
            st.warning("No video files found.")
        else:
            st.success(f"Found {len(video_files)} video file(s). Starting transcription...")

        model = whisper.load_model("base")

        for video_path in video_files:
            st.markdown("---")
            video_name = os.path.basename(video_path)
            st.subheader(f"🎥 Processing: {video_name}")

            st.info("🔁 Transcribing with Whisper...")
            result = model.transcribe(video_path)

            # Create SRT content
            subtitles = []
            for i, segment in enumerate(result["segments"]):
                start = datetime.timedelta(seconds=int(segment["start"]))
                end = datetime.timedelta(seconds=int(segment["end"]))
                content = segment["text"].strip()
                subtitles.append(srt.Subtitle(index=i+1, start=start, end=end, content=content))
            srt_content = srt.compose(subtitles)

            # Save SRT file
            srt_filename = os.path.splitext(video_name)[0] + ".srt"
            srt_path = os.path.join(temp_dir, srt_filename)
            with open(srt_path, "w", encoding="utf-8") as f:
                f.write(srt_content)

            with open(srt_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download SRT for {video_name}",
                    data=f,
                    file_name=srt_filename,
                    mime="text/plain"
                )
