## 🧗 MP Ticks Analysis

Analyze your personal climbing progression using Mountain Project (MP) tick data.

### Overview
This project parses your exported MP ticklist CSV and produces visualizations and statistics that show trends in your climbing over time. It includes:

Grade progression analysis

Rolling average of hardest climbs

Most frequently climbed locations

Style breakdown (e.g., Lead, TR, Flash, Onsight)

Optionally, a resume-style summary of your climbing experience

### 📁 Project Structure
```bash
Copy
Edit
mp-ticks-analysis/
│
├── data/
│   └── ticks.csv               # Your exported Mountain Project ticklist
│
├── notebooks/
│   └── analysis.ipynb          # Main analysis notebook
│
├── app/                        # Optional: Flask app for UI/resume
│   ├── app.py
│   └── templates/
│
├── charts/                     # Output plots and visualizations
│
├── utils/
│   └── parsing.py              # Functions for loading and cleaning tick data
│
├── requirements.txt
└── README.md
```
### 🧰 Getting Started
1. Export Your Ticks
Go to Mountain Project → Your Profile → Ticks → "Export to CSV"

Save the file as data/ticks.csv.

2. Set Up Environment
```bash
Copy
Edit
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### 3. Run the Analysis
Open the Jupyter notebook:

```bash
Copy
Edit
jupyter notebook notebooks/analysis.ipynb
```

Or run the script:

```bash
Copy
Edit
python -m analysis.main
```

📊 Features
Rolling Grade Progression
Visualize your hardest grades over time using a rolling average.

Monthly Climbing Trends
Track how often and how hard you climbed each month.

Top Locations
Find out where you climb the most and what level you’re climbing there.

Resume Generator (Optional)
Create a climbing resume summarizing your tick history and highlights.

📦 Dependencies
pandas

matplotlib

seaborn

scikit-learn (for regression line, optional)

Flask (only if using the web app)

Install all with:

```bash
Copy
Edit
pip install -r requirements.txt
```

### 📝 Future Work
Climbing discipline breakdown (bouldering, sport, trad)

Grade distribution histogram

Geo heatmaps of climb locations

Exporting climbing resume as PDF

### 📬 Contact
Created by Alexis Manyrath — feel free to reach out if you want help analyzing your own ticklist!

