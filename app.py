from flask import Flask, request, render_template, send_file
import pandas as pd
import tempfile
import os
from weasyprint import HTML
import base64
import tempfile
import os

app = Flask(__name__)

def b64encode_filter(s):
    return base64.b64encode(s.encode()).decode()

app.jinja_env.filters['b64encode'] = b64encode_filter


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/review', methods=['POST'])
def review():
    file = request.files.get('ticklist')
    if not file:
        return "No file uploaded", 400
    df = pd.read_csv(file)

    # Save the CSV to temp file to reuse in /generate
    tmp_path = os.path.join(tempfile.gettempdir(), 'ticklist.csv')
    df.to_csv(tmp_path, index=False)

    # Top 5 leaf locations (most specific, last segment)
    top_leaf_names = df['Location'].dropna().str.split(' > ').str[-1].value_counts().head(5).index.tolist()

    # Map each leaf to its full locations
    leaf_to_full = {
        leaf: df[df['Location'].str.endswith(leaf, na=False)]['Location'].unique().tolist()
        for leaf in top_leaf_names
    }

    tmp_path = os.path.join(tempfile.gettempdir(), 'ticklist.csv')
    df.to_csv(tmp_path, index=False)


    return render_template('review.html', leaf_to_full=leaf_to_full)


@app.route('/generate', methods=['POST'])
def generate():
    tmp_path = os.path.join(tempfile.gettempdir(), 'ticklist.csv')
    df = pd.read_csv(tmp_path)

    # Filter out attempts for grade calculations
    df_valid = df[df['Style'] != 'Attempt']

    def get_max_rating(df_subset):
        if df_subset.empty or df_subset['Rating Code'].dropna().empty:
            return None
        max_code = df_subset['Rating Code'].dropna().max()
        # In case multiple rows have same max code, take first rating
        return df_subset[df_subset['Rating Code'] == max_code]['Rating'].iloc[0]

    # Process ticks summary
    total_routes = len(df)

    max_grade_overall = get_max_rating(df_valid)

    max_grade_boulder = get_max_rating(df_valid[df_valid['Style'] == 'Send'])

    max_grade_lead = get_max_rating(df_valid[(df_valid['Style'] == 'Lead') & (df_valid['Lead Style'] != 'Fell/Hung')])

    # Flash grades
    max_flash_boulder = get_max_rating(df_valid[df_valid['Style'] == 'Flash'])

    max_flash_lead = get_max_rating(df_valid[(df_valid['Style'] == 'Lead') & (df_valid['Lead Style'].isin(['Flash', 'Onsight']))])

    # Onsight grades
    max_onsight_lead = get_max_rating(df_valid[(df_valid['Style'] == 'Lead') & (df_valid['Lead Style'] == 'Onsight')])

    # Parse rollup_map from POST
    rollup_map = {
        k[len('rollup_map['):-1]: int(v)
        for k, v in request.form.items() if k.startswith("rollup_map[")
    }

    def resolve_area(location):
        if pd.isna(location):
            return None
        for full, level in rollup_map.items():
            if location == full or location.startswith(full + ' >'):
                parts = location.split(' > ')
                if level < len(parts):
                    return ' > '.join(parts[:level + 1])
        return location

    df['Resolved Area'] = df['Location'].apply(resolve_area)

    # Top 5 rolled-up areas
    areas = df['Resolved Area'].value_counts().head(5).items()

    notable = df.head(5)[['Route', 'Rating', 'Location', 'Date']].to_dict(orient='records')

    # Favorite climbs: 3 most recent with 4 stars in 'Your Stars'
    df_favs = df[df['Your Stars'] == 4].sort_values(by='Date', ascending=False).head(3)
    favorites = df_favs[['Route', 'Rating', 'Location', 'Date']].to_dict(orient='records')

    # Hardest boulders: top 3 by 'Rating Code' where Style == 'Send'
    df_boulders = df[df['Style'] == 'Send'].sort_values(by='Rating Code', ascending=False).head(3)
    hardest_boulders = df_boulders[['Route', 'Rating', 'Location', 'Date']].to_dict(orient='records')

    # Hardest leads: top 3 by 'Rating Code' where Style == 'Lead' and Lead Style != 'Fell/Hung'
    df_leads = df[(df['Style'] == 'Lead') & (df['Lead Style'] != 'Fell/Hung')]
    df_leads = df_leads.sort_values(by='Rating Code', ascending=False).head(3)
    hardest_leads = df_leads[['Route', 'Rating', 'Location', 'Date']].to_dict(orient='records')

    # Longest climbs: top 3 by Length
    df_longest = df.sort_values(by='Length', ascending=False).head(3)
    longest_climbs = df_longest[['Route', 'Rating', 'Location', 'Date', 'Length']].to_dict(orient='records')

    # Example values for the rest of the resume
    name = "Alexis M"
    email = "alexis@example.com"
    bio = "Passionate climber and data scientist."

    html = render_template('resume.html', name=name, email=email, bio=bio,
                           total_routes=total_routes,
                           max_grade=max_grade_overall,
                           max_grade_boulder=max_grade_boulder,
                           max_grade_lead=max_grade_lead,
                           max_flash_boulder=max_flash_boulder,
                           max_flash_lead=max_flash_lead,
                           max_onsight_lead=max_onsight_lead,
                           areas=areas, notable=notable, favorites=favorites,
                           hardest_boulders=hardest_boulders, hardest_leads=hardest_leads,
                           longest_climbs=longest_climbs)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        HTML(string=html).write_pdf(f.name)
        return send_file(f.name, as_attachment=True, download_name='climbing_resume.pdf')


if __name__ == '__main__':
    app.run(debug=True)


