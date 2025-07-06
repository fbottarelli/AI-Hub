import streamlit as st
import os
import time
import threading
from pathlib import Path
import dotenv
from tts_service import TTSService, TTSConfig, run_async_in_sync

# Load environment variables
dotenv.load_dotenv()

# --- Configuration ---
OUTPUT_DIR = Path(__file__).parent / "audio_outputs"

# --- Page Configuration ---
st.set_page_config(
    page_title="OpenAI TTS Interface",
    page_icon="🔊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize TTS Service ---
@st.cache_resource
def get_tts_service():
    """Initialize and cache the TTS service"""
    try:
        return TTSService(OUTPUT_DIR)
    except Exception as e:
        st.error(f"Failed to initialize TTS service: {e}")
        if "OPENAI_API_KEY" not in os.environ:
            st.error("Please set the OPENAI_API_KEY environment variable.")
        st.stop()

tts_service = get_tts_service()

# --- Header ---
st.title("🔊 Advanced OpenAI Text-to-Speech Interface")
st.markdown("Turn text into lifelike spoken audio using OpenAI's TTS models with both file generation and streaming options.")
st.info("ℹ️ **Disclosure:** The TTS voice is AI-generated and complies with OpenAI's usage policies.")

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Generation Mode
    generation_mode = st.radio(
        "Generation Mode",
        ["File Generation", "True Streaming"],
        help="File Generation: Creates complete audio files. True Streaming: Plays audio as it's being generated."
    )
    
    st.divider()
    
    # Model Selection
    model = st.selectbox(
        "Model",
        tts_service.get_available_models(),
        index=0,
        help="gpt-4o-mini-tts: Latest model with instruction support. tts-1: Fast. tts-1-hd: High quality."
    )
    
    # Voice Selection
    voice = st.selectbox(
        "Voice",
        tts_service.get_available_voices(),
        index=3,  # Default to 'coral'
        help="Choose from 10 different AI voices with unique characteristics."
    )
    
    # Output Format
    output_format = st.selectbox(
        "Output Format",
        tts_service.get_available_formats(),
        index=0,  # Default to 'mp3'
        help="MP3: Default. Opus: Low latency. AAC: Mobile-friendly. FLAC: Lossless. WAV/PCM: Raw audio."
    )
    
    # Instructions (only for supported models)
    instructions = ""
    if tts_service.supports_instructions(model):
        instructions = st.text_input(
            "Instructions (Optional)",
            placeholder="e.g., Speak in a cheerful and positive tone",
            help="Provide specific instructions for tone, speed, or style."
        )
    else:
        st.info(f"Instructions are only supported by gpt-4o-mini-tts model.")

# --- Main Content ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Input Text")
    input_text = st.text_area(
        "Enter text to synthesize:",
        height=200,
        value="Today is a wonderful day to build something people love!",
        help="Enter the text you want to convert to speech. Longer texts may take more time to generate."
    )
    
    # Text statistics
    if input_text:
        word_count = len(input_text.split())
        char_count = len(input_text)
        st.caption(f"📊 {word_count} words, {char_count} characters")

with col2:
    st.subheader("🎵 Audio Output")
    
    # Generation buttons
    if generation_mode == "File Generation":
        generate_button = st.button(
            "🎵 Generate Audio File",
            type="primary",
            use_container_width=True,
            help="Generate complete audio file first, then play"
        )
    else:
        generate_button = st.button(
            "▶️ Stream Audio Now",
            type="primary",
            use_container_width=True,
            help="Start playing audio as soon as it begins generating"
        )
    
    # Audio output area
    audio_placeholder = st.empty()
    download_placeholder = st.empty()
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

# --- Generation Logic ---
if generate_button and input_text.strip():
    # Create TTS configuration
    config = TTSConfig(
        model=model,
        voice=voice,
        input_text=input_text.strip(),
        instructions=instructions if instructions else None,
        response_format=output_format
    )
    
    try:
        if generation_mode == "File Generation":
            # Traditional file-based generation
            with st.spinner("🎵 Generating complete audio file... Please wait."):
                start_time = time.time()
                
                # Generate speech file
                file_path = tts_service.generate_speech_file(config)
                
                generation_time = time.time() - start_time
                
                # Display audio player
                audio_placeholder.audio(str(file_path), format=f'audio/{output_format}')
                
                # Provide download link
                with open(file_path, "rb") as f:
                    download_placeholder.download_button(
                        label=f"📥 Download {file_path.name}",
                        data=f,
                        file_name=file_path.name,
                        mime=f'audio/{output_format}',
                        use_container_width=True
                    )
                
                status_placeholder.success(f"✅ Audio generated successfully in {generation_time:.2f}s!")
        
        else:
            # True streaming generation
            status_placeholder.info("🎵 Starting audio stream... Audio will play as soon as it's ready!")
            
            start_time = time.time()
            
            # Create temporary streaming file
            temp_path, stream_thread = tts_service.create_temp_streaming_file(config)
            
            # Give the streaming a moment to start
            time.sleep(0.5)
            
            # Show progress
            progress_bar = progress_placeholder.progress(0)
            progress_text = st.empty()
            
            # Monitor the file as it's being written
            initial_size = 0
            max_wait_time = 30  # Maximum wait time in seconds
            check_interval = 0.1  # Check every 100ms
            
            for i in range(int(max_wait_time / check_interval)):
                if temp_path.exists():
                    current_size = temp_path.stat().st_size
                    
                    if current_size > initial_size:
                        # File is growing, show audio player
                        if current_size > 1024:  # Wait for at least 1KB
                            audio_placeholder.audio(str(temp_path), format=f'audio/{output_format}')
                            
                            # Update progress based on file size growth
                            progress = min(i / (max_wait_time / check_interval * 0.8), 1.0)
                            progress_bar.progress(progress)
                            progress_text.text(f"Streaming... {current_size:,} bytes received")
                            
                            break
                    
                    initial_size = current_size
                
                time.sleep(check_interval)
            
            # Wait for thread to complete or timeout
            stream_thread.join(timeout=max_wait_time)
            
            generation_time = time.time() - start_time
            
            # Clear progress indicators
            progress_placeholder.empty()
            
            if temp_path.exists() and temp_path.stat().st_size > 0:
                # Ensure final audio player is shown
                audio_placeholder.audio(str(temp_path), format=f'audio/{output_format}')
                
                # Provide download option
                with open(temp_path, "rb") as f:
                    download_placeholder.download_button(
                        label=f"📥 Download Streamed Audio",
                        data=f,
                        file_name=f"streamed_{config.voice}_{config.model}.{config.response_format}",
                        mime=f'audio/{output_format}',
                        use_container_width=True
                    )
                
                status_placeholder.success(f"✅ Audio streamed successfully in {generation_time:.2f}s!")
                
                # Clean up temporary file after a delay (optional)
                def cleanup_temp_file():
                    time.sleep(60)  # Keep for 1 minute
                    try:
                        temp_path.unlink()
                    except:
                        pass
                
                cleanup_thread = threading.Thread(target=cleanup_temp_file)
                cleanup_thread.daemon = True
                cleanup_thread.start()
            else:
                status_placeholder.error("❌ Streaming failed - no audio data received")
    
    except Exception as e:
        status_placeholder.error(f"❌ An error occurred: {e}")
        st.error("Please check your API key, input text, and selected options.")

elif generate_button and not input_text.strip():
    status_placeholder.warning("⚠️ Please enter some text to synthesize.")

# --- Additional Information ---
st.markdown("---")

# Mode comparison
with st.expander("ℹ️ Generation Mode Comparison"):
    st.markdown("""
    **File Generation Mode:**
    - ✅ Creates complete downloadable audio files
    - ✅ Better for permanent storage
    - ✅ Guaranteed complete audio
    - ⏱️ Higher latency - must wait for complete generation
    - 🔄 Traditional approach
    
    **True Streaming Mode:**
    - ⚡ **Immediate playback** - audio starts as soon as first chunks arrive
    - ✅ **Lower perceived latency** - no waiting for complete file
    - ✅ More responsive and interactive experience
    - 🎯 Better for real-time applications
    - 🚀 Modern streaming approach
    """)

# Performance tips
with st.expander("🚀 Performance Tips"):
    st.markdown("""
    **For Best Streaming Performance:**
    - Use **Opus** format for lowest latency
    - Use **MP3** for best compatibility
    - Keep text under 500 words for optimal streaming
    - Ensure stable internet connection
    
    **For Best File Generation:**
    - Use **FLAC** for highest quality
    - Use **MP3** for smallest file size
    - Any text length works well
    """)

# Usage statistics
if OUTPUT_DIR.exists():
    audio_files = list(OUTPUT_DIR.glob("*"))
    if audio_files:
        st.caption(f"📁 {len(audio_files)} audio files in output directory")

st.markdown("---")
st.markdown("🚀 Built with Streamlit and OpenAI | ⚡ Enhanced with true streaming capabilities") 