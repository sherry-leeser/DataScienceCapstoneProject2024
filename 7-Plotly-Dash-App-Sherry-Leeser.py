# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Read the space data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # Define the dcc.Dropdown component
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
                 ),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),  # Added a div to contain the pie chart

    # TASK 3: Add a slider to select payload range
    html.Div([
        html.Label('Payload Range (kg)'),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={0: '0', 10000: '10000'},
            value=[min_payload, max_payload]
        )
    ], style={'margin': '20px 50px'}),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    # TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))  # Added a div to contain the scatter chart
])


@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    # Filter the DataFrame based on the selected launch site
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    # Count the total success launches (class=1)
    total_success = filtered_df[filtered_df['class'] == 1].shape[0]

    # Count the total failed launches (class=0)
    total_failed = filtered_df[filtered_df['class'] == 0].shape[0]

    # Create the pie chart
    fig = go.Figure(data=[go.Pie(labels=['Success', 'Failed'], values=[total_success, total_failed], hole=.3)])

    # Set layout properties
    fig.update_layout(title=f"Success vs Failed Launches at {entered_site if entered_site != 'ALL' else 'All Sites'}")

    return fig


@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    # Filter the DataFrame based on the selected launch site
    if entered_site == 'ALL':
        filtered_df = spacex_df
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

    # Filter the DataFrame based on payload range
    filtered_df = filtered_df[(filtered_df['Payload Mass (kg)'] >= payload_range[0]) &
                              (filtered_df['Payload Mass (kg)'] <= payload_range[1])]

    # Create the scatter plot
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title=f"Payload Success Outcome for {entered_site if entered_site != 'ALL' else 'All Sites'}",
                     labels={'class': 'Outcome'})

    return fig


if __name__ == '__main__':
    app.run_server()
