# Import necessary components for building the bot
from botbuilder.core import ActivityHandler, TurnContext
from handlers import generate_response, analyze_image, recognize_speech_from_audio

# Define a custom bot class inheriting from ActivityHandler
class YogaBot(ActivityHandler):

    # Handle incoming messages (text, image, or voice)
    async def on_message_activity(self, turn_context: TurnContext):

        # Get the text of the incoming message
        user_input = turn_context.activity.text

        # If message includes "image", simulate image analysis
        if "image" in user_input.lower():
            result = analyze_image("sample_image.jpg")
        # If message includes "voice", simulate voice recognition
        elif "voice" in user_input.lower():
            result = recognize_speech_from_audio("sample_audio.ogg")
        # For all other text inputs, generate GPT-based response
        else:
            result = generate_response(user_input)

        # Send the generated result back to the user
        await turn_context.send_activity(result)
