import getpass
import os
import base64
from pathlib import Path

# --- Potentially required imports, install if needed ---
try:
    from IPython.display import Image, display
except ImportError:
    print("Warning: 'ipython' package not found. Image display might not work.")
    Image, display = None, None # Assign None to avoid NameError later

try:
    from google.ai.generativelanguage_v1beta.types import Tool as GenAITool
except ImportError:
    print("Warning: 'google-ai-generativelanguage' package not found. Built-in tools might not work.")
    GenAITool = None # Assign None

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    print("Warning: 'scikit-learn' package not found. Task Types example might not work.")
    cosine_similarity = None # Assign None
# --- Core Langchain Imports ---
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore


# --- 1. API Key Setup ---
def setup_api_key():
    """Sets up the Google AI API key from environment variables or user input."""
    if "GOOGLE_API_KEY" not in os.environ:
        print("Google AI API Key not found in environment variables.")
        api_key = getpass.getpass("Enter your Google AI API key: ")
        os.environ["GOOGLE_API_KEY"] = api_key
        print("API Key set for this session.")
    else:
        print("Google AI API Key found in environment variables.")

# --- 2. Basic Chat Model Usage ---
def basic_chat_example():
    """Demonstrates basic interaction with the Gemini chat model."""
    print("\n--- Running Basic Chat Example ---")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", # Updated model name based on common availability
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    messages = [
        SystemMessage(content="You are a helpful assistant that translates English to French."),
        HumanMessage(content="I love programming."),
    ]
    try:
        response = llm.invoke(messages)
        print("Input:", [m.content for m in messages])
        print("Output:", response.content)
    except Exception as e:
        print(f"Error during basic chat invocation: {e}")

# --- 3. Chain Calls with Prompt Template ---
def prompt_template_example():
    """Shows chaining a prompt template with the Gemini model."""
    print("\n--- Running Prompt Template Example ---")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that translates {input_language} to {output_language}."),
        ("human", "{input}"),
    ])
    chain = prompt | llm
    try:
        result = chain.invoke({
            "input_language": "English",
            "output_language": "German",
            "input": "I love programming.",
        })
        print("Input:", {"input_language": "English", "output_language": "German", "input": "I love programming."})
        print("Output:", result.content)
    except Exception as e:
        print(f"Error during prompt template invocation: {e}")

# --- 4. Image Input ---
def image_input_example(image_url="https://picsum.photos/seed/picsum/200/300", local_image_path=None):
    """Demonstrates using image URLs and local files with multimodal models."""
    print("\n--- Running Image Input Example ---")
    # Use a model known for vision capabilities if needed, e.g., gemini-pro-vision (check availability)
    # Using gemini-1.5-flash as it generally supports multimodality
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # a) Using an image URL
    print(f"\nUsing Image URL: {image_url}")
    message_url = HumanMessage(
        content=[
            {"type": "text", "text": "Describe this image."},
            {"type": "image_url", "image_url": image_url},
        ]
    )
    try:
        result_url = llm.invoke([message_url])
        print("Image URL Description:", result_url.content)
    except Exception as e:
        print(f"Error processing image URL: {e}")

    # b) Using a local image (if path provided and file exists)
    if local_image_path and Path(local_image_path).is_file():
        print(f"\nUsing Local Image: {local_image_path}")
        try:
            with open(local_image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
            # Determine MIME type based on extension (basic example)
            ext = Path(local_image_path).suffix.lower()
            mime_type = f"image/{ext[1:]}" if ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp'] else "image/png" # Default to png

            message_local = HumanMessage(
                content=[
                    {"type": "text", "text": "Describe this image."},
                    {"type": "image_url", "image_url": f"data:{mime_type};base64,{encoded_image}"}
                ]
            )
            result_local = llm.invoke([message_local])
            print("Local Image Description:", result_local.content)
        except FileNotFoundError:
            print(f"Error: Local image file not found at {local_image_path}")
        except Exception as e:
            print(f"Error processing local image: {e}")
    else:
        print(f"\nSkipping local image part. Path not provided or file doesn't exist: {local_image_path}")

# --- 5. Audio Input ---
def audio_input_example(audio_file_path=None):
    """Shows how to provide audio data for tasks like transcription."""
    print("\n--- Running Audio Input Example ---")
    if not audio_file_path or not Path(audio_file_path).is_file():
        print(f"Skipping audio example. Provide a valid 'audio_file_path'. Path provided: {audio_file_path}")
        return

    print(f"Using Audio File: {audio_file_path}")
    # Ensure the model supports audio input. gemini-1.5-flash generally does.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # Basic MIME type detection (can be improved)
    ext = Path(audio_file_path).suffix.lower()
    if ext == ".mp3":
        audio_mime_type = "audio/mpeg"
    elif ext == ".wav":
        audio_mime_type = "audio/wav"
    elif ext == ".ogg":
        audio_mime_type = "audio/ogg"
    else:
        print(f"Warning: Unknown audio extension '{ext}'. Defaulting MIME type to 'audio/mpeg'.")
        audio_mime_type = "audio/mpeg"

    try:
        with open(audio_file_path, "rb") as audio_file:
            encoded_audio = base64.b64encode(audio_file.read()).decode('utf-8')

        message = HumanMessage(
            content=[
                {"type": "text", "text": "Transcribe this audio, please."},
                # Note: Langchain might evolve its media handling.
                # The original example used "media", but "image_url" with data URI is often used for inline data.
                # Let's try the data URI format similar to images, as 'media' type might be specific or deprecated.
                # If this fails, the underlying API call structure might need adjustment based on latest langchain-google-genai docs.
                {"type": "image_url", "image_url": f"data:{audio_mime_type};base64,{encoded_audio}"}
                # Original 'media' approach (keep for reference if the above fails):
                # {"type": "media", "data": encoded_audio, "mime_type": audio_mime_type}
            ]
        )
        response = llm.invoke([message])
        print("Audio Transcription/Response:", response.content)
    except FileNotFoundError:
         print(f"Error: Audio file not found at {audio_file_path}")
    except Exception as e:
        print(f"Error during audio processing: {e}")
        print("Note: Audio processing might require specific model versions or API features.")

# --- 6. Video Input ---
def video_input_example(video_file_path=None):
    """Demonstrates using video files with Gemini models."""
    print("\n--- Running Video Input Example ---")
    if not video_file_path or not Path(video_file_path).is_file():
        print(f"Skipping video example. Provide a valid 'video_file_path'. Path provided: {video_file_path}")
        return

    print(f"Using Video File: {video_file_path}")
    # Ensure the model supports video input. gemini-1.5-flash generally does.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # Basic MIME type detection
    ext = Path(video_file_path).suffix.lower()
    if ext == ".mp4":
        video_mime_type = "video/mp4"
    elif ext == ".mov":
        video_mime_type = "video/quicktime"
    elif ext == ".avi":
        video_mime_type = "video/x-msvideo"
    else:
        print(f"Warning: Unknown video extension '{ext}'. Defaulting MIME type to 'video/mp4'.")
        video_mime_type = "video/mp4"

    try:
        with open(video_file_path, "rb") as video_file:
            encoded_video = base64.b64encode(video_file.read()).decode('utf-8')

        message = HumanMessage(
            content=[
                {"type": "text", "text": "Describe the key events happening in this video."},
                 # Using the data URI approach similar to audio/image
                {"type": "image_url", "image_url": f"data:{video_mime_type};base64,{encoded_video}"}
                # Original 'media' approach (keep for reference):
                # {"type": "media", "data": encoded_video, "mime_type": video_mime_type}
            ]
        )
        response = llm.invoke([message])
        print("Video Description:", response.content)
    except FileNotFoundError:
         print(f"Error: Video file not found at {video_file_path}")
    except Exception as e:
        print(f"Error during video processing: {e}")
        print("Note: Video processing can be resource-intensive and might require specific model versions.")


# --- 7. Image Generation ---
# Note: Image generation models might have specific names and might not be the standard chat models.
# The example used "models/gemini-2.0-flash-exp-image-generation", which might be experimental or outdated.
# Check Google AI documentation for current image generation model names (e.g., potentially via Imagen API integration).
# This example might fail if the specified model isn't available or correctly configured.
def image_generation_example(output_image_path="generated_image.png"):
    """Generates an image from a text prompt (requires a specific image generation model)."""
    print("\n--- Running Image Generation Example ---")
    # IMPORTANT: Replace with the actual, available image generation model name if different.
    image_gen_model_name = "gemini-1.5-flash" # Placeholder - Check docs for actual image gen models

    if "imagen" in image_gen_model_name or "image-generation" in image_gen_model_name: # Basic check
        print(f"Using presumed image generation model: {image_gen_model_name}")
    else:
         print(f"Warning: Model '{image_gen_model_name}' might not support direct image generation as in the example. Check Google AI docs.")
         # Attempting anyway, but it might fail or return text.

    try:
        # Initialization might differ for specific generation models.
        llm = ChatGoogleGenerativeAI(model=image_gen_model_name)

        # The original example used a specific message format and generation_config.
        # This might need adjustment based on the actual model and LangChain integration.
        # Let's try a simple prompt first.
        prompt = "Generate an image of a cat wearing a red hat."
        # If direct generation is supported via invoke with config:
        # response = llm.invoke(
        #     prompt,
        #     generation_config={"response_modalities": ["IMAGE"]} # Example config
        # )

        # Simpler approach: just invoke, see if it returns image data
        response = llm.invoke(prompt)

        print("Image Generation Raw Response:", response) # See what the model returns

        # --- Post-processing based on expected response format ---
        # This part heavily depends on how the image data is returned.
        # The original example expected content[0] with image_url. Adapt as needed.
        image_data = None
        if isinstance(response.content, list) and len(response.content) > 0:
            first_item = response.content[0]
            if isinstance(first_item, dict) and first_item.get("type") == "image_url":
                 image_url_data = first_item.get("image_url", {}).get("url")
                 if image_url_data and image_url_data.startswith("data:image"):
                     image_base64 = image_url_data.split(",")[-1]
                     image_data = base64.b64decode(image_base64)
            # Add other checks if the format differs (e.g., direct base64 string in response.content)

        elif isinstance(response.content, str) and response.content.startswith("data:image"): # Maybe direct data URI?
             image_base64 = response.content.split(",")[-1]
             image_data = base64.b64decode(image_base64)

        if image_data:
            print(f"Image data received. Saving to {output_image_path}")
            with open(output_image_path, "wb") as f:
                f.write(image_data)
            # Try displaying if IPython is available
            if Image and display:
                print("Displaying generated image (if in compatible environment):")
                display(Image(data=image_data, width=300))
            else:
                print(f"Image saved to {output_image_path}. Cannot display (IPython not available or display failed).")
        else:
            print("Could not extract image data from the response.")
            print("Response content:", response.content)

    except Exception as e:
        print(f"Error during image generation: {e}")
        print("Check if the model name is correct and supports image generation.")

# --- 8. Tool Calling / Function Calling ---
# a) Define a tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    """A dummy function to simulate fetching weather."""
    print(f"--- Tool 'get_weather' called with location: {location} ---")
    # In a real scenario, this would call an API
    if "san francisco" in location.lower():
        return "It's foggy and cool in San Francisco."
    elif "tokyo" in location.lower():
         return "It's warm and sunny in Tokyo."
    else:
        return f"Weather data unavailable for {location}. Let's say it's pleasant."

def tool_calling_example():
    """Demonstrates using custom tools with Gemini."""
    print("\n--- Running Tool Calling Example ---")
    # Use a model known to be good at tool calling (gemini-1.5-flash is generally capable)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    llm_with_tools = llm.bind_tools([get_weather]) # Bind the tool

    query = "What's the weather like in San Francisco right now?"
    print(f"Invoking model with query: '{query}' and tool '{get_weather.name}'")

    try:
        # First invocation: Model should decide to call the tool
        ai_msg = llm_with_tools.invoke(query)
        print("\nModel Response (initial):", ai_msg)

        # Check if the model generated tool calls
        if not ai_msg.tool_calls:
            print("\nModel did not request a tool call. Final response:", ai_msg.content)
            return

        print(f"\nModel requested tool call(s): {ai_msg.tool_calls}")

        # Execute the tool call(s) and collect results
        tool_messages = []
        for tool_call in ai_msg.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args")
            tool_id = tool_call.get("id")

            if tool_name == get_weather.name:
                # Call the actual function with the arguments provided by the model
                tool_output = get_weather(tool_args.get('location', '')) # Pass args correctly
                print(f" -> Executed '{tool_name}', Output: '{tool_output}'")
                # Create a ToolMessage with the result
                tool_messages.append(ToolMessage(content=tool_output, tool_call_id=tool_id))
            else:
                print(f"Warning: Model requested unknown tool '{tool_name}'")
                tool_messages.append(ToolMessage(content=f"Error: Unknown tool '{tool_name}'", tool_call_id=tool_id))

        # Second invocation: Pass the original message and the tool results back to the model
        print("\nInvoking model again with tool results...")
        final_response = llm_with_tools.invoke([ai_msg] + tool_messages) # Pass history including AI msg and tool results

        print("\nFinal Response from model:", final_response.content)

    except Exception as e:
        print(f"Error during tool calling: {e}")

# --- 9. Built-in Tools (Google Search, Code Execution) ---
def built_in_tools_example():
    """Leverages Gemini's native tools like Google Search and Code Execution."""
    print("\n--- Running Built-in Tools Example ---")
    if not GenAITool:
        print("Skipping built-in tools example: 'google.ai.generativelanguage' package not found.")
        return

    # Use a model that supports function calling/tools (gemini-1.5-flash usually does)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # a) Google Search Tool
    print("\nTesting Google Search Tool...")
    search_query = "When is the next total solar eclipse visible from the contiguous US?"
    try:
        # Define the Google Search tool according to the google-ai library spec
        google_search_tool = GenAITool(google_search_retrieval={}) # Use google_search_retrieval

        search_resp = llm.invoke(
            search_query,
            tools=[google_search_tool] # Pass the tool instance
        )
        # The response might contain citations or structured search results
        print(f"Query: '{search_query}'")
        print("Search Response Content:", search_resp.content)
        # Check for tool calls or specific response attributes if needed
        # print("Search Response Metadata:", search_resp.response_metadata)


    except Exception as e:
        print(f"Error using Google Search tool: {e}")
        print("Ensure the model supports this tool and API key has necessary permissions.")

    # b) Code Execution Tool (Use with caution!)
    print("\nTesting Code Execution Tool...")
    code_query = "What is 123 * 456? Use python code to calculate it."
    try:
         # Define the Code Execution tool
        code_execution_tool = GenAITool(code_execution={}) # No args needed for the tool itself

        code_resp = llm.invoke(
            code_query,
            tools=[code_execution_tool] # Pass the tool instance
        )

        print(f"Query: '{code_query}'")
        print("Code Execution Response Content:", code_resp.content) # Raw content

        # The original example iterated through content parts, let's replicate that if content is a list
        if isinstance(code_resp.content, list):
             print("\nParsed Code Execution Response Parts:")
             for part in code_resp.content:
                 if isinstance(part, dict):
                     part_type = part.get("type")
                     if part_type == 'executable_code':
                         print(f"  - Executable Code Proposed: {part.get('executable_code', {}).get('code')}")
                     elif part_type == 'code_execution_result':
                         print(f"  - Code Execution Result: {part.get('code_execution_result', {}).get('outcome')}")
                 elif isinstance(part, str):
                     print(f"  - Text Part: {part}")
        elif isinstance(code_resp.content, str):
             # Simpler response, just print the string
             print(f"Response (string): {code_resp.content}")

        # You might also check response_metadata or tool_calls if the structure differs
        # print("Code Execution Response Metadata:", code_resp.response_metadata)


    except Exception as e:
        print(f"Error using Code Execution tool: {e}")
        print("Ensure the model supports this tool. Use code execution responsibly.")


# --- 10. Structured Output (Pydantic) ---
class Person(BaseModel):
    """Information about a person."""
    name: str = Field(..., description="The person's name")
    height_m: float = Field(None, description="The person's height in meters, if known")

def structured_output_example():
    """Forces the model output to conform to a Pydantic schema."""
    print("\n--- Running Structured Output Example ---")
    # Use a model known to work well with structured output (gemini-1.5-flash often does)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    # `with_structured_output` is the correct method
    structured_llm = llm.with_structured_output(Person)

    query = "Tell me about the 16th president of the USA, including his height in meters."
    print(f"Invoking model with query for structured output: '{query}'")
    try:
        result = structured_llm.invoke(query)
        print("Structured Output (Pydantic Object):", result)
        print("Name:", result.name)
        print("Height (m):", result.height_m)
    except Exception as e:
        print(f"Error during structured output invocation: {e}")
        print("Ensure the model supports structured output and the Pydantic model is well-defined.")


# --- 11. Token Usage Tracking ---
def token_usage_example():
    """Shows how to access token usage metadata after a call."""
    print("\n--- Running Token Usage Example ---")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    prompt = "Explain the concept of prompt engineering in one concise sentence."
    try:
        result = llm.invoke(prompt)
        print("Prompt:", prompt)
        print("Response:", result.content)
        print("\nUsage Metadata:", result.usage_metadata) # Access the metadata attribute
    except Exception as e:
        print(f"Error during invocation for token tracking: {e}")

# --- 12. Gemini Embeddings ---
def embeddings_example():
    """Demonstrates generating text embeddings using Gemini."""
    print("\n--- Running Embeddings Example ---")
    # Use an appropriate embeddings model name (check Google AI docs for current names)
    # Example name from cheatsheet: "models/embedding-001" or "models/text-embedding-004" might be current
    embedding_model_name = "models/text-embedding-004" # Replace if needed
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model_name)

        # a) Embed a single query
        query = "hello, world!"
        vector = embeddings.embed_query(query)
        print(f"\nEmbedding for query: '{query}'")
        print(f"Vector (first 10 dims): {vector[:10]}...") # Show partial vector
        print(f"Vector dimension: {len(vector)}")

        # b) Embed multiple documents
        documents = [
            "The quick brown fox jumps over the lazy dog.",
            "LangChain provides tools for building AI applications.",
            "Paris is the capital of France.",
        ]
        vectors = embeddings.embed_documents(documents)
        print(f"\nEmbeddings for {len(documents)} documents:")
        for i, doc in enumerate(documents):
            print(f"  Doc {i+1}: '{doc}'")
            print(f"  Vector (first 10 dims): {vectors[i][:10]}...")
            print(f"  Vector dimension: {len(vectors[i])}")

    except Exception as e:
        print(f"Error during embeddings generation: {e}")
        print(f"Ensure the embedding model name '{embedding_model_name}' is correct and available.")


# --- 13. Using Embeddings with a Vector Store ---
def vector_store_example():
    """Integrates Gemini embeddings with an in-memory vector store for retrieval."""
    print("\n--- Running Vector Store Example ---")
    embedding_model_name = "models/text-embedding-004" # Use the same model as above
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model_name)

        texts = [
            "LangChain is a framework for developing applications powered by language models.",
            "It enables applications that are context-aware and reasoning-based.",
            "Google Gemini is a family of large language models.",
            "Vector stores are databases for efficient similarity searches on embeddings."
            ]
        print("Creating InMemoryVectorStore with texts:")
        for t in texts: print(f" - {t}")

        # Create vector store from texts
        vectorstore = InMemoryVectorStore.from_texts(texts, embedding=embeddings)

        # Create a retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2}) # Get top 2 results

        # Query the retriever
        query = "What is LangChain used for?"
        print(f"\nRetrieving documents similar to: '{query}'")
        retrieved_documents = retriever.invoke(query)

        print("\nRetrieved Documents:")
        if retrieved_documents:
            for i, doc in enumerate(retrieved_documents):
                print(f"  {i+1}. Content: {doc.page_content}")
                # print(f"     Metadata: {doc.metadata}") # Metadata is usually empty for from_texts
        else:
            print("  No documents retrieved.")

    except Exception as e:
        print(f"Error during vector store example: {e}")


# --- 14. Embedding Task Types ---
def task_types_example():
    """Optimizes embeddings by specifying the task type."""
    print("\n--- Running Task Types Example ---")
    if not cosine_similarity:
         print("Skipping task types example: 'scikit-learn' not installed.")
         return

    embedding_model_name = "models/text-embedding-004" # Check availability
    try:
        # Initialize embeddings with specific task types
        query_embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            task_type="retrieval_query"  # For similarity search queries
        )
        doc_embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model_name,
            task_type="retrieval_document"  # For documents to be stored/searched
        )
        # Other potential task types: "semantic_similarity", "classification", "clustering"

        print(f"Using Query Embedding Task Type: {query_embeddings.task_type}")
        print(f"Using Document Embedding Task Type: {doc_embeddings.task_type}")

        # Example query and documents
        query = "What is the capital of France?"
        documents = [
            "Paris is the capital city of France, known for the Eiffel Tower.",
            "Berlin is the capital of Germany.",
            "What kind of food do people eat in Paris?" # Semantically related but different topic
            ]

        # Embed the query and documents using their respective task types
        q_embed = query_embeddings.embed_query(query)
        d_embeds = doc_embeddings.embed_documents(documents)

        print(f"\nComparing query '{query}' similarity to documents:")
        for i, doc in enumerate(documents):
            similarity = cosine_similarity([q_embed], [d_embeds[i]])[0][0]
            print(f"  - Doc: '{doc}'")
            print(f"    Similarity: {similarity:.4f}")

    except Exception as e:
        print(f"Error during task types example: {e}")
        print("Ensure the model supports task types and the types used are valid.")


# --- Main Execution ---
if __name__ == "__main__":
    print("Running Langchain Google Gemini Examples")
    print("======================================")

    # 1. Set up API Key (Important first step)
    setup_api_key()

    # --- Choose which examples to run ---
    # run_basic_chat = True
    # run_prompt_template = True
    # run_image_input = True # Set local_image_path if testing local files
    # run_audio_input = False # Set audio_file_path to a valid .mp3 or .wav file
    # run_video_input = False # Set video_file_path to a valid .mp4 file
    # run_image_generation = False # Requires specific model and might fail
    # run_tool_calling = True
    # run_built_in_tools = True # Requires google-ai-generativelanguage
    # run_structured_output = True
    # run_token_usage = True
    # run_embeddings = True # Requires embedding model
    # run_vector_store = True # Requires embedding model
    # run_task_types = True # Requires embedding model and scikit-learn

    # --- Example Execution ---
    # if run_basic_chat:
    #     basic_chat_example()
    # if run_prompt_template:
    #     prompt_template_example()
    # if run_image_input:
    #     # Provide a path to a real image if you have one, otherwise it uses the URL
    #     local_image_for_test = "../assets/react.png" # Placeholder - CHANGE ME
    #     image_input_example(local_image_path=local_image_for_test)
    # if run_audio_input:
    #     audio_file_for_test = "../path/to/your/audio/file.mp3" # Placeholder - CHANGE ME
    #     audio_input_example(audio_file_path=audio_file_for_test)
    # if run_video_input:
    #     video_file_for_test = "../path/to/your/video/file.mp4" # Placeholder - CHANGE ME
    #     video_input_example(video_file_path=video_file_for_test)
    # if run_image_generation:
    #     image_generation_example(output_image_path="generated_cat.png")
    # if run_tool_calling:
    #     tool_calling_example()
    # if run_built_in_tools:
    #     built_in_tools_example()
    # if run_structured_output:
    #     structured_output_example()
    # if run_token_usage:
    #     token_usage_example()
    # if run_embeddings:
    #     embeddings_example()
    # if run_vector_store:
    #     vector_store_example()
    # if run_task_types:
    #     task_types_example()

    print("\n======================================")
    print("Finished running selected examples.")
    print