"""Animal Shelter dashboard for the Grazioso Salvare CS 340 project."""

from collections import Counter
from pathlib import Path
import os

from dotenv import load_dotenv
import pandas as pd
import plotly.graph_objects as go
import dash_leaflet as dl
from dash import Dash, Input, Output, dash_table, dcc, html

from CRUD_Python_Module import AnimalShelter

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

# Breed, sex, and age ranges from the CS 340 rescue-dog specifications.
RESCUE_RULES = {
    "water": {
        "breeds": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"],
        "sex": "Intact Female",
        "min_weeks": 26,
        "max_weeks": 156,
    },
    "mountain": {
        "breeds": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"],
        "sex": "Intact Male",
        "min_weeks": 26,
        "max_weeks": 156,
    },
    "tracking": {
        "breeds": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"],
        "sex": "Intact Male",
        "min_weeks": 20,
        "max_weeks": 300,
    },
}

DEFAULT_CENTER = [30.75, -97.48]


def get_rescue_query(category):
    """Build the database query for a rescue type, or return everything on Reset."""
    rule = RESCUE_RULES.get(category)
    if rule is None:
        return {}
    # Course data sometimes lists a mix (e.g. German Shepherd Mix), so match
    # the target breed as a phrase without ignoring those mixed-breed records.
    import re
    pattern = "|".join(re.escape(breed) for breed in rule["breeds"])
    return {
        "animal_type": {"$regex": "^Dog$", "$options": "i"},
        "breed": {"$regex": pattern, "$options": "i"},
        "sex_upon_outcome": rule["sex"],
        "age_upon_outcome_in_weeks": {"$gte": rule["min_weeks"], "$lte": rule["max_weeks"]},
    }


def clean_records(records):
    """Remove the MongoDB ObjectId so the data can be sent to Dash as JSON."""
    if not records:
        return []
    result = []
    for record in records:
        cleaned = {}
        for key, value in record.items():
            if key == "_id":
                continue
            # Dataset fields are usually scalar; avoid passing database-specific
            # objects directly to the browser when a record has an odd field.
            if isinstance(value, (str, int, float, bool)) or value is None:
                cleaned[key] = value
            else:
                cleaned[key] = str(value)
        result.append(cleaned)
    return result


def breed_figure(rows):
    """Build a pie chart from the animal records currently visible in the table."""
    counts = Counter(str(row.get("breed") or "Unknown") for row in (rows or []))
    fig = go.Figure()
    if counts:
        common = counts.most_common(10)
        other = sum(counts.values()) - sum(n for _, n in common)
        if other:
            common.append(("Other breeds", other))
        fig.add_trace(go.Pie(labels=[k for k, _ in common], values=[n for _, n in common], hole=0.25))
        fig.update_layout(title="Breed distribution", margin=dict(l=15, r=15, t=55, b=10))
    else:
        fig.add_annotation(text="No animals match this filter", x=0.5, y=0.5, showarrow=False)
        fig.update_layout(title="Breed distribution", xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def map_layers(rows, selected_rows):
    """Show the selected animal's location, or a neutral map when none is available."""
    base = [dl.TileLayer()]
    if not rows:
        return base
    idx = (selected_rows or [0])[0]
    if not isinstance(idx, int) or not (0 <= idx < len(rows)):
        idx = 0
    animal = rows[idx]
    try:
        lat, lon = float(animal["location_lat"]), float(animal["location_long"])
        if pd.isna(lat) or pd.isna(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            return base
    except (KeyError, ValueError, TypeError):
        return base
    name = str(animal.get("name") or "Unnamed animal")
    breed = str(animal.get("breed") or "Unknown breed")
    return base + [dl.Marker(position=[lat, lon], children=[
        dl.Tooltip(breed), dl.Popup([html.B(name), html.P(breed)]),
    ])]


def load_animals(category):
    """Query MongoDB again for each rescue selection."""
    try:
        shelter = AnimalShelter()
        # A ping distinguishes a disconnected database from a collection with no matches.
        shelter.client.admin.command("ping")
        rows = clean_records(shelter.read(get_rescue_query(category)))
        return rows, None
    except Exception as exc:
        return [], "Could not connect to MongoDB. Check your .env settings and make sure MongoDB is running."


app = Dash(__name__, assets_folder=str(ROOT / "assets"), suppress_callback_exceptions=False)
app.title = "Grazioso Salvare | Animal Shelter"
app.layout = html.Div([
    html.Header([
        html.A(html.Img(src="/assets/grazioso-salvare.svg", style={"maxWidth": "390px", "width": "100%"}),
               href="https://www.snhu.edu/", target="_blank", title="Grazioso Salvare logo"),
        html.Div([html.H1("Animal Shelter Dashboard", style={"marginBottom": "4px"}),
                  html.P("Dashboard created by Gabriel Vasquez", style={"marginTop": "0"})]),
    ], style={"display": "flex", "alignItems": "center", "gap": "24px", "flexWrap": "wrap"}),
    html.Hr(),
    html.Label("Rescue category", htmlFor="rescue-type", style={"fontWeight": "bold"}),
    dcc.RadioItems(id="rescue-type", options=[
        {"label": "Water Rescue", "value": "water"},
        {"label": "Mountain / Wilderness Rescue", "value": "mountain"},
        {"label": "Disaster / Individual Tracking", "value": "tracking"},
        {"label": "Reset", "value": "reset"},
    ], value="reset", inline=True, style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "padding": "14px 0"}),
    html.Div(id="status-message", role="status", style={"paddingBottom": "10px", "color": "#5b4b36"}),
    dash_table.DataTable(
        id="datatable-id", data=[], columns=[],
        row_selectable="single", selected_rows=[],
        page_action="native", page_size=10,
        sort_action="native", filter_action="native",
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left", "padding": "7px", "minWidth": "110px", "maxWidth": "240px", "whiteSpace": "normal"},
        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#f5f8f7"}],
        style_header={"fontWeight": "bold", "backgroundColor": "#e4eeeb"},
    ),
    html.Div([
        html.Div(dcc.Graph(id="breed-chart"), style={"flex": "1 1 380px", "minWidth": "0"}),
        html.Div(dl.Map(id="map-id", center=DEFAULT_CENTER, zoom=10,
                        style={"height": "430px", "width": "100%"}, children=[dl.TileLayer()]),
                 style={"flex": "1 1 380px", "minWidth": "0"}),
    ], style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "marginTop": "22px"}),
], style={"fontFamily": "Arial, sans-serif", "maxWidth": "1400px", "margin": "auto", "padding": "24px"})


@app.callback(
    Output("datatable-id", "data"), Output("datatable-id", "columns"),
    Output("datatable-id", "selected_rows"), Output("status-message", "children"),
    Input("rescue-type", "value"),
)
def update_table(category):
    rows, error = load_animals(category)
    cols = list(dict.fromkeys(key for row in rows for key in row))
    return rows, [{"name": key.replace("_", " ").title(), "id": key, "selectable": True} for key in cols], ([0] if rows else []), (error or f"Showing {len(rows)} animal records")


@app.callback(
    Output("breed-chart", "figure"), Output("map-id", "children"),
    Input("datatable-id", "derived_virtual_data"),
    Input("datatable-id", "derived_virtual_selected_rows"),
    Input("datatable-id", "data"),
    Input("datatable-id", "selected_rows"),
)
def update_visualizations(view_rows, view_selected_rows, full_rows, selected_rows):
    rows = full_rows if view_rows is None else view_rows
    picked = selected_rows if view_rows is None else view_selected_rows
    return breed_figure(rows), map_layers(rows, picked)


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
