# Media Content Summarizer

A Streamlit application that takes video or audio input, transcribes it, and generates a detailed summary using Google's Gemini AI.

## Features

- Supports video (mp4, avi) and audio (mp3, wav) files
- Extracts audio from video files
- Transcribes speech to text using Google Speech Recognition
- Generates comprehensive summaries using Google Gemini AI
- Clean and intuitive user interface

## Setup

1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open your web browser and navigate to the provided URL (typically http://localhost:8501)
3. Upload a video or audio file using the file uploader
4. Wait for the processing to complete
5. View the transcription and generated summary

## Requirements

- Python 3.8+
- FFmpeg (for audio processing)
- Google API key with access to Gemini API

## Note

The application uses temporary files for processing but automatically cleans them up after use. Make sure you have sufficient disk space available for processing large media files. 