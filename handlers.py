# Import Azure Computer Vision client and feature types for image analysis
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes

# Import Azure Speech SDK for speech-to-text functionality
import azure.cognitiveservices.speech as speechsdk
# Import pydub module for audio manipulation
from pydub import AudioSegment

# Import credentials handler for Azure Cognitive Services authentication
from msrest.authentication import CognitiveServicesCredentials

# Import Azure OpenAI client for GPT model interaction
from openai import AzureOpenAI

# Load environment variables from .env file securely
from dotenv import load_dotenv
import openai
import os

# Import Telegram Bot API components for interaction handling
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, CommandHandler,
    ContextTypes, filters
)

# Load environment variables (API keys, endpoints)
load_dotenv("yoga-bot-charu.env")

# Initialize Azure OpenAI client for GPT-based responses
client = AzureOpenAI(
    # Fetch API key securely
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    # Azure resource URL
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    # API version in use
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

# Function to generate a GPT-based response from user input
def generate_response(prompt):
    # Apply custom logic to modify prompt based on user input
    modified_prompt = apply_custom_logic(prompt)

    # Send prompt to Azure OpenAI GPT deployment for completion
    response = client.chat.completions.create(
        # GPT deployment ID
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_ID"),
        messages=[  # Define system and user messages for context
            {"role": "system", "content": "You are a yoga bot providing "
             "recommendations to the user on yoga poses, customised class plans, "
             "environment-based pose suggestions, and yoga sequences "
             "tailored to the user's needs."},
            {"role": "user", "content": prompt}
        ],
        # Limit the response to 200 tokens
        max_tokens=200,
        # Control response creativity (0.0-1.0)
        temperature=0.7
    )
    # Return the text content of the first response choice
    return response.choices[0].message.content

# Function to apply simple custom rules to user input
def apply_custom_logic(input_text):
    input_text_lower = input_text.lower()

    if "beginner" in input_text_lower:
        return ("The user is a beginner. Recommend simple, low-impact poses. "
                f"Query: {input_text}")
    
    if "advanced" in input_text_lower or "intense" in input_text_lower:
        return ("The user is advanced. Suggest challenging sequences. "
                f"Query: {input_text}")
    
    if "backpain" in input_text_lower or "relax" in input_text_lower:
        return ("The user seeks relief from back pain or relaxation. "
                f"Query: {input_text}")
    
    # Default fallback logic if no special conditions match
    return f"Query: {input_text}"

# Initialize Azure Computer Vision client with endpoint and key
def get_cv_client():
    return ComputerVisionClient(
        # Vision API endpoint
        os.getenv("VISION_ENDPOINT"),
        # API key auth
        CognitiveServicesCredentials(os.getenv("VISION_KEY"))
    )

# Analyze an image for tags and description using Azure CV
def analyze_image(image_path):
    # Get initialized CV client
    client = get_cv_client()
    with open(image_path, "rb") as img:
        # Analyze image for tags and caption
        result = client.analyze_image_in_stream(img, visual_features=[
            VisualFeatureTypes.tags, VisualFeatureTypes.description
        ])
    # Extract tag names from result
    tags = [t.name for t in result.tags]
    # Extract first caption if available
    caption = result.description.captions[0].text if result.description.captions else ""
    # Return formatted string of tags and caption
    return f"Tags: {tags}\nCaption: {caption}"

# Absolute paths to ffmpeg and ffprobe binaries
ffmpeg_path = os.path.abspath("./bin/ffmpeg.exe")
ffprobe_path = os.path.abspath("./bin/ffprobe.exe")

# Assign paths directly to pydub's AudioSegment handlers
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# Extend system PATH to include ffmpeg directory
ffmpeg_dir = os.path.dirname(ffmpeg_path)
os.environ["PATH"] += os.pathsep + ffmpeg_dir
print("Updated PATH includes:", ffmpeg_dir)

# Audio File Setup

# Define input (OGG) and output (WAV) audio file paths
ogg_file = "./voice.ogg"
wav_file = "./voice.wav"

# Verify that input file and tool paths are valid
print("OGG file exists:", os.path.isfile(ogg_file))
print("Using ffmpeg:", AudioSegment.converter)
print("Using ffprobe:", AudioSegment.ffprobe)

# Audio Conversion from ogg to wav file to provide to Azure speech processing
try:
    # Load OGG audio, resample to 16kHz, mono, 16-bit
    audio = AudioSegment.from_file(ogg_file, format="ogg")
    audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
    
    # Export processed audio as WAV
    audio.export(wav_file, format="wav")
    print("Audio converted successfully:", wav_file)

except Exception as e:
    # Handle and report conversion errors
    print("Error converting audio:", e)
# Convert speech in audio file to text using Azure Speech Service
def recognize_speech_from_audio(file_path):
    # Configure Azure Speech with subscription key and region
    speech_config = speechsdk.SpeechConfig(
        # Azure Speech API key
        subscription=os.getenv("SPEECH_KEY"),
        # Azure region for speech service
        region=os.getenv("SPEECH_REGION")
    )
    # Set up audio file input configuration
    audio_config = speechsdk.audio.AudioConfig(filename=file_path)
    
    # Initialize speech recognizer with configs
    recognizer = speechsdk.SpeechRecognizer(speech_config, audio_config)
    
    # Perform recognition once on the audio file
    result = recognizer.recognize_once()
    
    # Return recognized text or error message if not understood
    return result.text if result.reason == speechsdk.ResultReason.RecognizedSpeech \
           else "Could not understand"


