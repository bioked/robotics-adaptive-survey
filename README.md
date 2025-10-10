
# HRI adaptive survey

This flask-based survey tool is designed to collect data from participants in human-robot interaction (HRI) studies. It assigns participants to different segments based on their experience and comfort levels operating a robot.

Built with Python, Flask, and SQLAlchemy, the tool stores responses in a relational database and includes researcher-facing routes and API endpoints (WIP).

## Run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
