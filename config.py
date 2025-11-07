"""
AI Crop Doctor - Configuration File
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Directory
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# API Keys
ASSEMBLY_AI_KEY = os.getenv("ASSEMBLY_AI_KEY", "ceb7e80fe4d94821ac353cdc9012eaaa")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
PLANT_ID_API_KEY = os.getenv("PLANT_ID_API_KEY", "FWkOQW9MDxa3RLEw3tHDwPfN9RAMdVKRPHUXu8vTDTvgoMNkeC")

# API Configuration
ASSEMBLY_AI_URL = "https://api.assemblyai.com/v2"
PLANT_ID_URL = "https://api.plant.id/v2/health_assessment"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "meta-llama/llama-3.2-11b-vision-instruct:free"

# App Settings
APP_NAME = "AI Crop Doctor"
APP_VERSION = "5.0"
CONFIDENCE_THRESHOLD = 0.20

# Punjab Districts
PUNJAB_DISTRICTS = [
    "Select District",
    "Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib",
    "Fazilka", "Firozpur", "Gurdaspur", "Hoshiarpur", "Jalandhar",
    "Kapurthala", "Ludhiana", "Malerkotla", "Mansa", "Moga",
    "Mohali (S.A.S. Nagar)", "Muktsar", "Nawanshahr (Shaheed Bhagat Singh Nagar)",
    "Pathankot", "Patiala", "Rupnagar", "Sangrur", "Tarn Taran"
]

# Supported Languages
LANGUAGES = {
    'en': {'name': 'English', 'code': 'en', 'tts': 'en', 'assemblyai': 'en'},
    'hi': {'name': 'हिंदी (Hindi)', 'code': 'hi', 'tts': 'hi', 'assemblyai': 'hi'},
    'pa': {'name': 'ਪੰਜਾਬੀ (Punjabi)', 'code': 'pa', 'tts': 'pa', 'assemblyai': 'pa'},
    'ur': {'name': 'اردو (Urdu)', 'code': 'ur', 'tts': 'ur', 'assemblyai': 'ur'}
}