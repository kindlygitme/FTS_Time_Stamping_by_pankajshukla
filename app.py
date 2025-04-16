import streamlit as st
import zipfile
import os
import tempfile
import whisper
import srt
import datetime
import ffmpeg

st.set_page_config(page_title="Transcript Generator", layout="centered")
st.title("🎬 Video Transcript to SRT Generator")
st.write("Upload a ZIP file containing videos. We'll generate `.srt` transcript files for manual timestamping.")

uploaded_zip = st.file_uploader("📦 Upload ZIP file (MP4/MKV/AVI)", type=["zip"])

if uploaded_zip:
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded zip
        zip_path = os.path.join(temp_dir, "videos.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        # Extract zip contents
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # 🔍 Recursively find all video files inside folders
        video_files = []
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith((".mp4", ".mkv", ".avi")):
                    video_files.append(os.path.join(root, file))

        if not video_files:
            st.warning("❌ No video files found inside the ZIP (even in subfolders).")
        else:
            st.success(f"✅ Found {len(video_files)} video file(s). Starting transcription...")

        model = whisper.load_model("base")

        for video_path in video_files:
            st.markdown("---")
            video_name = os.path.basename(video_path)
            st.subheader(f"🎥 {video_name}")

            try:
                # Extract audio from video using ffmpeg-python
                audio_path = os.path.join(temp_dir, f"{os.path.splitext(video_name)[0]}.wav")
                ffmpeg.input(video_path).output(audio_path, ac=1, ar='16000').overwrite_output().run(quiet=True)

                # Transcribe with Whisper
                st.info("🔁 Transcribing...")
                result = model.transcribe(audio_path)

                # Convert to SRT format
                subtitles = []
                for i, segment in enumerate(result["segments"]):
                    start = datetime.timedelta(seconds=int(segment["start"]))
                    end = datetime.timedelta(seconds=int(segment["end"]))
                    content = segment["text"].strip()
                    subtitles.append(srt.Subtitle(index=i+1, start=start, end=end, content=content))
                srt_text = srt.compose(subtitles)

                # Save SRT file
                srt_filename = os.path.splitext(video_name)[0] + ".srt"
                srt_path = os.path.join(temp_dir, srt_filename)
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(srt_text)

                # Provide download button
                with open(srt_path, "rb") as f:
                    st.download_button(
                        label=f"⬇️ Download SRT for {video_name}",
                        data=f,
                        file_name=srt_filename,
                        mime="text/plain"
                    )

            except Exception as e:
                st.error(f"❌ Error processing {video_name}: {str(e)}")
