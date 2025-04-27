# app.py

import os
from flask import Flask, request, Response
from botbuilder.core import (
    BotFrameworkAdapter, BotFrameworkAdapterSettings, TurnContext
)
from botbuilder.schema import Activity
from handlers import generate_response, analyze_image, recognize_speech_from_audio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Flask App
app = Flask(__name__)

# Azure Bot Adapter Settings
APP_ID = os.getenv("MICROSOFT_APP_ID")
APP_PASSWORD = os.getenv("MICROSOFT_APP_PASSWORD")
adapter_settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkAdapter(adapter_settings)

# Simple async bot logic
async def process_message(turn_context: TurnContext):
    user_input = turn_context.activity.text
    # Here we handle multimodal inputs; we start with text
    response_text = generate_response(user_input)
    await turn_context.send_activity(response_text)

# API Endpoint
@app.route("/api/messages", methods=["POST"])
def messages():
    if "application/json" in request.headers["Content-Type"]:
        json_message = request.json
    else:
        return Response(status=415)

    activity = Activity().deserialize(json_message)
    auth_header = request.headers.get("Authorization", "")
    
    async def aux_func(turn_context):
        await process_message(turn_context)

    task = adapter.process_activity(activity, auth_header, aux_func)
    return Response(status=202)

if __name__ == "__main__":
    app.run(port=3978)
