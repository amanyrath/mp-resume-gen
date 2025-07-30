from flask import Flask, request, render_template, send_file
import pandas as pd
import tempfile
import os
from weasyprint import HTML

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    file = request.files['ticklist']
    name = request.form['name']
    email = request.form['email']
    bio = request.form['bio']

    df = pd.read_csv(file)

    # Process ticks summary
    total_routes = len(df)
    max_grade = df['Rating'].dropna().max()
    areas = df['Location'].dropna().str.split(' > ').str[-1].value_counts().head(5)
    notable = df.head(5)[['Route', 'Rating', 'Location', 'Date']].to_dict(orient='records')

    html = render_template('resume.html', name=name, email=email, bio=bio,
                           total_routes=total_routes, max_grade=max_grade,
                           areas=areas, notable=notable)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        HTML(string=html).write_pdf(f.name)
        return send_file(f.name, as_attachment=True, download_name='climbing_resume.pdf')

if __name__ == '__main__':
    app.run(debug=True)
