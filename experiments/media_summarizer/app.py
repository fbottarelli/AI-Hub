import os
import tempfile
import streamlit as st
from moviepy.editor import VideoFileClip
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in .env file")

client = genai.Client(api_key=GOOGLE_API_KEY)

def extract_audio_from_video(video_path):
    """Extract audio from video file."""
    video = VideoFileClip(video_path)
    audio = video.audio
    
    # Save audio to temporary file
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    audio.write_audiofile(temp_audio.name)
    video.close()
    
    return temp_audio.name

def transcribe_audio(audio_path, model_name):
    """Transcribe audio file using Google Gemini."""
    try:
        # Upload audio file to Gemini
        audio_file = client.files.upload(file=audio_path)
        
        # Create transcription prompt
        prompt = """Accurately transcribe this audio file. Maintain:
        - Exact wording including filler words
        - Speaker changes (mark with [Speaker X])
        - Non-verbal sounds in brackets
        - Punctuation and capitalization"""
        
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt, audio_file],
            config={
                'temperature': 0.1,
                'top_p': 0.95,
                'top_k': 20,
                'max_output_tokens': 4096
            }
        )
        return response.text
    except Exception as e:
        return f"Error transcribing audio: {str(e)}"

def generate_summary(text, model_name):
    """Generate summary using Google Gemini."""
    prompt = f"""Please provide a comprehensive summary of the following transcription. 
    Focus on the main points, key insights, and important details. 
    Structure the summary in a clear and organized way:

    {text}
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                'temperature': 0.3,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 2048
            }
        )
        return response.text
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def main():
    st.title("Media Content Summarizer")
    st.write("Upload a video or audio file to get a detailed summary of its content")
    
    # Aggiungi selettore modello Gemini
    model_options = {
        "Gemini 2.0 Pro (Migliorato)": "gemini-2.0-pro-exp-02-05",
        "Gemini 2.0 Flash Thinking": "gemini-2.0-flash-thinking-exp-01-21", 
        "Gemini 2.0 Flash": "gemini-2.0-flash-exp",
        "Gemini (Anniversario)": "gemini-exp-1206",
        "LearnLM 1.5 Pro Sperimentale": "learnlm-1.5-pro-experimental"
    }
    model_choice = st.selectbox("Seleziona il modello Gemini", options=list(model_options.keys()))
    selected_model = model_options[model_choice]

    # File uploader
    uploaded_file = st.file_uploader("Choose a file", type=['mp4', 'mp3', 'wav', 'avi'])
    
    if uploaded_file:
        with st.spinner("Processing your file..."):
            # Save uploaded file temporarily
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(uploaded_file.read())
            
            try:
                # Handle video files
                if uploaded_file.type.startswith('video'):
                    st.video(temp_file.name)
                    audio_path = extract_audio_from_video(temp_file.name)
                else:
                    # Handle audio files
                    st.audio(temp_file.name)
                    audio_path = temp_file.name
                
                # Transcribe
                st.subheader("Transcription")
                transcription = transcribe_audio(audio_path, selected_model)
                st.text_area("Extracted Text", transcription, height=200)
                
                if transcription and not transcription.startswith("Error transcribing"):
                    # Generate summary
                    st.subheader("Summary")
                    summary = generate_summary(transcription, selected_model)
                    st.markdown(summary)
                else:
                    st.error("Could not generate summary due to transcription error")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                # Cleanup
                os.unlink(temp_file.name)
                if 'audio_path' in locals():
                    os.unlink(audio_path)

if __name__ == "__main__":
    main() 