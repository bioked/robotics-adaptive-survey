# Robotics Adaptive Survey

This flask-based survey tool is designed to collect information from participants through an intake form for an HRI survey. Built with Python and Flask, it uses simple branching based on the respondent's experience and comfort level operating a robot. Responses are stored as CSV. It also includes researcher-facing routes and API endpoints (WIP).

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install Flask
python app.py
