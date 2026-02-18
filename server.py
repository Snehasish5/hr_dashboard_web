"""
Standalone HR Attrition Dashboard Server
No external dependencies required — uses Python's built-in http.server.

Usage:
    python3 server.py

Then open http://localhost:8000 in your browser.

For production, use the FastAPI version:
    pip install -r requirements.txt
    uvicorn main:app --reload
"""

import csv, json, os
from collections import Counter, defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DATA_PATH = os.path.join(os.path.dirname(__file__), "data.csv")
EDUCATION_MAP = {"1": "Below College", "2": "College", "3": "Bachelor", "4": "Master", "5": "Doctor"}

# ── Data Loader ──────────────────────────────────────────────────────────────
def load_data(gender=None, job_role=None, education=None, department=None):
    rows = []
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if gender and row["Gender"] != gender: continue
            if job_role and row["JobRole"] != job_role: continue
            if education and row["Education"] != education: continue
            if department and row["Department"] != department: continue
            rows.append(row)
    return rows

def get_params(qs):
    p = parse_qs(qs)
    return {
        "gender": p.get("gender", [None])[0],
        "job_role": p.get("job_role", [None])[0],
        "education": p.get("education", [None])[0],
        "department": p.get("department", [None])[0],
    }

# ── API Handlers ─────────────────────────────────────────────────────────────
def api_filters():
    rows = load_data()
    return {
        "genders": sorted(set(r["Gender"] for r in rows)),
        "job_roles": sorted(set(r["JobRole"] for r in rows)),
        "educations": [{"value": k, "label": v} for k, v in sorted(EDUCATION_MAP.items())],
        "departments": sorted(set(r["Department"] for r in rows)),
    }

def api_kpis(p):
    rows = load_data(**p)
    total = len(rows)
    if total == 0:
        return {"total": 0, "attrition_rate": 0, "avg_age": 0, "avg_income": 0, "avg_satisfaction": 0}
    attr = sum(1 for r in rows if r["Attrition"] == "Yes")
    return {
        "total": total,
        "attrition_rate": round(attr / total * 100, 1),
        "avg_age": round(sum(int(r["Age"]) for r in rows) / total, 1),
        "avg_income": round(sum(int(r["MonthlyIncome"]) for r in rows) / total),
        "avg_satisfaction": round(sum(int(r["JobSatisfaction"]) for r in rows) / total, 2),
    }

def api_attrition_dept(p):
    rows = load_data(**p)
    total = Counter(); attr = Counter()
    for r in rows:
        total[r["Department"]] += 1
        if r["Attrition"] == "Yes": attr[r["Department"]] += 1
    labels = sorted(total.keys())
    return {"labels": labels, "total": [total[l] for l in labels], "attrition": [attr[l] for l in labels],
            "rate": [round(attr[l]/total[l]*100,1) if total[l] else 0 for l in labels]}

def api_attrition_jobrole(p):
    rows = load_data(**p)
    total = Counter(); attr = Counter()
    for r in rows:
        total[r["JobRole"]] += 1
        if r["Attrition"] == "Yes": attr[r["JobRole"]] += 1
    labels = sorted(total.keys())
    return {"labels": labels, "total": [total[l] for l in labels], "attrition": [attr[l] for l in labels],
            "rate": [round(attr[l]/total[l]*100,1) if total[l] else 0 for l in labels]}

def api_age_dist(p):
    rows = load_data(**p)
    bins = list(range(18, 65, 5)); labels = [f"{b}-{b+4}" for b in bins]
    tc = [0]*len(bins); ac = [0]*len(bins)
    for r in rows:
        idx = min((int(r["Age"])-18)//5, len(bins)-1)
        if 0 <= idx < len(bins):
            tc[idx] += 1
            if r["Attrition"] == "Yes": ac[idx] += 1
    return {"labels": labels, "total": tc, "attrition": ac}

def api_gender_split(p):
    rows = load_data(**p)
    cnt = Counter(r["Gender"] for r in rows)
    attr = Counter(r["Gender"] for r in rows if r["Attrition"] == "Yes")
    labels = sorted(cnt.keys())
    return {"labels": labels, "total": [cnt[l] for l in labels], "attrition": [attr[l] for l in labels]}

def api_income_role(p):
    rows = load_data(**p)
    role_income = defaultdict(list)
    for r in rows: role_income[r["JobRole"]].append(int(r["MonthlyIncome"]))
    labels = sorted(role_income.keys())
    return {"labels": labels, "avg_income": [round(sum(role_income[l])/len(role_income[l])) if role_income[l] else 0 for l in labels]}

def api_satisfaction(p):
    rows = load_data(**p)
    labels = ["1 - Low","2 - Medium","3 - High","4 - Very High"]
    stayed = [0,0,0,0]; left = [0,0,0,0]
    for r in rows:
        idx = int(r["JobSatisfaction"])-1
        if r["Attrition"] == "Yes": left[idx] += 1
        else: stayed[idx] += 1
    return {"labels": labels, "stayed": stayed, "left": left}

def api_overtime(p):
    rows = load_data(**p)
    data = {"Yes": {"Yes":0,"No":0}, "No": {"Yes":0,"No":0}}
    for r in rows: data[r["OverTime"]][r["Attrition"]] += 1
    return {"labels": ["With Overtime","Without Overtime"],
            "stayed": [data["Yes"]["No"],data["No"]["No"]],
            "left": [data["Yes"]["Yes"],data["No"]["Yes"]]}

def api_edu_field(p):
    rows = load_data(**p)
    cnt = Counter(r["EducationField"] for r in rows)
    attr = Counter(r["EducationField"] for r in rows if r["Attrition"] == "Yes")
    labels = sorted(cnt.keys())
    return {"labels": labels, "total": [cnt[l] for l in labels], "attrition": [attr[l] for l in labels]}

def api_years_attrition(p):
    rows = load_data(**p)
    yt = Counter(); ya = Counter()
    for r in rows:
        y = int(r["YearsAtCompany"]); yt[y] += 1
        if r["Attrition"] == "Yes": ya[y] += 1
    mx = max(yt.keys()) if yt else 0
    labels = list(range(0, min(mx+1,41)))
    return {"labels": labels, "attrition_rate": [round(ya[y]/yt[y]*100,1) if yt[y] else 0 for y in labels], "total": [yt[y] for y in labels]}

def api_worklife(p):
    rows = load_data(**p)
    metrics = ["JobSatisfaction","EnvironmentSatisfaction","RelationshipSatisfaction","WorkLifeBalance","JobInvolvement"]
    labels = ["Job Satisfaction","Environment","Relationships","Work-Life Balance","Job Involvement"]
    stayed_avgs, left_avgs = [], []
    for m in metrics:
        stayed = [int(r[m]) for r in rows if r["Attrition"] == "No"]
        left = [int(r[m]) for r in rows if r["Attrition"] == "Yes"]
        stayed_avgs.append(round(sum(stayed)/len(stayed),2) if stayed else 0)
        left_avgs.append(round(sum(left)/len(left),2) if left else 0)
    return {"labels": labels, "stayed": stayed_avgs, "left": left_avgs}

# ── HTTP Handler ─────────────────────────────────────────────────────────────
ROUTES = {
    "/api/filters": (api_filters, False),
    "/api/kpis": (api_kpis, True),
    "/api/attrition-by-department": (api_attrition_dept, True),
    "/api/attrition-by-jobrole": (api_attrition_jobrole, True),
    "/api/age-distribution": (api_age_dist, True),
    "/api/gender-split": (api_gender_split, True),
    "/api/income-by-role": (api_income_role, True),
    "/api/satisfaction-distribution": (api_satisfaction, True),
    "/api/overtime-attrition": (api_overtime, True),
    "/api/education-field": (api_edu_field, True),
    "/api/years-attrition": (api_years_attrition, True),
    "/api/worklife-balance": (api_worklife, True),
}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), "static"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ROUTES:
            fn, needs_params = ROUTES[path]
            try:
                result = fn(get_params(parsed.query)) if needs_params else fn()
                body = json.dumps(result).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", len(body))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_error(500, str(e))
        elif path == "/" or path == "":
            self.path = "/index.html"
            super().do_GET()
        else:
            super().do_GET()

    def log_message(self, fmt, *args):
        print(f"  {args[0]} {args[1]}")

if __name__ == "__main__":
    port = 8000
    print(f"\n{'='*55}")
    print(f"  HR Attrition Dashboard")
    print(f"  Running at: http://localhost:{port}")
    print(f"  No dependencies required!")
    print(f"{'='*55}\n")
    HTTPServer(("", port), Handler).serve_forever()