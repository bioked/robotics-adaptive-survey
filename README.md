# Robotics Adaptive Survey

Flask-based HRI **adaptive survey** for participant intake, with adaptive branching based on the respondent's self-report (past experience working with robots, and comfort level).
Responses are logged to CSV, and participants are assigned to one of three groups: 'tutorial', 'standard', or 'advanced'.

## Features
- /survey -> HTML form (name, age, experience level operating a robotic arm, preferred control method, and comfort level)
- Adaptive branching assigns 'assigned_group'
- /filled -> Thank-you page that shows the participant's assigned group
- All responses are saved to survey_responses.csv
- /responses -> Researcher view: table containing all responses that've been collected
- /responses.csv -> Download all responses as CSV (for analysis or dashboards)

## Run
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install Flask
python app.py
