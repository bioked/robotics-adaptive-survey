import json
import sys
from pathlib import Path

# make sure pytest can find app.py by adding the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app import app

def client():
	app.config["TESTING"] = True
	return app.test_client()

def test_home():
	c = client()
	r = c.get("/")
	assert r.status_code == 200

def test_survey_get():
	c = client()
	r = c.get("/survey")
	assert r.status_code == 200

def test_api_responses_get():
	c = client()
	r = c.get("/api/responses")
	assert r.status_code == 200
	assert isinstance(r.get_json(), list)

def test_api_submit_post_success():
	c = client()
	payload = {
		"name": "P0",
		"age": "99",
		"q_arm_experience": "demo_only",
		"q_control": "joystick",
		"q_comfort": "comfortable",
	}
	r = c.post("/api/submit", data=json.dumps(payload), content_type="application/json")
	assert r.status_code == 200
	data = r.get_json()
	assert data.get("status") == "ok"
	assert data.get("assigned_group") in {"tutorial", "standard", "advanced"}

