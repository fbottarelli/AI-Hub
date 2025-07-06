import gradio as gr
from deepgram import DeepgramClient, SpeakOptions
import asyncio
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from langchain.chat_models import ChatOpenRouter
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()

# Get API keys from environment variables
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

class DeepgramApp:
    def __init__(self):
        self.dg_client = None
        self.openai_client = None
        self.openrouter_client = None
        self.dg_api_key = None
        self.openai_api_key = None
        self.openrouter_api_key = None
        
        # Initialize clients with environment variables if available
        if DEEPGRAM_API_KEY or OPENAI_API_KEY or OPENROUTER_API_KEY:
            self.initialize_clients(DEEPGRAM_API_KEY, OPENAI_API_KEY, OPENROUTER_API_KEY)

    def initialize_clients(self, dg_api_key, openai_api_key, openrouter_api_key):
        """Initialize or update the Deepgram, OpenAI and OpenRouter clients with the provided API keys"""
        message = []
        
        if dg_api_key:
            self.dg_api_key = dg_api_key
            self.dg_client = DeepgramClient(dg_api_key)
            message.append("Deepgram client initialized successfully!")
        
        if openai_api_key:
            self.openai_api_key = openai_api_key
            self.openai_client = OpenAI(api_key=openai_api_key)
            message.append("OpenAI client initialized successfully!")

        if openrouter_api_key:
            self.openrouter_api_key = openrouter_api_key
            self.openrouter_client = ChatOpenRouter(api_key=openrouter_api_key)
            message.append("OpenRouter client initialized successfully!")
        
        if not message:
            return "Please provide at least one valid API key"
        
        return " ".join(message)

    async def translate_text(self, text, openrouter_api_key):
        """Translate text to English using OpenRouter"""
        if not openrouter_api_key:
            return "Please provide an OpenRouter API key first"
        
        if self.openrouter_api_key != openrouter_api_key:
            self.initialize_clients(None, None, openrouter_api_key)
        
        try:
            messages = [
                HumanMessage(content=f"Translate the following text to English: {text}")
            ]
            response = self.openrouter_client.invoke(messages)
            return response.content
        except Exception as e:
            return f"Error during translation: {str(e)}"

    async def transcribe_audio(self, audio_path, provider, prompt, dg_api_key, openai_api_key):
        """Transcribe audio to text using either Deepgram or OpenAI"""
        if provider == "deepgram":
            if not dg_api_key:
                return "Please provide a Deepgram API key first"
            
            if self.dg_api_key != dg_api_key:
                self.initialize_clients(dg_api_key, None, None)

            try:
                with open(audio_path, 'rb') as audio:
                    buffer_data = audio.read()
                    
                    payload = {
                        "buffer": buffer_data,
                    }
                    
                    options = {
                        'smart_format': True,
                        'model': 'nova-2',
                        'language': 'it'
                    }
                    
                    response = await asyncio.to_thread(
                        self.dg_client.listen.rest.v("1").transcribe_file,
                        payload,
                        options
                    )
                    return response["results"]["channels"][0]["alternatives"][0]["transcript"]
            except Exception as e:
                return f"Error during Deepgram transcription: {str(e)}"
        
        elif provider == "openai":
            if not openai_api_key:
                return "Please provide an OpenAI API key first"
            
            if self.openai_api_key != openai_api_key:
                self.initialize_clients(None, openai_api_key, None)
            
            try:
                with open(audio_path, "rb") as audio_file:
                    transcription = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        prompt=prompt if prompt else None
                    )
                    return transcription.text
            except Exception as e:
                return f"Error during OpenAI transcription: {str(e)}"

    async def text_to_speech(self, text, provider, voice, dg_api_key, openai_api_key):
        """Convert text to speech using either Deepgram or OpenAI"""
        if provider == "deepgram":
            if not dg_api_key:
                return None, "Please provide a Deepgram API key first"
            
            if self.dg_api_key != dg_api_key:
                self.initialize_clients(dg_api_key, None, None)
            
            try:
                options = SpeakOptions(model=voice)

                output_path = "output_speech.wav"
                self.dg_client.speak.rest.v("1").save(
                    output_path,
                    {"text": text},
                    options
                )
                
                return output_path, "Audio generated successfully with Deepgram!"

            except Exception as e:
                return None, f"Error during Deepgram TTS: {str(e)}"
                
        elif provider == "openai":
            if not openai_api_key:
                return None, "Please provide an OpenAI API key first"
            
            if self.openai_api_key != openai_api_key:
                self.initialize_clients(None, openai_api_key, None)
            
            try:
                output_path = "output_speech.mp3"
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                response.stream_to_file(output_path)
                
                return output_path, "Audio generated successfully with OpenAI!"

            except Exception as e:
                return None, f"Error during OpenAI TTS: {str(e)}"

def create_gradio_interface():
    app = DeepgramApp()
    
    with gr.Blocks(title="Deepgram STT & TTS") as interface:
        gr.Markdown("# Speech-to-Text and Text-to-Speech Platform")
        
        with gr.Row():
            with gr.Column():
                dg_api_key = gr.Textbox(
                    label="Deepgram API Key",
                    placeholder="Enter your Deepgram API key",
                    type="password",
                    value=DEEPGRAM_API_KEY
                )
            with gr.Column():
                openai_api_key = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="Enter your OpenAI API key",
                    type="password",
                    value=OPENAI_API_KEY
                )
            with gr.Column():
                openrouter_api_key = gr.Textbox(
                    label="OpenRouter API Key",
                    placeholder="Enter your OpenRouter API key",
                    type="password",
                    value=OPENROUTER_API_KEY
                )
            init_button = gr.Button("Initialize/Update Clients")

        status_message = gr.Textbox(label="Status", interactive=False)
        
        gr.Markdown("## Speech to Text")
        with gr.Row():
            with gr.Column():
                audio_input = gr.Audio(
                    label="Upload Audio",
                    type="filepath",
                    sources=["upload", "microphone"]
                )
                stt_provider = gr.Radio(
                    choices=["deepgram", "openai"],
                    label="STT Provider",
                    value="deepgram"
                )
                prompt = gr.Textbox(
                    label="Prompt (OpenAI only)",
                    placeholder="Optional: Add a prompt to improve transcription accuracy",
                    visible=False
                )
            with gr.Column():
                transcription_output = gr.Textbox(
                    label="Transcription",
                    interactive=False
                )
                translate_button = gr.Button("Translate to English")
                translation_output = gr.Textbox(
                    label="English Translation",
                    interactive=False
                )

        gr.Markdown("## Text to Speech")
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Text to Convert",
                    placeholder="Enter text to convert to speech"
                )
                provider = gr.Radio(
                    choices=["deepgram", "openai"],
                    label="TTS Provider",
                    value="deepgram"
                )
                voice = gr.Radio(
                    choices=["aura-asteria-en"],
                    label="Voice",
                    value="aura-asteria-en"
                )
            with gr.Column():
                audio_output = gr.Audio(
                    label="Generated Speech",
                    type="filepath"
                )
                tts_status = gr.Textbox(label="TTS Status", interactive=False)

        # Event handlers
        init_button.click(
            app.initialize_clients,
            inputs=[dg_api_key, openai_api_key, openrouter_api_key],
            outputs=[status_message]
        )

        def update_prompt_visibility(provider):
            return gr.update(visible=provider == "openai")

        stt_provider.change(
            update_prompt_visibility,
            inputs=[stt_provider],
            outputs=[prompt]
        )

        audio_input.change(
            lambda x, p, pr, d, o: asyncio.run(app.transcribe_audio(x, p, pr, d, o)),
            inputs=[audio_input, stt_provider, prompt, dg_api_key, openai_api_key],
            outputs=[transcription_output]
        )

        def update_voice_choices(provider):
            if provider == "deepgram":
                return gr.update(
                    choices=["aura-asteria-en"],
                    value="aura-asteria-en"
                )
            else:  # openai
                return gr.update(
                    choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
                    value="alloy"
                )

        provider.change(
            update_voice_choices,
            inputs=[provider],
            outputs=[voice]
        )

        text_input.submit(
            lambda x, p, v, d, o: asyncio.run(app.text_to_speech(x, p, v, d, o)),
            inputs=[text_input, provider, voice, dg_api_key, openai_api_key],
            outputs=[audio_output, tts_status]
        )

        translate_button.click(
            lambda x, o: asyncio.run(app.translate_text(x, o)),
            inputs=[transcription_output, openrouter_api_key],
            outputs=[translation_output]
        )

        # Add footer
        gr.Markdown("---")
        gr.Markdown("*by fbot*", elem_classes=["footer-text"])

    return interface

if __name__ == "__main__":
    interface = create_gradio_interface()
    interface.launch() 