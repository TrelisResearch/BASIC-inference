"""Configuration settings for the touch rugby bot and evaluations."""

import os
from dotenv import load_dotenv
import openai
from humanloop import Humanloop
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure Humanloop
humanloop = Humanloop(api_key=os.getenv('HUMANLOOP_API_KEY'))

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

BT_EVAL_CONFIG = {
    "dataset": "touch-rugby-evals",
    "scorer": "touch-criteria",
    "project": "touch-rugby-bot"
}

MODEL_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.7
} 