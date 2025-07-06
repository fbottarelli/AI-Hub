import asyncio
import tempfile
import io
from pathlib import Path
from typing import Optional, AsyncGenerator, Iterator
from openai import OpenAI, AsyncOpenAI
from dataclasses import dataclass
import hashlib
import os
import threading
import queue
import time


@dataclass
class TTSConfig:
    """Configuration for TTS generation"""
    model: str
    voice: str
    input_text: str
    instructions: Optional[str] = None
    response_format: str = "mp3"


class StreamingAudioBuffer:
    """Buffer for streaming audio data that can be played while being written"""
    
    def __init__(self):
        self.buffer = io.BytesIO()
        self.chunks = queue.Queue()
        self.is_complete = False
        self.total_size = 0
        self._lock = threading.Lock()
    
    def write_chunk(self, chunk: bytes):
        """Write a chunk of audio data"""
        with self._lock:
            self.buffer.write(chunk)
            self.total_size += len(chunk)
            self.chunks.put(chunk)
    
    def mark_complete(self):
        """Mark the stream as complete"""
        self.is_complete = True
        self.chunks.put(None)  # Sentinel value
    
    def get_buffer(self) -> io.BytesIO:
        """Get the complete buffer"""
        with self._lock:
            self.buffer.seek(0)
            return self.buffer
    
    def iter_chunks(self) -> Iterator[bytes]:
        """Iterate over chunks as they become available"""
        while True:
            try:
                chunk = self.chunks.get(timeout=1.0)
                if chunk is None:  # Sentinel value indicating completion
                    break
                yield chunk
            except queue.Empty:
                if self.is_complete:
                    break
                continue


class TTSService:
    """Service for handling OpenAI Text-to-Speech operations"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize clients
        try:
            self.sync_client = OpenAI()
            self.async_client = AsyncOpenAI()
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI clients: {e}")
    
    def _generate_filename(self, config: TTSConfig) -> str:
        """Generate a safe filename based on input text and configuration"""
        # Create a hash of the input for uniqueness
        text_hash = hashlib.md5(config.input_text.encode()).hexdigest()[:8]
        
        # Create safe filename base from first 30 chars
        safe_base = "".join(c for c in config.input_text[:30] if c.isalnum() or c in (' ', '_')).rstrip().replace(" ", "_")
        if not safe_base:
            safe_base = "speech"
        
        return f"{safe_base}_{text_hash}_{config.voice}_{config.model}.{config.response_format}"
    
    def _build_api_kwargs(self, config: TTSConfig) -> dict:
        """Build API kwargs from configuration"""
        api_kwargs = {
            "model": config.model,
            "voice": config.voice,
            "input": config.input_text,
            "response_format": config.response_format
        }
        
        # Only include instructions if provided and using the gpt-4o-mini-tts model
        if config.instructions and config.model == "gpt-4o-mini-tts":
            api_kwargs["instructions"] = config.instructions
        
        return api_kwargs
    
    def generate_speech_file(self, config: TTSConfig) -> Path:
        """
        Generate speech and save to file (synchronous)
        
        Returns:
            Path to the generated audio file
        """
        filename = self._generate_filename(config)
        file_path = self.output_dir / filename
        
        # Skip generation if file already exists
        if file_path.exists():
            return file_path
        
        api_kwargs = self._build_api_kwargs(config)
        
        try:
            response = self.sync_client.audio.speech.create(**api_kwargs)
            response.stream_to_file(str(file_path))
            return file_path
        except Exception as e:
            raise RuntimeError(f"Failed to generate speech: {e}")
    
    async def generate_speech_stream(self, config: TTSConfig) -> AsyncGenerator[bytes, None]:
        """
        Generate speech as streaming bytes (asynchronous)
        
        Yields:
            Audio data chunks as bytes
        """
        api_kwargs = self._build_api_kwargs(config)
        
        try:
            async with self.async_client.audio.speech.with_streaming_response.create(**api_kwargs) as response:
                async for chunk in response.iter_bytes(chunk_size=1024):
                    yield chunk
        except Exception as e:
            raise RuntimeError(f"Failed to generate streaming speech: {e}")
    
    async def generate_speech_buffer(self, config: TTSConfig) -> io.BytesIO:
        """
        Generate speech and return as BytesIO buffer (asynchronous)
        
        Returns:
            BytesIO buffer containing the complete audio data
        """
        buffer = io.BytesIO()
        
        async for chunk in self.generate_speech_stream(config):
            buffer.write(chunk)
        
        buffer.seek(0)
        return buffer
    
    async def generate_streaming_buffer(self, config: TTSConfig) -> StreamingAudioBuffer:
        """
        Generate speech with true streaming - returns buffer that can be played while being filled
        
        Returns:
            StreamingAudioBuffer that can be read while being written to
        """
        streaming_buffer = StreamingAudioBuffer()
        
        async def fill_buffer():
            try:
                async for chunk in self.generate_speech_stream(config):
                    streaming_buffer.write_chunk(chunk)
                    # Small delay to allow for more natural streaming
                    await asyncio.sleep(0.001)
                streaming_buffer.mark_complete()
            except Exception as e:
                streaming_buffer.mark_complete()
                raise e
        
        # Start filling the buffer in the background
        asyncio.create_task(fill_buffer())
        
        # Give it a moment to start receiving data
        await asyncio.sleep(0.1)
        
        return streaming_buffer
    
    def create_temp_streaming_file(self, config: TTSConfig) -> tuple[Path, threading.Thread]:
        """
        Create a temporary file that gets written to while streaming (for better Streamlit compatibility)
        
        Returns:
            Tuple of (temp_file_path, thread_that_writes_to_it)
        """
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            suffix=f".{config.response_format}",
            delete=False,
            dir=self.output_dir
        )
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        def stream_to_file():
            """Stream audio data to file in a separate thread"""
            try:
                # Run the async streaming in this thread
                async def write_stream():
                    with open(temp_path, 'wb') as f:
                        async for chunk in self.generate_speech_stream(config):
                            f.write(chunk)
                            f.flush()  # Ensure data is written immediately
                
                # Run the async function
                asyncio.run(write_stream())
            except Exception as e:
                print(f"Streaming error: {e}")
        
        # Start the streaming thread
        thread = threading.Thread(target=stream_to_file)
        thread.daemon = True
        thread.start()
        
        return temp_path, thread
    
    def get_available_models(self) -> list[str]:
        """Get list of available TTS models"""
        return ["gpt-4o-mini-tts", "tts-1", "tts-1-hd"]
    
    def get_available_voices(self) -> list[str]:
        """Get list of available voices"""
        return ["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]
    
    def get_available_formats(self) -> list[str]:
        """Get list of available output formats"""
        return ["mp3", "opus", "aac", "flac", "wav", "pcm"]
    
    def supports_instructions(self, model: str) -> bool:
        """Check if model supports instructions parameter"""
        return model == "gpt-4o-mini-tts"


# Utility function for running async code in sync context
def run_async_in_sync(coro):
    """Run async coroutine in sync context (for Streamlit compatibility)"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If there's already a running loop, we need to use a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(coro) 