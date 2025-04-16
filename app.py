import streamlit as st
import zipfile
import os
import tempfile
import whisper

st.set_page_config(page_title="SRT Subtitle Generator", layout="centered")
st.title("🎬 Generate SRT Subtitles from Videos")
st.write("Upload a ZIP file containing MP4/MKV/AVI videos. We'll generate subtitles (SRT format) and let you download them.")

uploaded_zip = st.file_uploader("📁 Upload ZIP file", type=["zip"])

if uploaded_zip is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        video_files = [
            os.path.join(temp_dir, f)
            for f in os.listdir(temp_dir)
            if f.lower().endswith((".mp4", ".mkv", ".avi"))
        ]

        model = whisper.load_model("base")

        for video_path in video_files:
            st.markdown("---")
            video_name = os.path.basename(video_path)
            st.subheader(f"📹 {video_name}")

            st.info("⏳ Generating transcript...")
            result = model.transcribe(video_path, task="transcribe", verbose=False)

            srt_lines = []
            for i, segment in enumerate(result["segments"]):
                start = int(segment["start"])
                end = int(segment["end"])
                srt_lines.append(
                    f"{i+1}\n"
                    f"{start//3600:02}:{(start%3600)//60:02}:{start%60:02},000 --> "
                    f"{end//3600:02}:{(end%3600)//60:02}:{end%60:02},000\n"
                    f"{segment['text']}\n"
                )

            srt_text = "\n".join(srt_lines)

            # Save .srt file
            srt_path = os.path.join(temp_dir, f"{os.path.splitext(video_name)[0]}.srt")
            with open(srt_path, "w", encoding="utf-8") as srt_file:
                srt_file.write(srt_text)

            # Provide download link
            with open(srt_path, "rb") as srt_file:
                st.download_button(
                    label=f"⬇️ Download SRT for {video_name}",
                    data=srt_file,
                    file_name=os.path.basename(srt_path),
                    mime="text/plain"
                )
