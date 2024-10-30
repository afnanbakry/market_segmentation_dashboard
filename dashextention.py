
import dash
from dash import html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd


# Load data from Excel file
file_path = 'F:\Graduation project\work\Online Retail.xlsx'
df = pd.read_excel(file_path)

# Prepare data
df = df.dropna(subset=['CustomerID']).query('Quantity > 0')
df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

# Calculate RFM metrics
rfm = df.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
    'InvoiceNo': 'count',
    'TotalAmount': 'sum'
}).rename(columns={'InvoiceDate': 'Recency', 'InvoiceNo': 'Frequency', 'TotalAmount': 'Monetary'}).reset_index()

# Segment customers based on RFM scores
def segment_customers(df, criteria):
    if 'R' in criteria:
        df['R_Score'] = pd.qcut(df['Recency'], q=4, labels=[4, 3, 2, 1])
    if 'F' in criteria:
        df['F_Score'] = pd.qcut(df['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4])
    if 'M' in criteria:
        df['M_Score'] = pd.qcut(df['Monetary'], q=4, labels=[1, 2, 3, 4])
    
    df['RFM_Score'] = df[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
    
    df['Segment'] = df.apply(lambda x: 'Champions' if x['R_Score'] >= 4 and x['F_Score'] >= 4 and x['M_Score'] >= 4 else
                                       'Loyal Customers' if x['R_Score'] >= 3 and x['F_Score'] >= 3 and x['M_Score'] >= 3 else
                                       'Potential Loyalists' if x['R_Score'] >= 3 and x['F_Score'] >= 1 and x['M_Score'] >= 2 else
                                       'At Risk' if x['R_Score'] >= 2 and x['F_Score'] <= 2 and x['M_Score'] <= 2 else
                                       'Lost Customers', axis=1)
    return df

# Initialize the Dash app
app = dash.Dash(__name__)

# Define color scheme for segments
color_scheme = {
    'Champions': '#2E8B57',
    'Loyal Customers': '#4682B4',
    'Potential Loyalists': '#DAA520',
    'At Risk': '#CD853F',
    'Lost Customers': '#B22222'
}

# App layout
app.layout = html.Div([
    # Header
    html.H1('Customer Segmentation Dashboard - RFM Analysis',
            style={'textAlign': 'center', 'padding': '20px', 'backgroundColor': '#f8f9fa'}),
    
    # Segmentation Criteria Selection
    html.Div([
        html.Label('Select Segmentation Criteria:'),
        dcc.Dropdown(
            id='segmentation-criteria',
            options=[
                {'label': 'Recency, Frequency, Monetary (RFM)', 'value': 'RFM'},
                {'label': 'Recency, Frequency (RF)', 'value': 'RF'},
                {'label': 'Recency, Monetary (RM)', 'value': 'RM'},
                {'label': 'Frequency, Monetary (FM)', 'value': 'FM'},
                {'label': 'Recency (R)', 'value': 'R'},
                {'label': 'Frequency (F)', 'value': 'F'},
                {'label': 'Monetary (M)', 'value': 'M'}
            ],
            value='RFM',
            clearable=False
        )
    ], style={'padding': '20px'}),
    
    # Tabs for Visualizations and Segment Details
    dcc.Tabs(id='tabs', value='visualizations', children=[
        dcc.Tab(label='Visualizations', value='visualizations', children=[
            # KPI Cards Row
            html.Div([
                html.Div([
                    html.H4('Total Customers'),
                    html.H2(len(rfm)),
                ], className='stats-card'),
                html.Div([
                    html.H4('Average Order Value'),
                    html.H2(f'${rfm["Monetary"].mean():.2f}'),
                ], className='stats-card'),
                html.Div([
                    html.H4('Average Frequency'),
                    html.H2(f'{rfm["Frequency"].mean():.1f}'),
                ], className='stats-card'),
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
            
            # Charts Row
            html.Div([
                # Segment Distribution Pie Chart
                html.Div([
                    dcc.Graph(
                        id='segment-pie',
                        figure={}
                    )
                ], style={'width': '50%'}),
                
                # Average Values by Segment Bar Chart
                html.Div([
                    dcc.Graph(
                        id='segment-metrics',
                        figure={}
                    )
                ], style={'width': '50%'})
            ], style={'display': 'flex', 'margin': '20px'}),
            
            # Customer Table Section
            html.Div([
                html.H3('Customer Details'),
                # Search options
                html.Div([
                    html.Label('Search by:'),
                    dcc.Dropdown(
                        id='search-by',
                        options=[
                            {'label': 'Customer ID', 'value': 'CustomerID'},
                            {'label': 'Segment', 'value': 'Segment'},
                            {'label': 'Recency (days)', 'value': 'Recency'},
                            {'label': 'Frequency', 'value': 'Frequency'},
                            {'label': 'Monetary', 'value': 'Monetary'}
                        ],
                        value='CustomerID',
                        clearable=False,
                        style={'width': '200px', 'marginRight': '10px'}
                    ),
                    dcc.Input(
                        id='search-input',
                        type='text',
                        placeholder='Enter search value...',
                        style={'width': '300px', 'padding': '10px', 'marginBottom': '10px'}
                    )
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                
                # Segment dropdown
                html.Div([
                    html.Label('Filter by Segment:'),
                    dcc.Dropdown(
                        id='segment-filter',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': 'Champions', 'value': 'Champions'},
                            {'label': 'Loyal Customers', 'value': 'Loyal Customers'},
                            {'label': 'Potential Loyalists', 'value': 'Potential Loyalists'},
                            {'label': 'At Risk', 'value': 'At Risk'},
                            {'label': 'Lost Customers', 'value': 'Lost Customers'}
                        ],
                        value='all',
                        clearable=False,
                        style={'width': '200px'}
                    )
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '10px'}),
                
                # Customer table
                dash_table.DataTable(
                    id='customer-table',
                    columns=[
                        {'name': 'Customer ID', 'id': 'CustomerID'},
                        {'name': 'Segment', 'id': 'Segment'},
                        {'name': 'Recency (days)', 'id': 'Recency'},
                        {'name': 'Frequency', 'id': 'Frequency'},
                        {'name': 'Monetary', 'id': 'Monetary'}
                    ],
                    data=[],
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px'
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold'
                    },
                    style_data_conditional=[
                        {
                            'if': {'column_id': 'Segment'},
                            'backgroundColor': 'lightgrey',
                            'fontWeight': 'bold'
                        }
                    ]
                )
            ], style={'margin': '20px'})
        ]),
        
        dcc.Tab(label='Segment Details', value='segment-details', children=[
            html.Div(id='segment-details-content')
        ])
    ])
])

# Callbacks
@app.callback(
    [Output('segment-pie', 'figure'),
     Output('segment-metrics', 'figure'),
     Output('customer-table', 'data'),
     Output('segment-details-content', 'children')],
    [Input('segmentation-criteria', 'value'),
     Input('search-by', 'value'),
     Input('search-input', 'value'),
     Input('segment-filter', 'value')])
def update_dashboard(segmentation_criteria, search_by, search_value, segment_filter):
    # Segment customers based on selected criteria
    df = segment_customers(rfm, segmentation_criteria)
    
    # Segment Distribution Pie Chart
    segment_pie = px.pie(
        df['Segment'].value_counts(),
        values='count',
        names=df['Segment'].value_counts().index,
        title='Customer Segment Distribution',
        color=df['Segment'].value_counts().index,
        color_discrete_map=color_scheme
    )
    segment_pie.update_traces(hoverinfo='label+percent')
    
    # Average Values by Segment Bar Chart
    segment_metrics = px.bar(
        df.groupby('Segment').agg({
            'Monetary': 'mean',
            'Frequency': 'mean',
            'Recency': 'mean'
        }).reset_index(),
        x='Segment',
        y=['Monetary', 'Frequency', 'Recency'],
        title='Average Metrics by Segment',
        barmode='group'
    )
    segment_metrics.update_layout(bargap=0.1)
    segment_metrics.update_traces(hovertemplate='%{y:.2f}')
    
    # Customer Table
    if search_value:
        if search_by == 'Segment':
            filtered_df = df[df['Segment'] == search_value]
        else:
            filtered_df = df[df[search_by].astype(str).str.contains(search_value)]
    else:
        filtered_df = df
    
    if segment_filter != 'all':
        filtered_df = filtered_df[filtered_df['Segment'] == segment_filter]
    
    # Segment Details
    segment_details = []
    for segment, segment_df in filtered_df.groupby('Segment'):
        segment_info = {
            'Segment': segment,
            'Percentage': f"{len(segment_df) / len(df) * 100:.2f}%",
            'Recency': segment_df['Recency'].mean(),
            'Frequency': segment_df['Frequency'].mean(),
            'Monetary': segment_df['Monetary'].mean()
        }
        
        if segment == 'Champions':
            segment_info['Description'] = 'Highly engaged customers with high recency, frequency, and monetary value.'
            segment_info['Strengths'] = 'These customers are your most valuable and loyal. They are likely to continue generating high revenue.'
            segment_info['Weaknesses'] = 'None, these are your best customers.'
            segment_info['Strategies'] = 'Continue providing excellent service and offers to maintain their loyalty.'
        elif segment == 'Loyal Customers':
            segment_info['Description'] = 'Moderately engaged customers with good recency, frequency, and monetary value.'
            segment_info['Strengths'] = 'These customers are reliable and valuable, though not as much as Champions.'
            segment_info['Weaknesses'] = 'May be at risk of churn if not properly engaged.'
            segment_info['Strategies'] = 'Offer targeted promotions and rewards to increase their engagement and lifetime value.'
        elif segment == 'Potential Loyalists':
            segment_info['Description'] = 'Customers with good recency and monetary value, but low frequency.'
            segment_info['Strengths'] = 'These customers have potential to become more loyal if properly engaged.'
            segment_info['Weaknesses'] = 'Low purchase frequency may indicate lack of loyalty or awareness.'
            segment_info['Strategies'] = 'Implement campaigns to increase purchase frequency and move them to the Loyal Customers segment.'
        elif segment == 'At Risk':
            segment_info['Description'] = 'Customers with low recency, frequency, and monetary value.'
            segment_info['Strengths'] = 'None, these customers are at risk of churn.'
            segment_info['Weaknesses'] = 'Low engagement and declining value.'
            segment_info['Strategies'] = 'Reach out to these customers with targeted offers and incentives to re-engage them.'
        elif segment == 'Lost Customers':
            segment_info['Description'] = 'Customers who have not made a purchase in a long time.'
            segment_info['Strengths'] = 'None, these customers are likely lost.'
            segment_info['Weaknesses'] = 'No recent engagement or purchases.'
            segment_info['Strategies'] = 'Consider running win-back campaigns to try to re-engage these customers.'
        
        segment_details.append(segment_info)
    
    segment_details_content = html.Div([
        html.H2('Segment Details'),
        dash_table.DataTable(
            columns=[
                {'name': 'Segment', 'id': 'Segment'},
                {'name': 'Percentage', 'id': 'Percentage'},
                {'name': 'Recency', 'id': 'Recency'},
                {'name': 'Frequency', 'id': 'Frequency'},
                {'name': 'Monetary', 'id': 'Monetary'},
                {'name': 'Description', 'id': 'Description'},
                {'name': 'Strengths', 'id': 'Strengths'},
                {'name': 'Weaknesses', 'id': 'Weaknesses'},
                {'name': 'Strategies', 'id': 'Strategies'}
            ],
            data=segment_details,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold'
            }
        )
    ])
    
    return segment_pie, segment_metrics, filtered_df.to_dict('records'), segment_details_content

# Add CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>RFM Dashboard</title>
        <style>
            .stats-card {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                width: 30%;
            }
            .stats-card h4 {
                color: #666;
                margin-bottom: 10px;
            }
            .stats-card h2 {
                color: #333;
                margin: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)