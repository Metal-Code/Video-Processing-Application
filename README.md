# Smart Video Compression and Editing Suite

A comprehensive video processing platform that combines advanced compression algorithms with intelligent editing capabilities. This suite provides robust video editing and compression tools, allowing users to efficiently compress videos while preserving quality and apply various video processing features including cropping, trimming, filtering, and automated subtitle generation.

The platform leverages cutting-edge Python libraries including FFmpeg, Whisper, and MoviePy to deliver a seamless and professional video processing experience.

## Key Features

**Core Video Processing**
- Advanced video compression with up to 50% size reduction while maintaining quality
- Precision video trimming based on specified time intervals
- Flexible video cropping for custom aspect ratios and regions
- Professional-grade filter application including grayscale, sepia, invert, and brightness adjustments

**AI-Powered Capabilities**
- Automated subtitle generation with multi-language support using speech recognition
- Intelligent video summarization and content analysis
- Interactive video content querying through AI-powered transcript analysis
- Frame-by-frame video analysis for detailed inspection

## Technical Architecture

**Core Technologies**
- **Python**: Primary development language providing robust backend processing
- **FFmpeg**: Industry-standard multimedia framework for video compression and editing
- **Whisper**: OpenAI's automatic speech recognition system for transcription services
- **MoviePy**: Comprehensive video processing library for editing operations
- **Google Gemini AI**: Advanced AI integration for video analysis and summarization
- **Streamlit**: Web application framework for user interface deployment

## Installation and Setup

### Prerequisites
Ensure you have Python 3.8 or higher installed on your system.

### Repository Setup
```bash
git clone https://github.com/Metal-Code/Video-Processing-Application.git
cd Video-Processing-Application
```

### Dependency Installation
Install required Python packages:
```bash
pip install -r requirements.txt
```

### FFmpeg Installation

**Ubuntu/Debian Systems:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download the official FFmpeg executable from https://ffmpeg.org/download.html and ensure it is added to your system PATH.

## Usage Instructions

### Application Launch
Start the application using Streamlit:
```bash
streamlit run app.py
```

Alternatively, access the deployed version at: https://vidcompsuite.streamlit.app

### Workflow Process

1. **Video Upload**: Upload video files in supported formats (MP4, MOV, AVI) through the web interface

2. **Processing Selection**: Choose from available processing options:
   - Video compression with quality preservation
   - Automated subtitle generation and transcription
   - Video trimming to specified durations
   - Custom video cropping and region selection
   - Visual filter application and effects
   - AI-powered video content summarization
   - Interactive content querying and analysis

3. **Processing Execution**: The system processes the video using optimized algorithms and AI models

4. **Output Delivery**: Download processed videos, generated subtitles, or analysis reports

## Compression Algorithm Details

The video compression system implements sophisticated algorithms to achieve optimal file size reduction while maintaining visual quality:

**Technical Implementation:**
- Utilizes FFmpeg's advanced compression capabilities with optimized bitrate management
- Targets 50% file size reduction through intelligent quality-size trade-offs
- Employs H.264 (libx264) video encoding for broad compatibility
- Implements AAC audio compression for optimal audio-video synchronization
- Maintains original video resolution and frame rate where possible

**Quality Assurance:**
- Dynamic bitrate adjustment based on content complexity
- Quality metrics evaluation during compression process
- Compatibility testing across multiple playback platforms

For detailed implementation specifics, refer to the `compress_video` function within the `compressor.py` module.

## System Requirements

**Minimum Specifications:**
- Python 3.8 or higher
- 4GB RAM (8GB recommended for large video files)
- 2GB available storage space
- Internet connection for AI-powered features

**Supported Video Formats:**
- Input: MP4, MOV, AVI, MKV
- Output: MP4 (optimized for compatibility)

## Contributing Guidelines

We welcome contributions from the development community. To contribute:

1. Fork the repository and create a feature branch
2. Implement changes with appropriate documentation
3. Ensure all tests pass and add new tests for new features
4. Submit a pull request with detailed description of changes
5. Follow existing code style and documentation standards

## License and Acknowledgments

**Technology Credits:**
- **FFmpeg Project**: Leading multimedia processing framework
- **OpenAI Whisper**: State-of-the-art automatic speech recognition
- **Google Gemini**: Advanced AI capabilities for content analysis
- **MoviePy**: Comprehensive Python video editing library

## Support and Documentation

For technical support, feature requests, or bug reports, please create an issue in the project repository. Detailed documentation and API references are available in the `/docs` directory.

**Project Status**: Active Development  
**Latest Version**: 1.0.0  
**Maintenance**: Regular updates and security patches
