import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from PIL import Image
import base64

# import dataset
df = pd.read_csv(r"C:\Users\ADMIN\Documents\2nd yr\Python Dashboard\FInal Assignment\flights.csv")

df['date'] = pd.to_datetime(df['date'])
df['total_delay'] = df['carrier_delay'] + df['weather_delay'] + df['nas_delay'] + df['security_delay'] + df['late_aircraft_delay']

delay_counts = df.groupby('airline')[['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay']].sum().reset_index()

airline_counts = df['airline'].value_counts()

#image file 
pil_image = Image.open(r"C:\Users\ADMIN\Documents\2nd yr\Python Dashboard\FInal Assignment\edited png.png")


app = dash.Dash(__name__)

#tabs
app.layout = html.Div([
    html.H1("FLIGHT DELAYS"), 
    html.Img(src=pil_image, style={'width': '50%', 'height': '100px'}),     
    
    dcc.Tabs(
        id='Tab',
        children = [
        dcc.Tab(label='Line Chart', children=[
            html.H2('Line Chart'),
            # Date picker 
            dcc.DatePickerRange(
                id='line-chart-date-picker',
                display_format='DD/MM/YYYY',
                min_date_allowed=min(df['date']),
                max_date_allowed=max(df['date']),
                initial_visible_month=max(df['date']),
                start_date=min(df['date']),
                end_date=max(df['date'])
            ),
            # Dropdowns
            dcc.Dropdown(
                id='origin-dropdown',
                options=[{'label': origin, 'value': origin} for origin in df['origin'].unique()],
                placeholder='Select origin',
                multi=False
            ),
            dcc.Dropdown(
                id='dest-dropdown',
                options=[{'label': dest, 'value': dest} for dest in df['dest'].unique()],
                placeholder='Select destination',
                multi=False
            ),
            # Line chart 
            dcc.Graph(id='line-chart')
        ]),

        dcc.Tab(label='Scatter Plot', children=[
            html.H2('Correlation Plot'),
            # Radio button
            dcc.RadioItems(
                id='scatter-plot-radio',
                options=[{'label': col, 'value': col} for col in ['carrier_delay','weather_delay','nas_delay','security_delay','late_aircraft_delay']],
                value='carrier_delay'  
            ),
            # Scatter plot 
            dcc.Graph(id='scatter-plot')
        ]),

        dcc.Tab(label='Interactive Charts', children=[
            html.H2('Interactive Charts'),

            html.Div([
                # Chart 1
                dcc.Graph(
                    id='chart1',
                    figure=px.bar(delay_counts, x='airline', y=['carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay'],
                        title='Delay Breakdown by Airline', labels={'airline': 'Airline', 'value': 'Delay Count'}).update_layout(barmode='stack')
                ),
                # Chart 2
                dcc.Graph(
                    id='chart2',
                    figure=px.scatter(df, x='dep_time', y='total_delay', color='airline', title='Departure Time vs. Total Delay',
                         labels={'dep_time': 'Departure Time', 'total_delay': 'Total Delay'})
                )
            ])
        ]),

        dcc.Tab(label='Custom Graph', children=[
            html.H2('Total Delays by Airline'),
            # Box plot 
            dcc.Graph(
                id='custom-graph',
                figure=px.box(df, x='airline', y='total_delay', color='origin', title='Total Delays by Airline')
            )
        ])
    ]),

    # HTML 
    html.Footer(
        'Created by: Jehan Nirmal Fernando (Index: COHNDDS231F-015)',
        style={'position': 'fixed', 'bottom': '0', 'left': '0', 'width': '100%', 'background-color': '#f8f8f8',
               'padding': '10px'}
    )
])


# Callback line chart
@app.callback(
    dash.dependencies.Output('line-chart', 'figure'),
    dash.dependencies.Input('line-chart-date-picker', 'start_date'),
    dash.dependencies.Input('line-chart-date-picker', 'end_date'),
    dash.dependencies.Input('origin-dropdown', 'value'),
    dash.dependencies.Input('dest-dropdown', 'value'))
def update_line_chart(start_date, end_date, origin, dest):
    # Filter the dataset on the selected date range, origin, and destination
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date) & (df['origin'] == origin) & (df['dest'] == dest)]

    # line chart(total delay)
    fig = px.line(filtered_df, x='date', y='total_delay', title=f'Total Delays for flights from {origin} to {dest}')

    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)' 
    )
    fig.update_xaxes(
        mirror=False,
        ticks='outside',
        showline=False, 
        linecolor='black',
        gridcolor='grey'
    )
    fig.update_yaxes(
        mirror=True,
        ticks='outside',
        showline=False, 
        linecolor='black',
        gridcolor='grey'
    )
    
    return fig


# Callback scatter plot
@app.callback(
    dash.dependencies.Output('scatter-plot', 'figure'),
    dash.dependencies.Input('scatter-plot-radio', 'value'))
def update_scatter_plot(selected_var):
    # correlation
    correlation = df[['total_delay', selected_var]].corr().iloc[0, 1]

    # Update scatter plot
    fig = px.scatter(df, x='total_delay', y=selected_var, title=f'Correlation between total_delay and {selected_var}: {correlation:.2f}')

    return fig

# interaction 
@app.callback(
    dash.dependencies.Output('chart2', 'figure'),
    dash.dependencies.Input('chart1', 'clickData'))
def update_scatter_plot(click_data):
    if click_data is None:
        # If clicked data = none
        fig = px.scatter(df, x='dep_time', y='total_delay', color='airline', title='Departure Time vs. Total Delay',
                         labels={'dep_time': 'Departure Time', 'total_delay': 'Total Delay'})
    else:
        # Retrieve the selected airline from the clicked data
        selected_airline = click_data['points'][0]['x']

        # Filter the dataset based on the selected airline
        filtered_df = df[df['airline'] == selected_airline]

        # Create the updated scatter plot
        fig = px.scatter(filtered_df, x='dep_time', y='total_delay', color='airline',
                         title=f'Departure Time vs. Total Delay for {selected_airline}',
                         labels={'dep_time': 'Departure Time', 'total_delay': 'Total Delay'})

    return fig

if __name__ == '__main__':
    app.run_server(port=9221)
