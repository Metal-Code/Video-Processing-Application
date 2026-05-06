import streamlit as st
import os
import tempfile
import numpy as np
import cv2
from PIL import Image
import moviepy.editor as mp
import openai
import whisper

from compressor import compress_video

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Smart Video Suite", page_icon="🎥", layout="wide")

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    .stButton > button {
        width: 100% !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 24px;
        background-color: #132378;
        color: #ffffff;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #facc15;
        color: #111827;
        transform: scale(1.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Cached resources (loaded once per session) ────────────────────────────────
@st.cache_resource
def load_whisper_model():
    return whisper.load_model("base")


# ── OpenRouter setup ──────────────────────────────────────────────────────────
ai_available = "OPENROUTER_API_KEY" in st.secrets
openrouter_client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets.get("OPENROUTER_API_KEY", ""),
) if ai_available else None

# ── Sidebar tool selector ─────────────────────────────────────────────────────
TOOLS = [
    "Compress Video",
    "Generate Subtitles",
    "Video Overview",
    "Frame-by-Frame Viewer",
    "Trim Video",
    "Crop Video",
    "Add Filter",
    "Ask Questions About Video",
]

if "tool" not in st.session_state:
    st.session_state.tool = TOOLS[0]

with st.sidebar:
    st.markdown("## 🎬 Tools")
    for tool in TOOLS:
        if st.button(tool, key=f"btn_{tool}"):
            st.session_state.tool = tool
            # Clear cached transcript when switching tools so it isn't stale
            st.session_state.pop("video_transcript", None)
            st.session_state.pop("transcript_for_file", None)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🎥 Smart Video Compression and Editing Suite")
st.markdown("Style, analyze, and understand your video — all in one place.")

# ── File upload ───────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("📄 Upload your video", type=["mp4", "mov", "avi"])

if not uploaded_file:
    st.info("👈 Upload a video to get started")
    st.stop()

# Write upload to a temp file; track path in session so we only write once per upload
if st.session_state.get("uploaded_file_name") != uploaded_file.name:
    # New file — clean up any previous temp file
    old_path = st.session_state.get("temp_video_path")
    if old_path and os.path.exists(old_path):
        os.remove(old_path)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tmp.write(uploaded_file.read())
    tmp.close()
    st.session_state.temp_video_path = tmp.name
    st.session_state.uploaded_file_name = uploaded_file.name
    # Invalidate transcript when a new video is uploaded
    st.session_state.pop("video_transcript", None)
    st.session_state.pop("transcript_for_file", None)

temp_video_path: str = st.session_state.temp_video_path
filename = uploaded_file.name.rsplit(".", 1)[0]

# ── Tool dispatch ─────────────────────────────────────────────────────────────
tool = st.session_state.tool

# ── Compress Video ────────────────────────────────────────────────────────────
if tool == "Compress Video":
    st.subheader("📦 Compress Video")
    if st.button("▶ Compress"):
        compressed_path = temp_video_path.replace(".mp4", "_compressed.mp4")
        with st.spinner("Compressing…"):
            try:
                compress_video(temp_video_path, compressed_path)
                st.success("✅ Compression complete")
                st.video(compressed_path)
                with open(compressed_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Compressed Video",
                        f,
                        file_name=f"{filename}_compressed.mp4",
                    )
            except Exception as e:
                st.error(f"Compression failed: {e}")

# ── Generate Subtitles ────────────────────────────────────────────────────────
elif tool == "Generate Subtitles":
    st.subheader("📝 Subtitle Generator")
    language = st.selectbox(
        "Select language:", ["en", "hi", "es", "fr", "de", "zh"]
    )
    if st.button("▶ Generate"):
        with st.spinner("Transcribing…"):
            try:
                model = load_whisper_model()
                result = model.transcribe(temp_video_path, language=language)
                subtitle_text = result["text"]
                st.success("✅ Subtitles generated")
                st.text_area("Subtitles:", subtitle_text, height=300)
                st.download_button(
                    "⬇️ Download Subtitles",
                    subtitle_text,
                    file_name=f"{filename}_subtitles.txt",
                )
            except Exception as e:
                st.error(f"Subtitle generation failed: {e}")

# ── Video Overview ────────────────────────────────────────────────────────────
elif tool == "Video Overview":
    st.subheader("🧐 Video Summary")
    if not ai_available:
        st.warning("⚠️ OPENROUTER_API_KEY not found in secrets. Add it to enable this feature.")
        st.stop()

    st.info("Extracts audio transcript via Whisper, then summarises with OpenRouter.")
    if st.button("▶ Summarise"):
        with st.spinner("Transcribing…"):
            try:
                model = load_whisper_model()
                result = model.transcribe(temp_video_path)
                transcript = result["text"]
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

        with st.spinner("Summarising…"):
            try:
                response = openrouter_client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": f"Summarize this transcript:\n{transcript}"}],
                )
                st.success("✅ Summary generated")
                st.text_area("Summary:", response.choices[0].message.content, height=200)
            except Exception as e:
                st.error(f"Summarisation failed: {e}")

# ── Frame-by-Frame Viewer ─────────────────────────────────────────────────────
elif tool == "Frame-by-Frame Viewer":
    st.subheader("🎞️ Frame Viewer")
    cap = cv2.VideoCapture(temp_video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total < 1:
        st.error("Could not read frames from this video.")
        cap.release()
        st.stop()

    idx = st.slider("Select frame index", 0, total - 1, 0)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
    ret, frame = cap.read()
    cap.release()

    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        st.image(frame_rgb, caption=f"Frame {idx}", use_container_width=True)
    else:
        st.error("Failed to extract frame.")

# ── Trim Video ────────────────────────────────────────────────────────────────
elif tool == "Trim Video":
    st.subheader("✂️ Trim Video")
    st.video(temp_video_path)
    video = mp.VideoFileClip(temp_video_path)
    duration = int(video.duration)
    video.close()

    start_time = st.slider("Start time (seconds):", 0, duration - 1, 0)
    end_time = st.slider("End time (seconds):", start_time + 1, duration, duration)

    if st.button("▶ Trim"):
        trimmed_path = temp_video_path.replace(".mp4", "_trimmed.mp4")
        with st.spinner("Trimming…"):
            try:
                clip = mp.VideoFileClip(temp_video_path)
                trimmed = clip.subclip(start_time, end_time)
                trimmed.write_videofile(trimmed_path, codec="libx264", logger=None)
                clip.close()
                st.success("✅ Trim complete")
                st.video(trimmed_path)
                with open(trimmed_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Trimmed Video", f, file_name=f"{filename}_trimmed.mp4"
                    )
            except Exception as e:
                st.error(f"Trim failed: {e}")

# ── Crop Video ────────────────────────────────────────────────────────────────
elif tool == "Crop Video":
    st.subheader("🖼️ Crop Video")
    cap = cv2.VideoCapture(temp_video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        st.error("Could not read the first frame.")
        st.stop()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame_rgb)
    st.image(image, caption="First Frame (use as reference)", use_container_width=True)

    st.markdown("**Specify crop region (pixels):**")
    col1, col2 = st.columns(2)
    with col1:
        x1 = st.number_input("x1 (left)", value=0, min_value=0, max_value=image.width - 1)
        y1 = st.number_input("y1 (top)", value=0, min_value=0, max_value=image.height - 1)
    with col2:
        x2 = st.number_input("x2 (right)", value=image.width, min_value=1, max_value=image.width)
        y2 = st.number_input("y2 (bottom)", value=image.height, min_value=1, max_value=image.height)

    if st.button("▶ Crop"):
        if x1 >= x2 or y1 >= y2:
            st.error("Invalid crop region: x1 must be < x2 and y1 must be < y2.")
        else:
            cropped_path = temp_video_path.replace(".mp4", "_cropped.mp4")
            with st.spinner("Cropping…"):
                try:
                    clip = mp.VideoFileClip(temp_video_path)
                    cropped = clip.crop(x1=int(x1), y1=int(y1), x2=int(x2), y2=int(y2))
                    cropped.write_videofile(cropped_path, codec="libx264", logger=None)
                    clip.close()
                    st.success("✅ Crop complete")
                    st.video(cropped_path)
                    with open(cropped_path, "rb") as f:
                        st.download_button(
                            "⬇️ Download Cropped Video", f, file_name=f"{filename}_cropped.mp4"
                        )
                except Exception as e:
                    st.error(f"Crop failed: {e}")

# ── Add Filter ────────────────────────────────────────────────────────────────
elif tool == "Add Filter":
    st.subheader("🎨 Add Video Filter")
    filter_choice = st.selectbox(
        "Choose filter:", ["Grayscale", "Sepia", "Invert", "Brighten"]
    )

    if st.button("▶ Apply Filter"):
        filtered_path = temp_video_path.replace(".mp4", f"_{filter_choice.lower()}.mp4")
        with st.spinner(f"Applying {filter_choice} filter…"):
            try:
                clip = mp.VideoFileClip(temp_video_path)

                if filter_choice == "Grayscale":
                    clip = clip.fx(mp.vfx.blackwhite)
                elif filter_choice == "Invert":
                    clip = clip.fl_image(lambda f: (255 - f).astype(np.uint8))
                elif filter_choice == "Sepia":
                    sepia_matrix = np.array([
                        [0.393, 0.769, 0.189],
                        [0.349, 0.686, 0.168],
                        [0.272, 0.534, 0.131],
                    ])
                    clip = clip.fl_image(
                        lambda f: np.clip(f.dot(sepia_matrix.T), 0, 255).astype(np.uint8)
                    )
                elif filter_choice == "Brighten":
                    clip = clip.fl_image(
                        lambda f: np.clip(f * 1.2, 0, 255).astype(np.uint8)
                    )

                clip.write_videofile(filtered_path, codec="libx264", logger=None)
                clip.close()
                st.success("✅ Filter applied")
                st.video(filtered_path)
                with open(filtered_path, "rb") as f:
                    st.download_button(
                        "⬇️ Download Filtered Video",
                        f,
                        file_name=f"{filename}_{filter_choice.lower()}.mp4",
                    )
            except Exception as e:
                st.error(f"Filter failed: {e}")

# ── Ask Questions About Video ─────────────────────────────────────────────────
elif tool == "Ask Questions About Video":
    st.subheader("💬 Ask Questions About Video")

    if not ai_available:
        st.warning("⚠️ OPENROUTER_API_KEY not found in secrets. Add it to enable this feature.")
        st.stop()

    # Only re-transcribe if it's a new video
    if st.session_state.get("transcript_for_file") != uploaded_file.name:
        st.info("Extracting transcript — this may take a moment on first load.")
        with st.spinner("Transcribing…"):
            try:
                model = load_whisper_model()
                result = model.transcribe(temp_video_path)
                st.session_state.video_transcript = result["text"]
                st.session_state.transcript_for_file = uploaded_file.name
                st.success("✅ Transcript ready.")
            except Exception as e:
                st.error(f"Transcription failed: {e}")
                st.stop()

    transcript = st.session_state.video_transcript
    user_question = st.text_input("Ask a question about the video:")

    if user_question:
        with st.spinner("Thinking…"):
            try:
                response = openrouter_client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": (
                        f"Answer the following question based on the video transcript.\n"
                        f"Question: {user_question}\nTranscript:\n{transcript}"
                    )}],
                )
                st.success("✅ Answer ready")
                st.text_area("Answer:", response.choices[0].message.content, height=150)
            except Exception as e:
                st.error(f"Answer generation failed: {e}")

st.markdown("---")