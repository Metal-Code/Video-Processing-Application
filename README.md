

# 🎬 Smart Video Compression and Editing Suite

This project provides a robust suite of video editing and compression tools, allowing you to efficiently compress videos while preserving quality, and apply various video editing features like cropping, trimming, adding filters, and generating subtitles. The entire suite is powered by Python libraries such as **FFmpeg**, **Whisper**, and **MoviePy**, offering a seamless user experience for video processing.

---

## 🚀 Features

- **Video Compression**: Reduce video file size by up to 50% while maintaining quality.
- **Trim Video**: Cut your video to a specific duration based on start and end time.
- **Crop Video**: Crop a video to your desired region.
- **Add Filters**: Apply various video filters like grayscale, sepia, invert, and brightness adjustments.
- **Generate Subtitles**: Automatically transcribe and generate subtitles for your videos in multiple languages.
- **Video Overview**: Get a summary of your video using AI.
- **Frame-by-Frame Viewer**: View videos frame-by-frame for detailed analysis.
- **Ask Questions About Video**: Interact with your video content by asking AI-based questions about the video transcript.

---

## 🔧 Technologies Used

- **Python**: The core language for this project.
- **FFmpeg**: For video compression and editing.
- **Whisper**: For automatic speech recognition to generate subtitles.
- **MoviePy**: For video processing, including trimming, cropping, and adding filters.
- **Google Gemini AI**: For video summarization and question-answering.

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/smart-video-compression-editing.git
cd smart-video-compression-editing
```

### 2. Install Dependencies

You can install the required dependencies using **pip**:

```bash
pip install -r requirements.txt
```

### 3. Install FFmpeg

**FFmpeg** is required for video compression and editing. You can install it as follows:

#### On Ubuntu:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### On macOS (using Homebrew):
```bash
brew install ffmpeg
```

#### On Windows:
Download the FFmpeg executable from the [official site](https://ffmpeg.org/download.html) and add it to your PATH.

---

## 📹 How to Use

1. **Run the Application**:
   - The app can be run directly using Streamlit for an easy-to-use interface.
   
   ```bash
   streamlit run app.py
   ```
   OR
   go to https://vidcompsuite.streamlit.app

3. **Upload Your Video**:
   - Choose a video file in **.mp4**, **.mov**, or **.avi** format and upload it through the app interface.

4. **Choose an Action**:
   - Select from available tools like:
     - **Compress Video**: Automatically reduce the video size.
     - **Generate Subtitles**: Transcribe your video and generate subtitles.
     - **Trim Video**: Trim the video to a specific section.
     - **Crop Video**: Crop a specific area of the video.
     - **Add Filter**: Apply visual effects to your video.
     - **Video Overview**: Get an AI-powered summary of your video.
     - **Ask Questions About Video**: Ask AI-based questions about the content.

5. **Download**:
   - Once the video processing is complete, you can download the modified video or subtitles.

---

## 📈 Compression Logic

The video compression feature reduces the file size by approximately 50% while maintaining a good balance of quality. The compression works as follows:

- The **FFmpeg** tool is used to compress the video by adjusting the bitrate and quality settings.
- The target size for the compressed video is set to 50% of the original size.
- The compression process also ensures the video is encoded with the **libx264** codec and the audio with the **AAC** codec for optimal compatibility.

For detailed information, refer to the `compress_video` function in the `compressor.py` file.

---

## 🤝 Contributing

We welcome contributions! If you have suggestions or bug fixes, feel free to open an issue or submit a pull request.

---

## 📜 Acknowledgements

- **FFmpeg**: The leading multimedia framework for video compression and editing.
- **Whisper**: OpenAI’s ASR system for transcription.
- **Google Gemini**: For advanced AI-powered video summarization and question-answering.
  
