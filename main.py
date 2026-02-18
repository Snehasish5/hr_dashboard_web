from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import csv
import json
from collections import Counter, defaultdict
from typing import Optional
import os

app = FastAPI(title="HR Attrition Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Load CSV ──────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), r"D:\Project\hr_dashboard\data.csv")

EDUCATION_MAP = {"1": "Below College", "2": "College", "3": "Bachelor", "4": "Master", "5": "Doctor"}

def load_data(
    gender: Optional[str] = None,
    job_role: Optional[str] = None,
    education: Optional[str] = None,
    department: Optional[str] = None,
):
    rows = []
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if gender and row["Gender"] != gender:
                continue
            if job_role and row["JobRole"] != job_role:
                continue
            if education and row["Education"] != education:
                continue
            if department and row["Department"] != department:
                continue
            rows.append(row)
    return rows


# ─── Filter Options ────────────────────────────────────────────────────────────
@app.get("/api/filters")
def get_filters():
    rows = load_data()
    return {
        "genders": sorted(set(r["Gender"] for r in rows)),
        "job_roles": sorted(set(r["JobRole"] for r in rows)),
        "educations": [
            {"value": k, "label": v}
            for k, v in sorted(EDUCATION_MAP.items(), key=lambda x: x[0])
        ],
        "departments": sorted(set(r["Department"] for r in rows)),
    }


# ─── KPI Summary ───────────────────────────────────────────────────────────────
@app.get("/api/kpis")
def get_kpis(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    total = len(rows)
    if total == 0:
        return {"total": 0, "attrition_rate": 0, "avg_age": 0, "avg_income": 0, "avg_satisfaction": 0}
    attrition = sum(1 for r in rows if r["Attrition"] == "Yes")
    avg_age = sum(int(r["Age"]) for r in rows) / total
    avg_income = sum(int(r["MonthlyIncome"]) for r in rows) / total
    avg_sat = sum(int(r["JobSatisfaction"]) for r in rows) / total
    return {
        "total": total,
        "attrition_rate": round(attrition / total * 100, 1),
        "avg_age": round(avg_age, 1),
        "avg_income": round(avg_income),
        "avg_satisfaction": round(avg_sat, 2),
    }


# ─── Attrition by Category (bar chart) ────────────────────────────────────────
@app.get("/api/attrition-by-department")
def attrition_by_department(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    dept_total = Counter()
    dept_attr = Counter()
    for r in rows:
        dept_total[r["Department"]] += 1
        if r["Attrition"] == "Yes":
            dept_attr[r["Department"]] += 1
    labels = sorted(dept_total.keys())
    return {
        "labels": labels,
        "total": [dept_total[l] for l in labels],
        "attrition": [dept_attr[l] for l in labels],
        "rate": [round(dept_attr[l] / dept_total[l] * 100, 1) if dept_total[l] else 0 for l in labels],
    }


@app.get("/api/attrition-by-jobrole")
def attrition_by_jobrole(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    role_total = Counter()
    role_attr = Counter()
    for r in rows:
        role_total[r["JobRole"]] += 1
        if r["Attrition"] == "Yes":
            role_attr[r["JobRole"]] += 1
    labels = sorted(role_total.keys())
    return {
        "labels": labels,
        "total": [role_total[l] for l in labels],
        "attrition": [role_attr[l] for l in labels],
        "rate": [round(role_attr[l] / role_total[l] * 100, 1) if role_total[l] else 0 for l in labels],
    }


# ─── Age Distribution (histogram) ─────────────────────────────────────────────
@app.get("/api/age-distribution")
def age_distribution(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    bins = list(range(18, 65, 5))
    labels = [f"{b}-{b+4}" for b in bins]
    total_counts = [0] * len(bins)
    attr_counts = [0] * len(bins)
    for r in rows:
        age = int(r["Age"])
        idx = min((age - 18) // 5, len(bins) - 1)
        if 0 <= idx < len(bins):
            total_counts[idx] += 1
            if r["Attrition"] == "Yes":
                attr_counts[idx] += 1
    return {"labels": labels, "total": total_counts, "attrition": attr_counts}


# ─── Gender Split (donut) ──────────────────────────────────────────────────────
@app.get("/api/gender-split")
def gender_split(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    cnt = Counter(r["Gender"] for r in rows)
    attr_cnt = Counter(r["Gender"] for r in rows if r["Attrition"] == "Yes")
    labels = sorted(cnt.keys())
    return {
        "labels": labels,
        "total": [cnt[l] for l in labels],
        "attrition": [attr_cnt[l] for l in labels],
    }


# ─── Monthly Income by Job Role (horizontal bar) ───────────────────────────────
@app.get("/api/income-by-role")
def income_by_role(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    role_income = defaultdict(list)
    for r in rows:
        role_income[r["JobRole"]].append(int(r["MonthlyIncome"]))
    labels = sorted(role_income.keys())
    return {
        "labels": labels,
        "avg_income": [round(sum(role_income[l]) / len(role_income[l])) if role_income[l] else 0 for l in labels],
    }


# ─── Job Satisfaction Distribution (grouped bar) ──────────────────────────────
@app.get("/api/satisfaction-distribution")
def satisfaction_distribution(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    sat_labels = ["1 - Low", "2 - Medium", "3 - High", "4 - Very High"]
    stayed = [0, 0, 0, 0]
    left = [0, 0, 0, 0]
    for r in rows:
        idx = int(r["JobSatisfaction"]) - 1
        if r["Attrition"] == "Yes":
            left[idx] += 1
        else:
            stayed[idx] += 1
    return {"labels": sat_labels, "stayed": stayed, "left": left}


# ─── Overtime vs Attrition (stacked) ──────────────────────────────────────────
@app.get("/api/overtime-attrition")
def overtime_attrition(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    data = {"Yes": {"Yes": 0, "No": 0}, "No": {"Yes": 0, "No": 0}}
    for r in rows:
        data[r["OverTime"]][r["Attrition"]] += 1
    return {
        "labels": ["With Overtime", "Without Overtime"],
        "stayed": [data["Yes"]["No"], data["No"]["No"]],
        "left": [data["Yes"]["Yes"], data["No"]["Yes"]],
    }


# ─── Education Field Distribution (polar area) ────────────────────────────────
@app.get("/api/education-field")
def education_field(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    cnt = Counter(r["EducationField"] for r in rows)
    attr = Counter(r["EducationField"] for r in rows if r["Attrition"] == "Yes")
    labels = sorted(cnt.keys())
    return {
        "labels": labels,
        "total": [cnt[l] for l in labels],
        "attrition": [attr[l] for l in labels],
    }


# ─── Years at Company vs Attrition (line) ─────────────────────────────────────
@app.get("/api/years-attrition")
def years_attrition(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    year_total = Counter()
    year_attr = Counter()
    for r in rows:
        y = int(r["YearsAtCompany"])
        year_total[y] += 1
        if r["Attrition"] == "Yes":
            year_attr[y] += 1
    max_year = max(year_total.keys()) if year_total else 0
    labels = list(range(0, min(max_year + 1, 41)))
    rates = [round(year_attr[y] / year_total[y] * 100, 1) if year_total[y] else 0 for y in labels]
    totals = [year_total[y] for y in labels]
    return {"labels": labels, "attrition_rate": rates, "total": totals}


# ─── Work-Life Balance (radar) ─────────────────────────────────────────────────
@app.get("/api/worklife-balance")
def worklife_balance(
    gender: Optional[str] = Query(None),
    job_role: Optional[str] = Query(None),
    education: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
):
    rows = load_data(gender, job_role, education, department)
    metrics = ["JobSatisfaction", "EnvironmentSatisfaction", "RelationshipSatisfaction", "WorkLifeBalance", "JobInvolvement"]
    stayed_avgs = []
    left_avgs = []
    for m in metrics:
        stayed = [int(r[m]) for r in rows if r["Attrition"] == "No"]
        left = [int(r[m]) for r in rows if r["Attrition"] == "Yes"]
        stayed_avgs.append(round(sum(stayed) / len(stayed), 2) if stayed else 0)
        left_avgs.append(round(sum(left) / len(left), 2) if left else 0)
    labels = ["Job Satisfaction", "Environment", "Relationships", "Work-Life Balance", "Job Involvement"]
    return {"labels": labels, "stayed": stayed_avgs, "left": left_avgs}


# ─── Serve Frontend ────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)