import streamlit as st
import zipfile
import os
import tempfile
import re
import whisper
import pandas as pd

st.set_page_config(page_title="Question Timestamp Extractor", layout="centered")
st.title("📘 वीडियो से प्रश्न नंबर के टाइमस्टैम्प निकालो")
st.write("कृपया एक ZIP फाइल अपलोड करें जिसमें MP4 वीडियो हों।")

uploaded_zip = st.file_uploader("ZIP फाइल अपलोड करें", type=["zip"])

if uploaded_zip is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "uploaded.zip")
        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        video_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.lower().endswith((".mp4", ".mkv", ".avi"))]

        all_data = []
        model = whisper.load_model("base")

        for video_path in video_files:
            st.write(f"🔍 प्रोसेस कर रहे हैं: `{os.path.basename(video_path)}`")

            result = model.transcribe(video_path, task="transcribe")

            for segment in result["segments"]:
                text = segment["text"]
                match = re.search(r"(question number|question|next question)\s*(\d{1,3})", text, re.IGNORECASE)
                if match:
                    question_num = match.group(2)
                    start_time = int(segment["start"])
                    formatted_time = "{:02d}:{:02d}:{:02d}".format(
                        start_time // 3600, (start_time % 3600) // 60, start_time % 60
                    )
                    all_data.append({
                        "वीडियो": os.path.basename(video_path),
                        "प्रश्न नंबर": question_num,
                        "टाइमस्टैम्प": formatted_time
                    })

        if all_data:
            df = pd.DataFrame(all_data)
            st.success("🎉 टाइमस्टैम्प निकाल लिए गए!")
            st.dataframe(df)

            csv_path = os.path.join(temp_dir, "timestamps.csv")
            df.to_csv(csv_path, index=False)
            with open(csv_path, "rb") as f:
                st.download_button("⬇️ CSV डाउनलोड करें", data=f, file_name="timestamps.csv", mime="text/csv")
        else:
            st.warning("❌ कोई प्रश्न नंबर नहीं मिला।")
