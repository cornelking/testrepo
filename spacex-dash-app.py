import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the data
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Calculate payload range
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get actual unique sites from data
unique_sites = [{'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())]

# Create Dash app
app = dash.Dash(__name__, serve_locally=True)

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown with correct site names
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + unique_sites,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range

    dcc.RangeSlider(id='payload-slider',
                min=0, 
                max=10000, 
                step=1000,
                marks={i: str(i) for i in range(0, 10001, 1000)},
                value=[min_payload, max_payload]),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: 
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output

@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Successful Launches by Launch Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Count success (1) and failure (0)
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['Outcome', 'Count']
        counts['Outcome'] = counts['Outcome'].map({0: 'Failure', 1: 'Success'})
        
        fig = px.pie(
            counts,
            names='Outcome',
            values='Count',
            title=f'Success vs Failure for {entered_site}',
            color_discrete_sequence=['#d62728', '#2ca02c']
        )
    return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def get_scatter_plot(entered_site, payload_range):
    low, high = payload_range
    
    # Filter by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    if entered_site == 'ALL':
        # All sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload Mass and Launch Success (All Sites)',
            hover_data=['Launch Site', 'Booster Version']
        )
    else:
        # Specific site
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload Mass and Launch Success ({entered_site})',
            hover_data=['Booster Version']
        )
    
    fig.update_layout(xaxis_title="Payload Mass (kg)", yaxis_title="Launch Outcome (0=Failure, 1=Success)")
    return fig


# Run the app
if __name__ == '__main__':
    app.run()