'''

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Dummy data for demonstration
def generate_dummy_data(n=1000):
    np.random.seed(0)
    data = {
        'Customer ID': range(1, n+1),
        'Age': np.random.randint(18, 80, n),
        'Income': np.random.randint(20000, 200000, n),
        'Spending Score': np.random.randint(1, 100, n),
        'Loyalty': np.random.choice(['Low', 'Medium', 'High'], n),
        'Segment': np.random.choice(['A', 'B', 'C', 'D'], n)
    }
    return pd.DataFrame(data)

df = generate_dummy_data()

# Sidebar
sidebar = html.Div([
    html.H3("Customer Segmentation"),
    dbc.Nav([
        dbc.NavLink("Dashboard", href="#", active="exact"),
        dbc.NavLink("Data View", href="#", active="exact"),
        dbc.NavLink("Segmentation Analysis", href="#", active="exact"),
    ], vertical=True, pills=True),
], style={"padding": "20px", "background-color": "#f8f9fa"})

# Main content
main_content = html.Div([
    html.H2("Customer Segmentation Dashboard"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='segment-pie-chart')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='age-income-scatter')
        ], width=6),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='spending-loyalty-heatmap')
        ], width=6),
        dbc.Col([
            dcc.Graph(id='segment-characteristics')
        ], width=6),
    ], className="mb-4"),
    dbc.Row([
        dbc.Col([
            html.H4("Filter Data"),
            dcc.RangeSlider(
                id='age-range-slider',
                min=df['Age'].min(),
                max=df['Age'].max(),
                value=[df['Age'].min(), df['Age'].max()],
                marks={str(age): str(age) for age in range(20, 81, 20)},
                step=1
            ),
            html.P("Age Range", className="mt-2")
        ], width=6),
        dbc.Col([
            dcc.Dropdown(
                id='loyalty-dropdown',
                options=[{'label': i, 'value': i} for i in df['Loyalty'].unique()],
                value=df['Loyalty'].unique(),
                multi=True
            ),
            html.P("Loyalty", className="mt-2")
        ], width=6),
    ], className="mb-4"),
])

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar, width=3),
        dbc.Col(main_content, width=9),
    ]),
], fluid=True)

# Callbacks
@app.callback(
    [Output('segment-pie-chart', 'figure'),
     Output('age-income-scatter', 'figure'),
     Output('spending-loyalty-heatmap', 'figure'),
     Output('segment-characteristics', 'figure')],
    [Input('age-range-slider', 'value'),
     Input('loyalty-dropdown', 'value')]
)
def update_graphs(age_range, loyalty):
    filtered_df = df[(df['Age'] >= age_range[0]) & (df['Age'] <= age_range[1])]
    filtered_df = filtered_df[filtered_df['Loyalty'].isin(loyalty)]

    # Pie chart
    pie_chart = px.pie(filtered_df, names='Segment', title='Customer Segments')

    # Scatter plot
    scatter_plot = px.scatter(filtered_df, x='Age', y='Income', color='Segment', 
                              title='Age vs Income by Segment')

    # Heatmap
    heatmap_data = filtered_df.groupby(['Loyalty', 'Segment'])['Spending Score'].mean().unstack()
    heatmap = px.imshow(heatmap_data, title='Average Spending Score by Loyalty and Segment')

    # Bar chart
    segment_chars = filtered_df.groupby('Segment')[['Age', 'Income', 'Spending Score']].mean()
    bar_chart = px.bar(segment_chars, title='Average Characteristics by Segment')

    return pie_chart, scatter_plot, heatmap, bar_chart

if __name__ == '__main__':
    app.run_server(debug=True)

    


    '''

# First, install required packages

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Generate dummy customer data
np.random.seed(42)
n_customers = 1000

data = {
    'CustomerID': range(1, n_customers + 1),
    'Age': np.random.normal(45, 15, n_customers).astype(int),
    'Income': np.random.normal(60000, 20000, n_customers),
    'SpendingScore': np.random.normal(50, 25, n_customers),
    'PurchaseFrequency': np.random.normal(30, 10, n_customers),
    'Gender': np.random.choice(['Male', 'Female'], n_customers),
    'Segment': np.random.choice(['High Value', 'Medium Value', 'Low Value', 'New Customer'], n_customers)
}

df = pd.DataFrame(data)

# Ensure values are within reasonable ranges
df['Age'] = df['Age'].clip(18, 90)
df['SpendingScore'] = df['SpendingScore'].clip(0, 100)
df['PurchaseFrequency'] = df['PurchaseFrequency'].clip(0, 100)
df['Income'] = df['Income'].clip(20000, 150000)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define colorblind-friendly color palette
colors = {
    'High Value': '#0077BB',      # Blue
    'Medium Value': '#33BBEE',    # Cyan
    'Low Value': '#EE7733',       # Orange
    'New Customer': '#009988'     # Teal
}

# Layout
app.layout = html.Div([
    html.H1('Customer Segmentation Dashboard',
            style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
    
    # Filters
    html.Div([
        html.Div([
            html.Label('Select Gender:'),
            dcc.Dropdown(
                id='gender-filter',
                options=[{'label': 'All', 'value': 'All'}] +
                        [{'label': x, 'value': x} for x in df['Gender'].unique()],
                value='All',
                clearable=False
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '5%'}),
        
        html.Div([
            html.Label('Age Range:'),
            dcc.RangeSlider(
                id='age-range',
                min=df['Age'].min(),
                max=df['Age'].max(),
                value=[df['Age'].min(), df['Age'].max()],
                marks={i: str(i) for i in range(20, 91, 10)},
                step=1
            )
        ], style={'width': '60%', 'display': 'inline-block'})
    ], style={'marginBottom': 30}),
    
    # First row of visualizations
    html.Div([
        html.Div([
            dcc.Graph(id='segment-distribution')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='spending-by-age')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ]),
    
    # Second row of visualizations
    html.Div([
        html.Div([
            dcc.Graph(id='income-distribution')
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Graph(id='purchase-frequency-segments')
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ])
])

# Callbacks
@app.callback(
    [Output('segment-distribution', 'figure'),
     Output('spending-by-age', 'figure'),
     Output('income-distribution', 'figure'),
     Output('purchase-frequency-segments', 'figure')],
    [Input('gender-filter', 'value'),
     Input('age-range', 'value')]
)
def update_graphs(selected_gender, age_range):
    # Filter data based on selections
    filtered_df = df[
        (df['Age'] >= age_range[0]) &
        (df['Age'] <= age_range[1])
    ]
    
    if selected_gender != 'All':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    # 1. Segment Distribution
    segment_dist = px.pie(
        filtered_df['Segment'].value_counts().reset_index(),
        values='count',
        names='Segment',
        title='Customer Segment Distribution',
        color='Segment',
        color_discrete_map=colors
    )
    segment_dist.update_traces(textinfo='percent+label')
    
    # 2. Spending Score by Age
    spending_age = px.scatter(
        filtered_df,
        x='Age',
        y='SpendingScore',
        color='Segment',
        title='Spending Score vs Age by Segment',
        color_discrete_map=colors
    )
    
    # 3. Income Distribution by Segment
    income_dist = px.box(
        filtered_df,
        x='Segment',
        y='Income',
        color='Segment',
        title='Income Distribution by Segment',
        color_discrete_map=colors
    )
    
    # 4. Purchase Frequency by Segment
    purchase_freq = px.violin(
        filtered_df,
        x='Segment',
        y='PurchaseFrequency',
        color='Segment',
        title='Purchase Frequency Distribution by Segment',
        color_discrete_map=colors
    )
    
    # Update layout for all plots
    for fig in [segment_dist, spending_age, income_dist, purchase_freq]:
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#2c3e50'},
            showlegend=True
        )
    
    return segment_dist, spending_age, income_dist, purchase_freq

if __name__ == '__main__':
    app.run_server(debug=True)