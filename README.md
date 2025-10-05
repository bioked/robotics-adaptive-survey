# Robotics Adaptive Survey

This flask-based survey tool is designed to collect information from study participants. More specifically, it collects self-report intake questionnaires so that a study owner can interpret them. 
Built with Python and Flask, the tool uses simple branching based on the respondent's experience and comfort level operating a robot. Results are stored as CSV. It also includes researcher-facing routes and API endpoints (WIP).

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install Flask
python app.py
