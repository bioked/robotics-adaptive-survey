# Robotics-Adaptive-Survey

Flask-based robotics-flavoured **adaptive survey** for participant intake.
Logs responses to CSV, and assigns each participant to one of the following groups: 'tutorial', 'standard' or 'advanced') based on the participant's experience and comfort level.

## Features
- '/survey' HTML form (name, age, experience operating a robotic arm, preferred control method, and comfort level)
- Adaptive branching assigns 'assigned_group'
- Persists responses to 'survey_responses.csv'
- '/filled' a 'form submitted / thank you for your response' page shows the assigned group

## Run locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install Flask
python app.py
