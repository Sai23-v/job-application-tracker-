from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

def db():
    return sqlite3.connect("jobs.db")

# Create table
with db() as con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            status TEXT
        )
    """)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Tracker</title>
    <style>
        body{font-family:Arial;padding:20px}
        input,select,button{padding:8px;margin:5px}
        table{width:100%;border-collapse:collapse;margin-top:20px}
        th,td{border:1px solid #ccc;padding:8px;text-align:center}
        .dash{display:flex;gap:10px;margin-bottom:20px}
        .card{padding:10px;background:#f4f4f4;border-radius:8px}
        .danger{background:#ff4d4d;color:white;border:none}
    </style>
</head>
<body>

<h2>Job Application Tracker</h2>

<div class="dash">
    <div class="card">Total: {{ counts.total }}</div>
    <div class="card">Applied: {{ counts.Applied }}</div>
    <div class="card">Interview: {{ counts.Interview }}</div>
    <div class="card">Offer: {{ counts.Offer }}</div>
    <div class="card">Rejected: {{ counts.Rejected }}</div>
</div>

<form method="POST">
    <input name="company" placeholder="Company" required>
    <input name="role" placeholder="Role" required>
    <select name="status" required>
        <option>Applied</option>
        <option>Interview</option>
        <option>Offer</option>
        <option>Rejected</option>
    </select>
    <button>Add Job</button>
</form>

<table>
<tr>
    <th>Company</th>
    <th>Role</th>
    <th>Status</th>
    <th>Update</th>
    <th>Delete</th>
</tr>

{% for j in jobs %}
<tr>
    <td>{{ j[1] }}</td>
    <td>{{ j[2] }}</td>
    <td>{{ j[3] }}</td>

    <td>
        <form method="POST" action="/update/{{ j[0] }}">
            <select name="status">
                <option {{'selected' if j[3]=='Applied'}}>Applied</option>
                <option {{'selected' if j[3]=='Interview'}}>Interview</option>
                <option {{'selected' if j[3]=='Offer'}}>Offer</option>
                <option {{'selected' if j[3]=='Rejected'}}>Rejected</option>
            </select>
            <button>Save</button>
        </form>
    </td>

    <td>
        <form method="POST" action="/delete/{{ j[0] }}">
            <button class="danger">Delete</button>
        </form>
    </td>
</tr>
{% endfor %}
</table>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    con = db()
    cur = con.cursor()

    if request.method == "POST":
        cur.execute(
            "INSERT INTO jobs (company, role, status) VALUES (?,?,?)",
            (request.form["company"], request.form["role"], request.form["status"])
        )
        con.commit()
        return redirect("/")

    jobs = cur.execute("SELECT * FROM jobs").fetchall()

    counts = {"total":len(jobs),"Applied":0,"Interview":0,"Offer":0,"Rejected":0}
    for j in jobs:
        counts[j[3]] += 1

    return render_template_string(HTML, jobs=jobs, counts=counts)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    with db() as con:
        con.execute(
            "UPDATE jobs SET status=? WHERE id=?",
            (request.form["status"], id)
        )
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    with db() as con:
        con.execute("DELETE FROM jobs WHERE id=?", (id,))
    return redirect("/")

if __name__ == "__main__":
    app.run()
