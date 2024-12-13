import random
import plotly
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from flask import Flask
from flask_restful import Resource, Api
from dash import dcc, html, dash_table
import math
import json

# Import json as dataframe
with open('persona_axis.json', 'r') as file:
    j = json.load(file)

df = pd.DataFrame(j['points'])

TABLE_DATA = None

# Predefined points with labels
points_with_labels = [
    {"label": "Hitler", "x": 0.8, "y": 0.9},
    {"label": "Stalin", "x": 0.2, "y": 0.9},
    {"label": "Thatcher", "x": 0.75, "y": 0.8},
    {"label": "G.W. Bush", "x": 0.85, "y": 0.7},
    {"label": "Friedman", "x": 0.9, "y": 0.15},
    {"label": "Gandhi", "x": 0.3, "y": 0.2},
    {"label": "Steph", "x": 0.4, "y": 0.1},
]

# Generate all coordinates in the range [0, 1] rounded to one decimal point
points_without_labels = [{"x": x, "y": y} for x in [i / 10 for i in range(11)] for y in [i / 10 for i in range(11)]]

# Remove predefined points from the list of invisible points to avoid overlap
points_without_labels = [point for point in points_without_labels if not any(
    existing_point['x'] == point['x'] and existing_point['y'] == point['y']
    for existing_point in points_with_labels
)]

# Function to calculate the Euclidean distance between two points
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to create the scatter plot figure
def create_scatter_figure(marker_x=0.5, marker_y=0.5):
    fig = go.Figure()

    # Add predefined points with labels (visible)
    fig.add_trace(go.Scatter(
        x=[point['x'] for point in points_with_labels],
        y=[point['y'] for point in points_with_labels],
        mode='markers+text',
        text=[point['label'] for point in points_with_labels],
        textposition='top center',
        marker=dict(size=10, color='blue'),
    ))

    # Add invisible points without labels
    fig.add_trace(go.Scatter(
        x=[point['x'] for point in points_without_labels],
        y=[point['y'] for point in points_without_labels],
        mode='markers',  # No labels (invisible points)
        text=['' for _ in points_without_labels],  # Empty text (no labels)
        marker=dict(size=5, color='blue', opacity=0),  # Invisible points
    ))

    # Add draggable marker at the user clicked position (default position)
    fig.add_trace(go.Scatter(
        x=[marker_x],
        y=[marker_y],
        mode='markers',
        marker=dict(size=15, color='red'),
        name='Draggable Marker'
    ))

    # Add center labels for each quadrant (for visual understanding)
    fig.add_trace(go.Scatter(
        x=[0.25, 0.75, 0.25, 0.75],
        y=[0.75, 0.75, 0.25, 0.25],
        mode='text',
        text=["Authoritarian Left", "Authoritarian Right", "Libertarian Left", "Liberitarian Right"],
        textposition="middle center",
        showlegend=False,
        textfont=dict(size=14, color="black"),
    ))

    # Add quadrant shading (background sections)
    fig.add_shape(type="rect", x0=0, y0=0.5, x1=0.5, y1=1,
                  fillcolor="rgba(255, 0, 0, 0.2)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0.5, y0=0.5, x1=1, y1=1,
                  fillcolor="rgba(0, 0, 255, 0.2)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0, y0=0, x1=0.5, y1=0.5,
                  fillcolor="rgba(0, 255, 0, 0.2)", line=dict(width=0), layer="below")
    fig.add_shape(type="rect", x0=0.5, y0=0, x1=1, y1=0.5,
                  fillcolor="rgba(255, 255, 0, 0.2)", line=dict(width=0), layer="below")

    # Update layout to give more space for components
    fig.update_layout(
        title='Persona State Space',
        xaxis=dict(title='Economic Axis', range=[0, 1], zeroline=True, showgrid=True),
        yaxis=dict(title='Social Axis', range=[0, 1], zeroline=True, showgrid=True),
        template='plotly',  # Modern plotly theme
        autosize=True,  # Allow resizing of the plot
        width=700,  # Adjust width to ensure it's not too squished
        height=600,  # Adjust height to give it more space
    )

    return fig

# Function to create the bar plot for Euclidean distances
def create_bar_figure(distances):
    fig = go.Figure()

    # Add a bar plot for Euclidean distances
    fig.add_trace(go.Bar(
        x=[point['label'] for point in points_with_labels],
        y=distances,
        name='Euclidean Distances',
        marker=dict(color='purple')
    ))

    # Update layout for the bar plot
    fig.update_layout(
        title='Affinity to Clicked Point',
        xaxis=dict(title='Label'),
        yaxis=dict(title='Affinity'),
        template='plotly',  # Modern plotly theme
        height=250,  # Adjust the height for the bar plot
    )

    return fig

# Flask app
server = Flask(__name__)

# Dash app
app = dash.Dash(__name__, server=server)

app.layout = html.Div([
    # Main container using Flexbox to align elements vertically and center content
    html.Div([
        # Title for the plot (bold and centered)
        html.H1("Political Compass Plot", style={"fontWeight": "bold", "textAlign": "center", "marginTop": "20px"}),  # Title centered and bold

        # Scatter plot container - This should be centered horizontally
        html.Div([
            dcc.Graph(
                id='political-compass',
                config={'displayModeBar': False},  # Disable editing tools
                figure=create_scatter_figure(),  # Initial scatter plot
            ),
        ], style={'width': '100%', 'maxWidth': '800px', 'marginLeft': '190px'}),  # Center the scatter plot and set a max width

        # Buttons and Table in a centered flex layout
        html.Div([
            # Randomize button
            html.Button('Randomize Marker', id='randomize-button', n_clicks=0, style={'marginRight': '10px'}),
            
            # Go to /persona button
            html.Button('Get Persona', id='go-to-persona-button', n_clicks=0),
        ], style={'display': 'flex', 'justifyContent': 'center', 'marginTop': '20px'}),

        # Euclidean Distance bar plot
        html.Div([
            dcc.Graph(
                id='euclidean-distances',
                config={'displayModeBar': False},  # Disable editing tools
                figure=create_bar_figure([]),  # Initially empty bar chart
            ),
        ], style={'flex': 1, 'width': '40%', 'height': '100%'}),  # Bar plot should take full width

        # Table to display the pre-defined labels with distances
        html.Div([
            dash_table.DataTable(
                id='distance-table',
                columns=[
                    {'name': 'Label', 'id': 'label'},
                    {'name': 'Character Affinity (Inverted Euclidean Distance)', 'id': 'affinity'},
                ],
                data=[],
                style_table={'height': '300px', 'overflowY': 'auto'},  # Make the table scrollable
                style_cell={'textAlign': 'center'},
            ),
        ], style={'flex': 1, 'width': '40%'}),  # Table should take full width

    ], style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),  # Center everything

    html.Div("Click anywhere on the plot to place the marker!", style={"textAlign": "center", "marginTop": "20px"}),

    # Location component to manage URL navigation
    dcc.Location(id='url', refresh=True),  # Set 'refresh' to True to trigger a full page reload
])

# Callback to update scatter plot, bar plot, and table
@app.callback(
    [Output('political-compass', 'figure'),
     Output('euclidean-distances', 'figure'),
     Output('distance-table', 'data')],
    [Input('political-compass', 'clickData'),  # Capture click event
     Input('randomize-button', 'n_clicks')]  # Capture randomize button click
)
def update_plots(click_data, n_clicks):
    if n_clicks > 0:  # Randomize marker on button click
        marker_x = random.uniform(0, 1)
        marker_y = random.uniform(0, 1)
    elif click_data:  # If there is click data, extract x and y coordinates
        marker_x = click_data['points'][0]['x']
        marker_y = click_data['points'][0]['y']
    else:
        marker_x = 0.5  # Default center position
        marker_y = 0.5

    # Calculate Euclidean distances for each labeled point
    distances = [euclidean_distance(marker_x, marker_y, point['x'], point['y']) for point in points_with_labels]

    # Find the maximum distance to invert the distances
    max_distance = max(distances)

    # Invert distances: subtract each distance from the maximum distance
    inverted_distances = [max_distance - dist for dist in distances]

    # Normalize the inverted distances so they sum to 1
    sum_inverted_distances = sum(inverted_distances)
    normalized_affinity = [round(dist / sum_inverted_distances, 3) for dist in inverted_distances]

    # Sort the labels by the normalized affinity (character affinity), from highest to lowest
    sorted_table_data = sorted(
        zip(points_with_labels, normalized_affinity),
        key=lambda x: x[1], reverse=True
    )

    # Prepare table data
    table_data = [
        {'label': point['label'], 'affinity': dist}
        for point, dist in sorted_table_data
    ]

    global TABLE_DATA
    TABLE_DATA = table_data

    # Return updated figures and table data
    return create_scatter_figure(marker_x, marker_y), create_bar_figure(normalized_affinity), table_data

# Callback to handle redirection when the 'Go to /hello' button is clicked
@app.callback(
    Output('url', 'pathname'),
    [Input('go-to-persona-button', 'n_clicks')]
)
def redirect_to_persona(n_clicks):
    if n_clicks > 0:
        return '/persona'
    return dash.no_update

# API resource (HelloWorld endpoint)
api = Api(server)

class personify(Resource):
    def get(self):
        return TABLE_DATA

api.add_resource(personify, '/persona')

# Run the server
if __name__ == '__main__':
    server.run(debug=True, port=8080, host='0.0.0.0')
