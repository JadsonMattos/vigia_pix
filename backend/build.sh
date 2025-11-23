#!/bin/bash
# Build script for Render.com

echo "🔨 Building VigiaPix Backend..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build complete!"

