# Robotics Adaptive Survey

Flask-based HRI **adaptive survey** for participant intake, with branching based on the respondent's self-report (past experience working with robots, and comfort level). 
Responses are saved to CSV, and can be viewed in multiple ways. 

## Features
- /survey -> HTML form (name, age, experience level, preferred control method, and comfort level).
- Adaptive branching assigns each participant to one of the following groups: tutorial, standard, or advanced.
- Responses saved to survey_responses.csv.
- /filled -> Confirmation page, including the assigned group.
- /responses -> Researcher view (HTML table populated with responses).
- /responses.csv -> Download all responses as CSV.
- /api/responses -> JSON API.
	- **GET** -> returns all responses as JSON.
	- **POST** -> accepts new JSON entries (form alternative).

## Run
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt   # or: pip install Flask
python app.py
