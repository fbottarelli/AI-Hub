# Personal Multi-Utility Hub

A Gradio-based web application that provides various utility tools. Currently includes:

## Features & TODO Lists

### 1. YouTube Utilities
Current Features:
- Download videos in MP4 format
- Extract audio in MP3 format
- Download subtitles (if available)
- Generate AI-powered video summaries using title and description

TODO:
- [ ] Migrate to Cobalt API for better Raspberry Pi compatibility: https://github.com/imputnet/cobalt/blob/main/docs/run-an-instance.md
  - [ ] Implement video download endpoint
  - [ ] Implement audio extraction endpoint
  - [ ] Add quality selection options
  - [ ] Handle rate limiting and errors
- [ ] Add playlist download support
- [ ] Implement download queue system
- [ ] Add progress tracking
- [ ] Create download history

### 2. File Management (Planned)
TODO:
- [ ] Basic file operations (upload, delete, rename)
- [ ] File compression/decompression
- [ ] Batch file processing
- [ ] File conversion utilities
- [ ] Media file optimization

### 3. System Monitoring (Planned)
TODO:
- [ ] CPU usage tracking
- [ ] Memory usage monitoring
- [ ] Disk space analysis
- [ ] Network usage statistics
- [ ] Temperature monitoring (Raspberry Pi specific)
- [ ] System logs viewer

### 2. GitHub Repository Analysis
Current Features:
- Analyze GitHub repositories
- View repository structure and content
- Generate AI-powered summaries
- Copy analysis results to clipboard
- Export analysis to markdown files

TODO:
- [ ] Add support for private repositories
- [ ] Implement diff analysis between commits
- [ ] Add code quality metrics
- [ ] Enable custom analysis templates

## Setup

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

## Requirements
- Python 3.8+
- FFmpeg (for audio extraction)
- OpenAI API key (for summarization feature)

## Coming Soon
- More utility tools and features
- Additional AI-powered functionalities
- Enhanced user interface 