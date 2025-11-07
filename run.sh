#!/bin/bash

echo "🌾 Starting AI Crop Doctor..."
echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🚀 Launching application..."
streamlit run app.py --server.port=8501 --server.address=0.0.0.0