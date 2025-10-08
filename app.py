from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file, Response
import csv
from pathlib import Path
from datetime import datetime, timezone

# --- Basic Auth ---
USERNAME = "studyowner"
PASSWORD = "password" # change this to something secure before deploying

def check_auth(u, p):
	return u == USERNAME and p == PASSWORD

def authenticate():
	"""Send 401 so browser asks for login credentials."""
	return Response(
		"Authentication required",
		401,
		{"WWW-Authenticate": 'Basic realm="Login Required"'}
	)

def requires_auth(fn):
	"""Decorator that adds basic password protection to a route."""
	@wraps(fn)
	def wrapper(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return fn(*args, **kwargs)
	return wrapper
        
app = Flask(__name__)
                        
CSV_PATH = Path("survey_responses.csv")
FIELDNAMES = ["timestamp", "name", "age",
		"q_arm_experience", "q_control", "q_comfort",
		"assigned_group"]
        
def init_csv():
	"""Create CSV incl. header if there isn't one already."""   
	if not CSV_PATH.exists():
		with CSV_PATH.open("w", newline="", encoding="utf-8") as f:   
			writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
			writer.writeheader()

def assign_group(exp_level: str, comfort: str) -> str:
	"""
	Basic adaptive branching:
	- never used a robotic arm OR very_uncomfortable	-> tutorial
	- demo_only AND neutral/comfortable			-> standard
	- often AND comfortable/very_comfortable		-> advanced
	- fallback						-> standard
	"""
	if exp_level == "never" or comfort == "very_uncomfortable":
		return "tutorial"
	if exp_level == "demo_only" and comfort in {"neutral", "comfortable", "very_comfortable"}:
		return "standard"
	if exp_level == "often" and comfort in {"comfortable", "very_comfortable"}:
		return "advanced"
	return "standard"
        
@app.route("/")
def home():
	"""Landing page with nav to all survey and researcher routes"""
	return render_template("home.html")

@app.route("/survey", methods=["GET", "POST"])
def survey():
	init_csv()
	if request.method == "POST":
		name = (request.form.get("name") or "").strip()
		age = (request.form.get("age") or "").strip()

		# robotics-specific questions
		q_arm_experience = request.form.get("q_arm_experience") or ""
		q_control = request.form.get("q_control") or ""
		q_comfort = request.form.get("q_comfort") or ""

		# small validation
		if not name or not age.isdigit():
			return render_template("survey.html", error="Enter your name and age (numbers only).")

		# adaptive branching
		group = assign_group(q_arm_experience, q_comfort)
                
		row = {
			"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
			"name": name,
			"age": age,
			"q_arm_experience": q_arm_experience,
			"q_control": q_control,
			"q_comfort": q_comfort,
			"assigned_group": group,
		}
		with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
			writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
			writer.writerow(row)
                
		# show assigned group on the form filled page
		return redirect(url_for("filled", group=group))
                        
	return render_template("survey.html")

@app.route("/filled")
def filled():
	return render_template("filled.html", group=request.args.get("group", ""))
                        
@app.route("/responses")
@requires_auth
def responses():
	init_csv()

	rows = []
	with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
		reader = csv.DictReader(f)
		for r in reader:
			rows.append(r)

	# Sorts table entries by timestamp (newest first)
	def parse_ts(r):
		ts = r.get("timestamp", "")
		try:
			dt = datetime.fromisoformat(ts)
			if dt.tzinfo is None:
				dt = dt.replace(tzinfo=timezone.utc)
			return dt
		except Exception:
			return datetime.min.replace(tzinfo=timezone.utc)

	rows.sort(key=parse_ts, reverse=True)

	# Records totals for each assigned group
	totals = {
		"count": len(rows),
		"by_group": {
			"tutorial": sum(1 for r in rows if r.get("assigned_group") == "tutorial"),
			"standard": sum(1 for r in rows if r.get("assigned_group") == "standard"),
			"advanced": sum(1 for r in rows if r.get("assigned_group") == "advanced"),
		},
	}	

	return render_template(
		"responses.html",
		rows=rows,
		fieldnames=FIELDNAMES,
		totals=totals,
	)

@app.route("/responses.csv")
def responses_csv():
        """Ability to download survey responses as CSV."""
        init_csv()
        # Download all responses as CSV
        return send_file(CSV_PATH, mimetype="text/csv", as_attachment=True, download_name="survey_responses.csv")

@app.route("/api/responses")
def api_responses():
	init_csv()
	with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
		rows = list(csv.DictReader(f))
	return jsonify(rows)

@app.route("/api/submit", methods=["POST"])
def api_submit():
	init_csv()
	data = request.get_json(force=True) or {}
	name = (data.get("name") or "").strip()
	age = (data.get("age") or "").strip()
	q_arm_experience = data.get("q_arm_experience") or ""
	q_control = data.get("q_control") or ""
	q_comfort = data.get("q_comfort") or ""

	if not name or not age.isdigit():
		return jsonify({"error": "Invalid input"}), 400

	group = assign_group(q_arm_experience, q_comfort)

	row = {
		"timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
		"name": name,
		"age": age,
		"q_arm_experience": q_arm_experience,
		"q_control": q_control,
		"q_comfort": q_comfort,
		"assigned_group": group,
	}
	with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
		writer.writerow(row)

	return jsonify({"status": "ok", "assigned_group": group})

if __name__ == "__main__":
	app.run(debug=True)
