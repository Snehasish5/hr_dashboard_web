# HR Attrition Intelligence Dashboard

A full-stack interactive data visualization dashboard for IBM's HR Employee Attrition dataset. Built with FastAPI backend and vanilla JavaScript frontend featuring real-time filtering and 10 interactive Chart.js visualizations.

**Features**

- **Real-time Filtering*: 4 dropdown filters (Gender, Department, Job Role, Education Level)
- **10 Interactive Charts*: Bar, Stacked Bar, Donut, Polar Area, Radar, Line, Histogram
- **5 Live KPI Cards*: Total Employees, Attrition Rate, Avg Age, Avg Income, Job Satisfaction
- **Responsive Design*: Works on desktop, tablet, and mobile (768px, 480px breakpoints)
- **Dark Industrial Theme*: Custom yellow accent colors, Space Mono + Syne fonts
- **Zero Build Step*: Pure HTML/CSS/JS frontend, no npm/webpack required
- **REST API*: 12 endpoints with query parameter filtering

**Project Structure**

```
hr-dashboard/
├── data.csv              ← IBM HR dataset (1,470 employees, 35 features)
├── main.py               ← FastAPI backend (production-ready)
├── server.py             ← Standalone Python server (zero dependencies)
├── requirements.txt      ← Python dependencies
├── render.yaml           ← Render.com one-click deploy config
├── Procfile              ← Heroku/Railway deploy config
├── dev.sh                ← Local development script
├── README.md             ← This file
└── static/
    └── index.html        ← Frontend (self-contained, ~1200 lines)
```

**Quick Start**

**Option 1*: Zero Dependencies (Instant Start)

- python3 server.py

- Opens at `http://localhost:8000` — uses Python's built-in `http.server`, no pip install needed.


**Option 2: FastAPI Development (Hot Reload)**

```bash

**Install dependencies:**
- pip install -r requirements.txt

# Or manually:
- uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Opens at `http://localhost:8000` with auto-reload on code changes.

**Option 3: Production Mode**

```bash
- pip install -r requirements.txt
- uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1
```

**Deploy to Cloud**

**Deploy to Render (Recommended)**

**One-Click Deploy:**
1. Push code to GitHub
2. Go to [Render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml` and deploys ✅

**Manual Setup:**
1. Create new Web Service on Render
2. Connect GitHub repo
3. Set configuration:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1`
   - **Health Check Path**: `/health`
4. Click "Create Web Service"

- Your app will be live at: `https://YOUR-APP-NAME.onrender.com`


**Dataset**

**Source*: IBM Watson HR Employee Attrition Dataset  
**Records*: 1,470 employees  
**Features*: 35 attributes including:
- Demographics: Age, Gender, Marital Status, Education
- Job Info: Department, Job Role, Job Level, Years at Company
- Compensation: Monthly Income, Hourly Rate, Stock Options
- Satisfaction: Job Satisfaction, Work-Life Balance, Environment Satisfaction
- Attrition: Yes/No (target variable)

**🛠 API Documentation**

**Base URL**
- **Local:* `http://localhost:8000`
- **Production:* `https://YOUR-APP.onrender.com`

**Health Check**
```bash
- GET /health
- HEAD /health
```
Returns: `{"status": "ok"}`

**Filter Options**

```bash
- GET /api/filters
```
- **Returns available filter values:*

```json
{
  "genders": ["Female", "Male"],
  "departments": ["Human Resources", "Research & Development", "Sales"],
  "job_roles": ["Healthcare Representative", "Human Resources", ...],
  "educations": [
    {"value": "1", "label": "Below College"},
    {"value": "2", "label": "College"},
  ]
}
```

**KPIs (Key Performance Indicators)**

```bash
GET /api/kpis?gender=Female&department=Sales
```
**Query Parameters (all optional):**

- **`gender`:* Female | Male
- **`department`:* Human Resources | Research & Development | Sales
- **`job_role`:* Any role from `/api/filters`
- **`education`:* 1-5

**Returns:*

```json
{
  "total": 189,
  "attrition_rate": 20.1,
  "avg_age": 37.2,
  "avg_income": 6972,
  "avg_satisfaction": 2.78
}
```

**Chart Data Endpoints**

All endpoints support the same query parameters as `/api/kpis`.

| Endpoint | Description | Returns |
|----------|-------------|---------|
| `/api/attrition-by-department` | Attrition breakdown by department | labels, total, attrition, rate |
| `/api/attrition-by-jobrole` | Attrition breakdown by job role | labels, total, attrition, rate |
| `/api/age-distribution` | Employee age histogram | labels, total, attrition |
| `/api/gender-split` | Gender distribution | labels, total, attrition |
| `/api/income-by-role` | Average income by role | labels, avg_income |
| `/api/satisfaction-distribution` | Job satisfaction levels | labels, stayed, left |
| `/api/overtime-attrition` | Overtime vs attrition | labels, stayed, left |
| `/api/education-field` | Education field distribution | labels, total, attrition |
| `/api/years-attrition` | Tenure vs attrition rate | labels, attrition_rate, total |
| `/api/worklife-balance` | Work-life metrics radar | labels, stayed, left |

**Example API Call**

```bash
- curl "http://localhost:8000/api/kpis?gender=Male&department=Sales"
```

**Frontend Features**

**Navigation*

- Smooth scroll to sections (Overview, Attrition, Workforce, Satisfaction, Tenure)
- Sticky header with transparency on scroll
- Mobile-responsive hamburger menu (768px breakpoint)

**Filter Panel*

- 4 custom-styled dropdowns with yellow accent theme
- Clear selection option in each dropdown
- "Reset All" button to clear all filters
- Active filter display with employee count

**Charts**

1. **Attrition by Department** (Stacked Bar)
2. **Overtime Impact** (Stacked Bar)
3. **Gender Distribution** (2-ring Donut)
4. **Attrition by Job Role** (Horizontal Bar with conditional coloring)
5. **Age Distribution** (Histogram)
6. **Job Satisfaction vs Attrition** (Grouped Bar)
7. **Avg Income by Role** (Horizontal Bar, multi-color)
8. **Education Field Spread** (Polar Area)
9. **Attrition Rate by Tenure** (Dual-axis Line)
10. **Work-Life Metrics** (Radar)

All charts update instantly when filters change via async API calls.

**Tech Stack**

**Backend*
- **FastAPI** 0.104+ — Modern Python web framework
- **Uvicorn** — ASGI server
- **Python 3.11+** — Core language

**Frontend*
- **Vanilla JavaScript** — No frameworks, just fetch API
- **Chart.js 4.4** — Interactive canvas-based charts
- **CSS Grid/Flexbox** — Modern responsive layout
- **Google Fonts** — Space Mono (mono), Syne (sans)

**Deployment*
- **Render.com** — Primary hosting (free tier available)


**Responsive Breakpoints**

- **Desktop** (>1200px): 5-column KPI grid, 3-column charts
- **Tablet** (768px-1200px): 3-column KPI grid, 2-column charts
- **Mobile** (480px-768px): 2-column KPI grid, single-column charts
- **Small Phone** (<480px): Stacked layout, compressed nav


**Development**

**Local Setup*
```bash
# Clone repo
- git clone <your-repo-url>
- cd hr-dashboard

# Install dependencies
- pip install -r requirements.txt

# Or manually with hot reload
- uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Troubleshooting**

**Render Deployment Issues**

**"No open ports detected"*

- Fixed: `render.yaml` uses `--host 0.0.0.0 --port $PORT`
- Fixed: Health check endpoint `/health` supports HEAD requests

**"Application failed to respond"*

- Check Render logs for Python errors
- Verify `data.csv` is committed to git
- Ensure `requirements.txt` has correct versions

**"Build failed"*

- Check Python version (needs 3.7+)
- Verify all dependencies in `requirements.txt`

**Local Development Issues**

**"ERR_ADDRESS_INVALID when accessing 0.0.0.0:8000"*

- Use `http://localhost:8000` in browser (not `0.0.0.0`)
- Server binds to `0.0.0.0` but you access via `localhost`

**"Charts not loading"*

- Check browser console for JavaScript errors
- Verify API endpoints return 200 status
- Ensure CORS is enabled (already configured in `main.py`)

**"Dropdown not scrolling"*

- Fixed: Dropdowns have `max-height: 280px` with custom scrollbar