import csv
import io
import os

from datetime import datetime, timezone
from functools import wraps
from pathlib import Path

from flask import (
	Flask, render_template, request, redirect, url_for, 
	jsonify, send_file, Response
)

from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Columns and order for tables and CSV export ---
FIELDNAMES = [
	"timestamp",
	"name",
	"age",
	"q_arm_experience",
	"q_control",
	"q_comfort",
	"assigned_group",
]

# --- Basic auth ---
USERNAME = "studyowner"
PASSWORD = "password" # change before deploying

def check_auth(u, p):
	return u == USERNAME and p == PASSWORD

def authenticate():
	"""Send 401 so browser prompts for username and password."""
	return Response(
		"Authentication required",
		401,
		{"WWW-Authenticate": 'Basic realm="Login Required"'}
	)

def requires_auth(fn):
	"""Require username and password before accessing this route."""
	@wraps(fn)
	def wrapper(*args, **kwargs):
		auth = request.authorization
		if not auth or not check_auth(auth.username, auth.password):
			return authenticate()
		return fn(*args, **kwargs)
	return wrapper

# --- Database config ---
db_url = os.getenv("DATABASE_URL", "sqlite:///./local.db")
engine = create_engine(db_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# --- SQLAlchemy model ---
class SurveyResponse(Base):
	__tablename__ = "responses"
	id = Column(Integer, primary_key=True)
	timestamp = Column(DateTime(timezone=True), 
		server_default=text("CURRENT_TIMESTAMP"))
	name = Column(String(255), nullable=False)
	age = Column(Integer, nullable=False)
	q_arm_experience = Column(String(50), nullable=False)
	q_control = Column(String(50), nullable=False)
	q_comfort = Column(String(50), nullable=False)
	assigned_group = Column(String(50), nullable=False)

with engine.begin() as conn:
	Base.metadata.create_all(conn)

app = Flask(__name__)

def assign_group(exp_level: str, comfort: str) -> str:
        """
        Basic adaptive branching:
        - never used a robotic arm OR very_uncomfortable        -> tutorial
        - demo_only AND neutral/comfortable                     -> standard
        - often AND comfortable/very_comfortable                -> advanced
        - fallback                                              -> standard
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
	"""Landing page with nav to all survey and researcher routes."""
	return render_template("home.html")

@app.route("/survey", methods=["GET", "POST"])
def survey():
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

		# save to DB
		with SessionLocal() as db:
			db.add(SurveyResponse(
				timestamp=datetime.now(timezone.utc),
				name=name,
				age=int(age),
				q_arm_experience=q_arm_experience,
				q_control=q_control,
				q_comfort=q_comfort,
				assigned_group=group,
			))
			db.commit()

		# show assigned group on success page 
		return redirect(url_for("filled", group=group))
                                
	return render_template("survey.html")

@app.route("/filled")
def filled():
	return render_template("filled.html", group=request.args.get("group", ""))
                        
@app.route("/responses")
@requires_auth
def responses():
	with SessionLocal() as db:
		items = (
			db.query(SurveyResponse)
			.order_by(SurveyResponse.timestamp.desc())
			.all()
		)

	rows = [
		{
			"timestamp": r.timestamp.isoformat() if r.timestamp else "",
			"name": r.name,
			"age": r.age,
			"q_arm_experience": r.q_arm_experience,
			"q_control": r.q_control,
			"q_comfort": r.q_comfort,
			"assigned_group": r.assigned_group,
		}
		for r in items
	]

	totals = {
		"count": len(rows),
		"by_group": {
			"tutorial": sum(1 for r in rows if r.get("assigned_group") 
				 == "tutorial"),
			"standard": sum(1 for r in rows if r.get("assigned_group") 
				== "standard"),
			"advanced": sum(1 for r in rows if r.get("assigned_group") 
				== "advanced"),
		},
	}	

	return render_template(
		"responses.html",
		rows=rows,
		fieldnames=FIELDNAMES,
		totals=totals,
	)

@app.route("/responses.csv")
@requires_auth
def responses_csv():
	"""Download responses (results) as CSV (authenticated)."""
	with SessionLocal() as db:
		data = (
			db.query(SurveyResponse)
			.order_by(SurveyResponse.timestamp.desc())
			.all()
		)
	
	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(FIELDNAMES) # header row

	for r in data:
		writer.writerow([
			r.timestamp.isoformat() if r.timestamp else "",
			r.name,
			r.age,
			r.q_arm_experience,
			r.q_control,
			r.q_comfort, 
			r.assigned_group
		])

	response = Response(output.getvalue(), mimetype="text/csv")
	response.headers["Content-Disposition"] = "attachment; filename=results.csv"
	return response

@app.route("/api/responses")
def api_responses():
	with SessionLocal() as db:
		data = (
			db.query(SurveyResponse)
			.order_by(SurveyResponse.timestamp.desc())
			.all()
		)

	out = [
		{
			"timestamp": r.timestamp.isoformat() if r.timestamp else "",
			"name": r.name,
			"age": r.age,
			"q_arm_experience": r.q_arm_experience,
			"q_control": r.q_control,
			"q_comfort": r.q_comfort,
			"assigned_group": r.assigned_group,
		}
		for r in data
	]
	return jsonify(out)

@app.route("/api/submit", methods=["POST"])
def api_submit():
	data = request.get_json(silent=True) or {}
	name = (data.get("name") or "").strip()
	age = (data.get("age") or "").strip()
	q_arm_experience = data.get("q_arm_experience") or ""
	q_control = data.get("q_control") or ""
	q_comfort = data.get("q_comfort") or ""

	if not name or not age.isdigit():
		return jsonify({"error": "Invalid input"}), 400

	group = assign_group(q_arm_experience, q_comfort)

	with SessionLocal() as db:
		db.add(SurveyResponse(
			timestamp=datetime.now(timezone.utc),
			name=name,
			age=int(age),
			q_arm_experience=q_arm_experience,
			q_control=q_control,
			q_comfort=q_comfort,
			assigned_group=group
		))
		db.commit()

	return jsonify({"status": "ok", "assigned_group": group})

if __name__ == "__main__":
	app.run(debug=True)
