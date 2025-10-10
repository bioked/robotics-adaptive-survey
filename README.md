
# HRI adaptive survey

This Flask-based survey tool is designed to collect self-reported data from participants in human-robot interaction (HRI) studies. Participants are assigned to different study groups based on their experience and comfort levels operating robots.

Built with Python, Flask, and SQLAlchemy, the tool stores responses in a relational database and includes researcher-facing routes and API endpoints (WIP).

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install Flask
python app.py
