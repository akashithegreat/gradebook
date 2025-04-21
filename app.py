from flask import Flask, render_template, request, redirect, url_for, session, flash
import networkx as nx
import itertools

app = Flask(__name__)
app.secret_key = "supersecretkey123"

assignment_structure = []
grades = {}

sample_grades = {
    "Akash": [(20, 88), (30, 92)],
    "Keya": [(25, 90), (25, 95)],
    "Jamal": [(30, 70), (30, 82)],
    "Emily": [(40, 85), (20, 78)],
    "Li Wei": [(30, 93), (20, 89)],
    "Aisha": [(25, 80), (25, 85)],
    "Ryan": [(35, 76), (30, 81)],
    "Priya": [(20, 91), (30, 94)],
    "Marcus": [(25, 68), (35, 73)],
    "Sakura": [(30, 88), (25, 90)],
}

students_db = {
    name: name.lower().replace(" ", "") + "123"
    for name in sample_grades
}

TEACHER_PASSWORD = "teacher123"

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/teacher")
def teacher_home():
    student_list = []
    for name in students_db:
        student_grades = grades.get(name, [])
        if student_grades:
            total = sum(w * s for _, w, s in student_grades)
            weight_sum = sum(w for _, w, _ in student_grades)
            grade = round(total / weight_sum, 2) if weight_sum > 0 else 0
        else:
            grade = "N/A"

        student_list.append({"name": name, "grade": grade})

    return render_template("teacher_home.html", students=student_list)


@app.route("/student")
def student_home():
    return render_template("student_home.html")

@app.route("/define-structure", methods=["GET", "POST"])
def define_structure():
    if request.method == "POST":
        name = request.form.get("name")
        weight = float(request.form.get("weight"))
        assignment_structure.append({"name": name, "weight": weight})
        flash(f"Added: {name} ({weight}%)", "success")

    total_weight = sum(a["weight"] for a in assignment_structure)
    return render_template("define_structure.html", structure=assignment_structure, total=total_weight)

@app.route("/add/<student_name>", methods=["GET", "POST"])
def add_grade_for_student(student_name):
    if request.method == 'POST':
        assignment = request.form["assignment"]
        score = float(request.form["score"])

        for a in assignment_structure:
            if a["name"] == assignment:
                weight = a["weight"]
                break
        else:
            flash("Assignment not found", "danger")
            return redirect(url_for("teacher_home"))

        if student_name not in grades:
            grades[student_name] = []

        grades[student_name].append((assignment, weight, score))
        return redirect(url_for('teacher_home'))

    return render_template("add_grade_for_student.html", student=student_name, assignments=assignment_structure)


@app.route("/home")
def index():
    return render_template('index.html', students=sample_grades.keys())

@app.route("/view/<student>")
def view_grade(student):
    student_grades = grades.get(student, [])
    if not student_grades:
        flash("No grades recorded for this student yet.", "info")
        return render_template("view_grade.html", student=student, grades=[], final=None)

    total = sum(w * s for _, w, s in student_grades)
    weight_sum = sum(w for _, w, _ in student_grades)
    final = round(total / weight_sum, 2) if weight_sum else 0

    return render_template("view_grade.html", student=student, grades=student_grades, final=final)



@app.route("/what_if", methods=["GET", "POST"])
def what_if():
    student_name = session.get("user")
    if not student_name:
        flash("Not logged in.", "danger")
        return redirect(url_for("landing"))

    result = None
    current_grades = grades.get(student_name, [])

    completed = []
    remaining = []

    used_names = set()

    for a in assignment_structure:
        matched = False
        for (name, w, s) in current_grades:
            if name == a["name"]:
                completed.append({ "name": name, "weight": w, "score": s })
                used_names.add(name)
                matched = True
                break
        if not matched:
            remaining.append(a)

    if request.method == "POST":
        simulated_data = [(c["weight"], c["score"]) for c in completed]
        for item in remaining:
            score_str = request.form.get(f"score_{item['name']}")
            if score_str:
                score = float(score_str)
                simulated_data.append((item["weight"], score))

        total_weight = sum(w for w, _ in simulated_data)
        weighted_sum = sum(s * (w / 100) for w, s in simulated_data)

        if total_weight > 100:
            flash("Total weight exceeds 100. Adjust the inputs.", "warning")
        elif total_weight > 0:
            result = round((weighted_sum / total_weight) * 100, 2)
        else:
            flash("Please enter at least one score.", "warning")

    return render_template(
        "what_if.html",
        student_name=student_name,
        completed=completed,
        assignments=remaining,
        result=result
    )





@app.route("/score_combinations", methods=["GET", "POST"])
def score_combinations():
    valid_combos = []
    result = None
    student_name = ""
    target = 90

    if request.method == "POST":
        student_name = request.form.get("student_name")
        target = float(request.form.get("target"))
        current_grades = sample_grades.get(student_name, [])
        current_score = sum(s * (w / 100) for w, s in current_grades)
        current_weight = sum(w for w, _ in current_grades)

        remaining = [a for a in assignment_structure if not any(abs(a["weight"] - w) < 0.01 for w, _ in current_grades)]
        score_options = [70, 75, 80, 85, 90, 95, 100]

        all_possibilities = list(itertools.product(score_options, repeat=len(remaining)))

        for combo in all_possibilities:
            total_weight = current_weight
            total_score = current_score

            for i, score in enumerate(combo):
                weight = remaining[i]["weight"]
                total_weight += weight
                total_score += (score * weight / 100)

            if total_weight <= 100 and (total_score / total_weight) * 100 >= target:
                labeled_combo = [(remaining[i]["name"], remaining[i]["weight"], combo[i]) for i in range(len(combo))]
                valid_combos.append((labeled_combo, round((total_score / total_weight) * 100, 2)))

        result = f"{len(valid_combos)} combinations found"

    return render_template("score_combinations.html", result=result, combos=valid_combos)

@app.route("/login/<role>", methods=["GET", "POST"])
def login(role):
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if role == "teacher":
            if password == TEACHER_PASSWORD:
                session["user"] = "teacher"
                return redirect(url_for("teacher_home"))
            else:
                flash("Invalid teacher password", "danger")

        elif role == "student":
            if name in students_db and students_db[name] == password:
                session["user"] = name
                return redirect(url_for("student_home"))
            else:
                flash("Invalid student name or password", "danger")

    return render_template("login.html", role=role)

@app.route("/strategy/<student_name>")
def strategy(student_name):
    target = float(request.args.get("target", 90))

    student_grades = grades.get(student_name, [])
    completed = []
    remaining = []

    for a in assignment_structure:
        matched = False
        for (name, w, s) in student_grades:
            if name == a["name"]:
                completed.append({ "name": name, "weight": w, "score": s })
                matched = True
                break
        if not matched:
            remaining.append(a)

    current_score = sum(c["score"] * (c["weight"] / 100) for c in completed)
    current_weight = sum(c["weight"] for c in completed)
    remaining_weight = 100 - current_weight
    current_avg = round((current_score / current_weight) * 100, 1) if current_weight > 0 else 0
    needed_avg = round((target - current_score) / (remaining_weight / 100), 1) if remaining_weight > 0 else 0

    # Best Path (assign needed_avg to all remaining)
    best_path = []
    for r in remaining:
        best_path.append({
            "name": r["name"],
            "weight": r["weight"],
            "needed_score": needed_avg
        })

    estimated_final = round(current_score + sum(r["weight"] * (needed_avg / 100) for r in remaining), 1)

    # DP score combos
    from itertools import product

    possible_scores = [100, 95, 90, 85, 80]
    dp_valid_combos = []

    for combo in product(possible_scores, repeat=len(remaining)):
        weighted = sum(combo[i] * (remaining[i]["weight"] / 100) for i in range(len(combo)))
        total = current_score + weighted
        if total >= target:
            dp_valid_combos.append({
                "scores": list(zip([r["name"] for r in remaining], combo)),
                "final": round(total, 1)
            })

    return render_template(
        "strategy.html",
        student=student_name,
        current_avg=current_avg,
        current_weight=current_weight,
        remaining_weight=remaining_weight,
        target=target,
        needed_avg=needed_avg,
        best_path=best_path,
        estimated_final=estimated_final,
        dp_valid_combos=dp_valid_combos[:3],  # only show top 3
        completed=completed
    )



if __name__ == '__main__':
    app.run(debug=True, port=5003)