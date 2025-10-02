from flask import Flask, render_template, request, redirect, url_for
import csv
from pathlib import Path
from datetime import datetime
        
app = Flask(__name__)
                        
CSV_PATH = Path("survey_responses.csv")
FIELDNAMES = ["timestamp", "name", "age",
		"q_arm_experience", "q_control", "q_comfort",
		"assigned_group"]
        
def init_csv():
	"""Create CSV with header if there isn't one already."""   
	if not CSV_PATH.exists():
		with CSV_PATH.open("w", newline="", encoding="utf-8") as f:   
			writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
			writer.writeheader()

def assign_group(exp_level: str, comfort: str) -> str:
	"""
	Basic adaptive branching:
	- never used robotic arm OR very_uncomfortable  -> tutorial
	- demo_only AND neutral/comfortable             -> standard
	- often AND (comfortable/very)                  -> advanced
	- fallback                                      -> standard
	"""
	if exp_level == "never" or comfort == "very_uncomfortable":
		return "tutorial"
	if exp_level == "demo_only" and comfort in {"neutral", "comfortable", "very_comfortable"}:
		return "standard"
	if exp_level == "often" and comfort in {"comfortable", "very_comfortable"}:
		return "advanced"
	return "standard"
        
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
			"timestamp": datetime.utcnow().isoformat(timespec="seconds"),
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
                        
@app.route("/")
def home():
	return "Welcome. Visit /survey to get started."

@app.route("/filled")
def filled():
	return render_template("filled.html", group=request.args.get("group", ""))
                        
if __name__ == "__main__":
	app.run(debug=True)
