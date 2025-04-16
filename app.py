import streamlit as st
import zipfile
import os
import tempfile
import re
import whisper
import pandas as pd

st.set_page_config(page_title="Video Question Timestamp Extractor", layout="centered")
st.title("🎬 Extract Timestamps from Video Subtitles using Regex")
st.write("Upload a ZIP file containing MP4/MKV/AVI videos. We’ll generate subtitles and extract timestamps based on a regex pattern.")

uploaded_zip = st.file_uploader("📁 Upload a ZIP file", type=["zip"])

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
        all_data = []

        # Preset regex patterns
        regex_presets = {
            "🧠 Default: question/prashn followed by number": r"(question|next|prashn)[^\d]{0,10}(\d{1,3})",
            "🔤 English only (question number 12)": r"(question number|next question)\s*(\d{1,3})",
            "🈶 Hindi only (prashn number 12)": r"(prashn|sawaal).{0,10}(\d{1,3})"
        }

        selected_preset = st.selectbox("🧩 Choose a regex pattern preset:", list(regex_presets.keys()))
        custom_regex = st.text_input("Or enter your custom regex pattern (overrides preset):", "")

        final_regex = custom_regex if custom_regex else regex_presets[selected_preset]

        for video_path in video_files:
            st.markdown("---")
            st.subheader(f"📹 File: {os.path.basename(video_path)}")

            st.info("⏳ Generating transcript using Whisper...")
            result = model.trans
