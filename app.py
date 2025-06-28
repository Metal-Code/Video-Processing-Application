import streamlit as st
import os
import tempfile
import cv2
from PIL import Image
import numpy as np

# Try importing optional dependencies
try:
    import moviepy.editor as mp
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    st.warning("MoviePy not available. Some features will be disabled.")

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

try:
    from compressor import compress_video
    COMPRESSOR_AVAILABLE = True
except ImportError:
    COMPRESSOR_AVAILABLE = False
    st.warning("Compressor module not available.")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
    }
    .toolbar {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        margin-top: 1rem;
    }
    .tool-button {
        width: 200px;
        padding: 12px 20px;
        background-color: #132378;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-size: 15px;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    }
    .tool-button:hover {
        background-color: #facc15;
        color: #111827;
        transform: scale(1.02);
    }
    .selected-button {
        background-color: #ffffff !important;
        color: #030549 !important;
        box-shadow: 0 0 12px rgba(249, 115, 22, 0.6);
    }
    .stButton > button {
        width: 100% !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: bold;
        border-radius: 10px;
        padding: 10px 24px;
        background-color: #000000;
        color: #ffffff;
        border: #ffffff;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #ffffff;
        transform: scale(1.04);
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🎥 Smart Video Processing Suite")
st.markdown("Process and analyze your videos with ease.")

# Initialize Gemini API if key is available
if GENAI_AVAILABLE and "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.warning("Gemini API configuration failed. AI features may not work.")

# Define available tools based on dependencies
tools = ["Frame-by-Frame Viewer"]

if COMPRESSOR_AVAILABLE:
    tools.insert(0, "Compress Video")

if MOVIEPY_AVAILABLE:
    tools.extend(["Trim Video", "Add Filter"])

if "tool" not in st.session_state:
    st.session_state.tool = tools[0]

with st.sidebar:
    st.markdown('<div class="toolbar">', unsafe_allow_html=True)
    for tool in tools:
        btn_class = "tool-button selected-button" if tool == st.session_state.tool else "tool-button"
        if st.button(f"{tool}", key=tool):
            st.session_state.tool = tool
    st.markdown('</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📄 Upload your video", type=["mp4", "mov", "avi"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_file.read())
        temp_video_path = temp_video.name

    filename = uploaded_file.name.rsplit(".", 1)[0]

    tool = st.session_state.tool
    
    if tool == "Compress Video" and COMPRESSOR_AVAILABLE:
        st.subheader("📦 Compressing your video")
        with st.spinner("Compressing video..."):
            compressed_path = temp_video_path.replace(".mp4", "_compressed.mp4")
            try:
                compress_video(temp_video_path, compressed_path)
                if os.path.exists(compressed_path):
                    st.success("✅ Compression complete")
                    st.video(compressed_path)
                    with open(compressed_path, "rb") as f:
                        st.download_button("⬇️ Download Compressed Video", f, file_name=filename + "_compressed.mp4")
                else:
                    st.error("Compression failed: Output file not created.")
            except Exception as e:
                st.error(f"Compression failed: {str(e)}")

    elif tool == "Frame-by-Frame Viewer":
        st.subheader("🧡 Frame Viewer")
        try:
            cap = cv2.VideoCapture(temp_video_path)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total > 0:
                idx = st.slider("Select frame index", 0, total - 1, 0)
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    st.image(frame, caption=f"Frame {idx}", use_column_width=True)
                else:
                    st.error("Failed to extract frame.")
            else:
                st.error("Could not read video file.")
            cap.release()
        except Exception as e:
            st.error(f"Frame extraction failed: {e}")

    elif tool == "Trim Video" and MOVIEPY_AVAILABLE:
        st.subheader("✂️ Trim Video")
        try:
            video = mp.VideoFileClip(temp_video_path)
            st.video(temp_video_path)
            max_duration = max(1, int(video.duration))
            start_time = st.slider("Start time (seconds):", 0, max_duration - 1, 0)
            end_time = st.slider("End time (seconds):", start_time + 1, max_duration, max_duration)
            
            if st.button("Trim"):
                trimmed_path = temp_video_path.replace(".mp4", "_trimmed.mp4")
                with st.spinner("Trimming video..."):
                    trimmed = video.subclip(start_time, end_time)
                    trimmed.write_videofile(trimmed_path, codec="libx264", audio_codec="aac")
                    trimmed.close()
                    st.success("✅ Trim complete")
                    st.video(trimmed_path)
                    with open(trimmed_path, "rb") as f:
                        st.download_button("⬇️ Download Trimmed Video", f, file_name=filename + "_trimmed.mp4")
            video.close()
        except Exception as e:
            st.error(f"Video trimming failed: {e}")

    elif tool == "Add Filter" and MOVIEPY_AVAILABLE:
        st.subheader("🎰 Add Video Filter")
        filter_choice = st.selectbox("Choose filter:", ["Grayscale", "Invert", "Brighten"])
        
        if st.button("Apply Filter"):
            filtered_path = temp_video_path.replace(".mp4", f"_{filter_choice.lower()}.mp4")
            try:
                with st.spinner(f"Applying {filter_choice} filter..."):
                    clip = mp.VideoFileClip(temp_video_path)
                    
                    if filter_choice == "Grayscale":
                        clip = clip.fx(mp.vfx.blackwhite)
                    elif filter_choice == "Invert":
                        clip = clip.fl_image(lambda f: 255 - f)
                    elif filter_choice == "Brighten":
                        clip = clip.fl_image(lambda f: np.clip(f * 1.2, 0, 255))

                    clip.write_videofile(filtered_path, codec="libx264", audio_codec="aac")
                    clip.close()
                    st.success("✅ Filter applied")
                    st.video(filtered_path)
                    with open(filtered_path, "rb") as f:
                        st.download_button("⬇️ Download Filtered Video", f, file_name=filename + f"_{filter_choice.lower()}.mp4")
            except Exception as e:
                st.error(f"Filter application failed: {e}")
                
    # Clean up temporary files
    try:
        if os.path.exists(temp_video_path):
            os.unlink(temp_video_path)
    except:
        pass
else:
    st.info("👈 Upload a video to get started")
    
    # Show available features
    st.markdown("### Available Features:")
    feature_status = []
    feature_status.append("✅ Frame-by-Frame Viewer")
    
    if COMPRESSOR_AVAILABLE:
        feature_status.append("✅ Video Compression")
    else:
        feature_status.append("❌ Video Compression (compressor.py missing)")
        
    if MOVIEPY_AVAILABLE:
        feature_status.append("✅ Video Trimming")
        feature_status.append("✅ Video Filters")
    else:
        feature_status.append("❌ Video Trimming (MoviePy not available)")
        feature_status.append("❌ Video Filters (MoviePy not available)")
    
    for status in feature_status:
        st.markdown(status)

st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
