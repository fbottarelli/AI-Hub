import streamlit as st
from openai import OpenAI, OpenAIError
import os
from dotenv import load_dotenv
import io

# Load environment variables from .env file
load_dotenv()

# --- App Configuration ---
st.set_page_config(page_title="OpenAI Speech-to-Text", layout="wide")
st.title("🔊 OpenAI Speech-to-Text")
st.caption("Upload an audio file and get its transcription or translation using OpenAI's Whisper or GPT-4o models.")

# --- Helper Functions ---
def initialize_client():
    """Initializes and returns the OpenAI client, handling API key errors."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable in a .env file.", icon="🚨")
        return None
    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {e}", icon="🚨")
        return None

def transcribe_audio(client, audio_file, model, task, prompt=None, response_format="text"):
    """Calls the OpenAI API for transcription or translation."""
    if not client:
        return None, "OpenAI client not initialized."

    try:
        file_obj = io.BytesIO(audio_file.getvalue())
        file_obj.name = audio_file.name # Necessary for the API

        if task == "transcribe":
            transcription = client.audio.transcriptions.create(
                model=model,
                file=file_obj,
                response_format=response_format,
                prompt=prompt if prompt else None
            )
        elif task == "translate":
            # Translations only supported by whisper-1 and output is always text
            if model != "whisper-1":
                 return None, f"Translation task is only supported by the 'whisper-1' model. Selected model: {model}"
            transcription = client.audio.translations.create(
                model="whisper-1", # Explicitly use whisper-1 for translation
                file=file_obj,
                prompt=prompt if prompt else None
                # response_format is not applicable here as output is English text
            )
        else:
            return None, "Invalid task selected."

        # Handle different response formats if needed in the future
        # For now, assume text or json (with a text field) based on common use
        if hasattr(transcription, 'text'):
             return transcription.text, None
        elif isinstance(transcription, str): # Handle plain text response
             return transcription, None
        else: # Handle potential JSON object without 'text' field gracefully for now
             return str(transcription), "Unexpected response format."


    except OpenAIError as e:
        return None, f"OpenAI API Error: {e}"
    except Exception as e:
        return None, f"An unexpected error occurred: {e}"

# --- OpenAI Client Initialization ---
client = initialize_client()

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# Model Selection
# GPT-4o models currently only support json or text responses.
# Whisper-1 supports json, text, srt, verbose_json, vtt and translations.
available_models = ["gpt-4o-transcribe", "gpt-4o-mini-transcribe", "whisper-1"]
selected_model = st.sidebar.selectbox(
    "Select Model",
    options=available_models,
    index=0,
    help="Choose the speech-to-text model. `whisper-1` supports translation and more response formats/features."
)

# Task Selection (Transcription or Translation)
task_options = ["transcribe"]
if selected_model == "whisper-1":
    task_options.append("translate") # Only whisper-1 supports translation

selected_task = st.sidebar.selectbox(
    "Select Task",
    options=task_options,
    index=0,
    help="`transcribe`: Audio language to text. `translate`: Audio language to English text (only whisper-1)."
)

# Prompt (Optional)
user_prompt = st.sidebar.text_area(
    "Prompt (Optional)",
    help="Provide context or correct spellings to improve accuracy (especially for GPT-4o models). Whisper-1 uses the last 224 tokens.",
    height=100
)

# --- Main Area ---
uploaded_file = st.file_uploader(
    "Choose an audio file...",
    type=["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"],
    help="Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm. Max size: 25MB."
)

if uploaded_file is not None:
    # Display audio player
    st.audio(uploaded_file, format=f'audio/{uploaded_file.type.split("/")[-1]}')

    # Check file size (OpenAI limit is 25 MB)
    file_size_mb = uploaded_file.size / (1024 * 1024)
    if file_size_mb > 25:
        st.error(f"File size ({file_size_mb:.2f} MB) exceeds the 25MB limit.", icon="🚨")
    else:
        st.success(f"File '{uploaded_file.name}' uploaded successfully ({file_size_mb:.2f} MB).", icon="✅")

        # Process Button
        if st.button(f"Run {selected_task.capitalize()}", type="primary", disabled=not client):
            if client:
                with st.spinner(f"{selected_task.capitalize()}ing... Please wait."):
                    result_text, error_message = transcribe_audio(
                        client=client,
                        audio_file=uploaded_file,
                        model=selected_model,
                        task=selected_task,
                        prompt=user_prompt
                    )

                if error_message:
                    st.error(f"Error: {error_message}", icon="🚨")
                elif result_text is not None:
                    st.subheader(f"{selected_task.capitalize()}d Text:")
                    st.text_area("Result", result_text, height=300, key="transcription_result")
                    # Add download button for the text
                    st.download_button(
                        label="Download Text",
                        data=result_text.encode('utf-8'),
                        file_name=f"{os.path.splitext(uploaded_file.name)[0]}_{selected_task}.txt",
                        mime="text/plain"
                    )
                else:
                    st.warning("Received no result or an empty result from the API.", icon="⚠️")
            else:
                st.error("OpenAI client is not initialized. Check API key.", icon="🚨")

else:
    st.info("Upload an audio file to begin.")


st.sidebar.markdown("---")
st.sidebar.markdown("Created with [Streamlit](https://streamlit.io) and [OpenAI](https://openai.com)") 