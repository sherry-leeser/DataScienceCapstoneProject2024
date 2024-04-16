import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Create the dropdown menu options
dropdown_options = [
    {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
]

# List of years 
year_list = [str(i) for i in range(1980, 2014)]

# Create the layout of the app
app.layout = html.Div([
    html.H1("Automobile Sales Statistics Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'font-size': 24}),
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            value='Yearly Statistics',
            placeholder='Select a Report Type'
        )
    ]),
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            disabled=False,  # Enabled by default
            placeholder='Select Year',
        ),
    ]),
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})
])

# Callback to update the disabled property of the second dropdown
@app.callback(
    Output('select-year', 'disabled'),
    [Input('dropdown-statistics', 'value')]
)
def update_year_dropdown(selected_stat):
    return selected_stat != 'Yearly Statistics'

# Callback for plotting
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'), 
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_stat, selected_year):
    if selected_stat == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = data[data['Recession'] == 1]

        # Plot 1: Average Automobile sales during the recession period
        R_chart1 = dcc.Graph(
            figure=px.line(recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index(), 
                           x='Year', y='Automobile_Sales',
                           title="Average Automobile Sales During Recession Period")
        )
        # Plot 2: Average number of vehicles sold by vehicle type
        R_chart2 = dcc.Graph(
            figure=px.bar(recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index(), 
                          x='Vehicle_Type', y='Automobile_Sales',
                          title='Average Number of Vehicles Sold by Vehicle Type During Recession Period')
        )
        # Plot 3: Total expenditure share by vehicle type during recession
        R_chart3 = dcc.Graph(
            figure=px.pie(recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index(), 
                          values='Advertising_Expenditure', names='Vehicle_Type',
                          title='Total Expenditure Share by Vehicle Type During Recession')
        )
        # Plot 4: Effect of unemployment rate on vehicle type and sales
        R_chart4 = dcc.Graph(
            figure=px.bar(recession_data.groupby('Vehicle_Type').agg({'unemployment_rate': 'mean', 'Automobile_Sales': 'mean'}).reset_index(), 
                  x='Vehicle_Type', y=['unemployment_rate', 'Automobile_Sales'],
                  title='Effect of Unemployment Rate on Vehicle Type and Sales',
                  labels={'value': 'Average', 'variable': 'Metric'},
                  barmode='group')
)

        return [
            html.Div(className='chart-item', children=[R_chart1, R_chart2]),
            html.Div(className='chart-item', children=[R_chart3, R_chart4])
        ]
    elif selected_stat == 'Yearly Statistics' and selected_year is not None:
        yearly_data = data[data['Year'] == int(selected_year)]
        # Plot 1: Yearly Automobile sales using line chart for the whole period
        Y_chart1 = dcc.Graph(
            figure=px.line(data.groupby('Year')['Automobile_Sales'].mean().reset_index(), 
                           x='Year', y='Automobile_Sales',
                           title='Yearly Automobile Sales')
        )
      
        # Plot 2: Total Monthly Automobile sales using line chart
        Y_chart2 = dcc.Graph(
            figure=px.line(data[data['Year'] == int(selected_year)].groupby(['Year', 'Month'])['Automobile_Sales'].sum().reset_index(), 
                        x='Month', y='Automobile_Sales',
                        title=f'Total Monthly Automobile Sales for {selected_year}')
        )


        # Plot 3: Bar chart for average number of vehicles sold during the given year
        Y_chart3 = dcc.Graph(
            figure=px.bar(yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index(), 
                          x='Vehicle_Type', y='Automobile_Sales',
                          title=f'Average Vehicles Sold by Vehicle Type in {selected_year}')
        )
        # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
        Y_chart4 = dcc.Graph(
            figure=px.pie(yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index(), 
                          values='Advertising_Expenditure', names='Vehicle_Type',
                          title=f'Total Advertisement Expenditure by Vehicle Type in {selected_year}')
        )
        return [
            html.Div(className='chart-item', children=[Y_chart1, Y_chart2]),
            html.Div(className='chart-item', children=[Y_chart3, Y_chart4])
        ]
    else:
        return html.Div("Please select a report type and year.")

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
