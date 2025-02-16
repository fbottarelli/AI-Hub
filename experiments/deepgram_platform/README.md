# Deepgram Speech Platform

A Gradio web application that demonstrates Deepgram's Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities.

## Features

- Speech-to-Text conversion using Deepgram's Nova model
- Text-to-Speech synthesis using Deepgram's Aura-Asteria model
- Simple and intuitive web interface
- Secure API key input

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Get your Deepgram API key:
   - Sign up at [Deepgram Console](https://console.deepgram.com)
   - Create a new API key

3. Run the application:
```bash
python app.py
```

## Usage

1. When the app starts, open the provided URL in your web browser
2. Enter your Deepgram API key in the designated field and click "Initialize Client"
3. For Speech-to-Text:
   - Upload an audio file using the audio input component
   - The transcription will appear automatically
4. For Text-to-Speech:
   - Enter your text in the text input field
   - Press Enter or click submit to generate speech
   - The generated audio will appear in the audio output component

## Notes

- The app supports common audio formats for STT
- For best results, use clear audio recordings
- The TTS feature uses Deepgram's Nova voice 