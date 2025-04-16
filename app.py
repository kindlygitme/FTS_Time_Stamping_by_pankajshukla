import streamlit as st
import zipfile
import os
import tempfile
import re
import whisper
import pandas as pd

st.set_page_config(page_title="Question Timestamp Extractor", layout="centered")
st.title("📘 Extract Question Number Timestamps from Videos")
st.write("Please upload a ZIP file containing MP4 videos.")

uploaded_zip = st.file_uploader("Upload ZIP file", type=["zip"])

if uploaded_zip is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        video_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.lower().endswith((".mp4", ".mkv", ".avi"))]

        model = whisper.load_model("base")
        all_data = []

        for video_path in video_files:
            st.markdown("---")
            st.subheader(f"🎞️ {os.path.basename(video_path)}")

            st.info("🎙️ Transcribing...")
            result = model.transcribe(video_path, task="transcribe")

            # Show full transcript
            st.text_area("📝 Transcribed Text:", result["text"], height=250)

            # User input regex pattern
            user_regex = st.text_input(
                f"🔍 Enter your regex pattern (e.g., `(question|prashn).{{0,10}}(\\d{{1,3}})`)", 
                key=video_path
            )

            if user_regex:
                matches_found = 0
                for segment in result["segments"]:
                    match = re.search(user_regex, segment["text"], re.IGNORECASE)
                    if match:
                        try:
                            question_num = match.group(2)
                        except IndexError:
                            question_num = match.group(1)

                        start_time = int(segment["start"])
                        formatted_time = "{:02d}:{:02d}:{:02d}".format(
                            start_time // 3600, (start_time % 3600) // 60, start_time % 60
                        )
                        all_data.append({
                            "Video": os.path.basename(video_path),
                            "Question Number": question_num,
                            "Timestamp": formatted_time
                        })
                        matches_found += 1

                st.success(f"✅ {matches_found} matches found!")

        # Final output
        if all_data:
            df = pd.DataFrame(all_data)
            st.markdown("---")
            st.success("🎉 Timestamps extracted successfully!")
            st.dataframe(df)

            csv_path = os.path.join(temp_dir, "timestamps.csv")
            df.to_csv(csv_path, index=False)
            with open(csv_path, "rb") as f:
                st.download_button("⬇️ Download CSV", data=f, file_name="timestamps.csv", mime="text/csv")
        else:
            st.warning("❌ No matches found with the given regex.")
