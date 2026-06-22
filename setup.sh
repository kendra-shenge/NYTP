#!/usr/bin/env bash
# Setup script for NYC Taxi Analytics

export PATH="$HOME/.local/bin:$PATH"

echo "Installing dependencies..."
pip install --user --break-system-packages -r requirements.txt 2>&1 | tail -5

echo ""
echo "To load data into the database, run:"
echo "  python3 -m src.pipeline.load"
echo ""
echo "To start the dashboard, run:"
echo "  streamlit run src/app.py"
echo ""
