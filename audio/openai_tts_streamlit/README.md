# Advanced OpenAI Text-to-Speech Streamlit Interface

A comprehensive web interface for OpenAI's Text-to-Speech (TTS) API, featuring both traditional file generation and modern streaming capabilities.

## ✨ Features

### 🎵 Dual Generation Modes
- **File Generation**: Traditional mode that creates downloadable audio files
- **Streaming Playback**: Modern mode with immediate audio playback as it's generated

### 🔧 Comprehensive Configuration
- **3 TTS Models**: `gpt-4o-mini-tts` (latest), `tts-1`, `tts-1-hd`
- **10 Unique Voices**: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer
- **6 Audio Formats**: MP3, Opus, AAC, FLAC, WAV, PCM
- **Instructions Support**: Custom tone and style instructions for `gpt-4o-mini-tts`

### 🎨 Enhanced User Experience
- Clean, modern interface with sidebar configuration
- Real-time text statistics (word/character count)
- Generation time tracking
- Comprehensive error handling
- Usage statistics and file management

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd audio/openai_tts_streamlit
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or using uv:
   ```bash
   uv sync
   ```

3. **Set up your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## 📋 Usage

### File Generation Mode
1. Select "File Generation" in the sidebar
2. Configure your preferences (model, voice, format)
3. Enter your text
4. Click "🎵 Generate Audio File"
5. Listen to the audio and download the file

### Streaming Mode
1. Select "Streaming Playback" in the sidebar
2. Configure your preferences
3. Enter your text
4. Click "▶️ Stream Audio"
5. Audio plays immediately as it's generated

### Advanced Features
- **Instructions**: Use custom instructions with `gpt-4o-mini-tts` for specific tone or style
- **Format Selection**: Choose the best format for your use case
- **Automatic Caching**: Files are cached to avoid regenerating identical requests

## 🏗️ Architecture

The application is built with a clean separation of concerns:

### `tts_service.py` - Backend Service
- **TTSService**: Main service class handling OpenAI API interactions
- **TTSConfig**: Configuration dataclass for TTS parameters
- **Async Support**: Built-in support for both sync and async operations
- **Error Handling**: Comprehensive error handling and validation

### `app.py` - Streamlit Frontend
- **Modern UI**: Clean, responsive interface with sidebar configuration
- **Dual Modes**: Support for both file generation and streaming
- **Real-time Feedback**: Progress indicators and generation timing
- **File Management**: Automatic file organization and statistics

## 🔍 Generation Mode Comparison

| Feature | File Generation | Streaming Playback |
|---------|----------------|-------------------|
| **Latency** | Higher (wait for complete file) | Lower (immediate playback) |
| **File Storage** | ✅ Creates permanent files | ⚡ Optional download |
| **Use Case** | Batch processing, downloads | Real-time, interactive |
| **Complexity** | Simple implementation | Advanced async handling |
| **Memory Usage** | Stores complete file | Streams in chunks |

## 🛠️ Technical Details

### Dependencies
- **streamlit**: Web interface framework
- **openai**: Official OpenAI Python client with async support
- **python-dotenv**: Environment variable management
- **asyncio-compat**: Enhanced async compatibility

### Audio Formats
- **MP3**: Default, widely compatible
- **Opus**: Low latency, ideal for streaming
- **AAC**: Mobile-friendly, good compression
- **FLAC**: Lossless, high quality
- **WAV/PCM**: Raw audio, lowest latency

### Models
- **gpt-4o-mini-tts**: Latest model with instruction support
- **tts-1**: Fast generation, good quality
- **tts-1-hd**: High-definition audio quality

## 📝 Configuration Options

### Environment Variables
```bash
OPENAI_API_KEY=your-api-key-here  # Required
```

### Streamlit Configuration
The app automatically configures Streamlit with:
- Wide layout for better space utilization
- Expanded sidebar for easy access to controls
- Custom page title and icon

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the AI-Hub repository. Please refer to the main repository license.

## 🆘 Troubleshooting

### Common Issues

**"Failed to initialize OpenAI client"**
- Ensure `OPENAI_API_KEY` is set in your environment
- Verify your API key is valid and has TTS permissions

**"Audio generation failed"**
- Check your internet connection
- Verify your OpenAI account has sufficient credits
- Try a shorter text input

**"Streaming audio not working"**
- Ensure your browser supports audio playback
- Try switching to File Generation mode
- Check browser console for errors

### Performance Tips
- Use MP3 format for best compatibility
- Use Opus format for lowest latency streaming
- Keep text under 4096 characters for optimal performance
- Use `gpt-4o-mini-tts` for best quality and features

## 🔗 Related Projects

- [OpenAI STT Streamlit](../openai_stt_streamlit/) - Speech-to-Text interface
- [AI-Hub](../../) - Main repository with more AI tools

---

**Built with ❤️ using Streamlit and OpenAI**
