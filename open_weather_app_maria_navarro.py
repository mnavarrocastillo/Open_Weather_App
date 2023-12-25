# Student: Maria Navarro
# Date: Dec 5, 2023
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

from controls_maria_navarro import GIS
from open_weather.open_weather_api import OpenWeather

#TEST Maria
from pycountry_convert import country_alpha2_to_country_name
import us
from collections import defaultdict

states_as_list = GIS.get_us_states()
countries_as_list = GIS.get_countries()
# TEST Maria
countries_dict = {} # creates empty countries dictionary
states_dict = {} # creates empty states dictionary

#TEST Maria
# creates dictionary of country codes and country names
for c in countries_as_list:
    if c == 'XK': # handle unique case
        country_name = "Kosovo"
        countries_dict[c] = country_name
    else:
        country_name = country_alpha2_to_country_name(c)
        countries_dict[c] = country_name

# creates dictionary of state codes and state names
for c in states_as_list:
    if c == "DC": # handle unique cases
        state_name = "District of Columbia"
        states_dict[c] = state_name
    elif c == "00": # handle unique cases
        state_name = "Unknown"
        states_dict[c] = state_name
    else:
        state = us.states.lookup(c)
        state_name = state.name
        states_dict[c] = state_name

# Sort the dictionaries alphabetically by value
sorted_countries_dict = {k: v for k, v in sorted(countries_dict.items(), key=lambda item: item[1])}
sorted_states_dict = {k: v for k, v in sorted(states_dict.items(), key=lambda item: item[1])}

# setup app with stylesheets
app = dash.Dash(__name__)  # , external_stylesheets=[dbc.theme.])

# create map template
mapbox_access_token = \
    'pk.eyJ1IjoiYW5hbWluaSIsImEiOiJja2htbGEwdHcwcWZ3MzVvOTR1amNhajM5In0.tmieTIAQdfvwE4m_WUXuCQ'

# Creates layout for map
layout_map = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=25, r=25, b=25, t=25),
    hovermode='closest',
    title='Weather Map',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        # center=dict(lon=-98.5795, lat=39.8283),
        zoom=1,
    ),
)

# Creates layout for bar graph
layout_bar = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=25, r=25, b=25, t=25),
    title='Weather Station Rankings',
    xaxis=dict(title='Weather Station', showticklabels=False),
    yaxis=dict(title='Temperature'),
)

controls = dbc.Form(
    dbc.Row(
        [
            dbc.Label("Country", width="auto"),
            dbc.Col(
                dcc.Dropdown(
                    options=[{'label': sorted_countries_dict[c], 'value': c} for c in sorted_countries_dict], #TEST Maria
                    value='',
                    id='country-list',
                    disabled=False,
                    multi=True #TEST Maria enable multiple selection
                ),
                className='me-3'
            ),
            dbc.Label("US State", width="auto"),
            dbc.Col(
                dcc.Dropdown(
                    options=[{'label': sorted_states_dict[c], 'value': c} for c in sorted_states_dict], # TEST Maria
                    value='',
                    id='state-list',
                    disabled=False,
                    multi=True #TEST Maria enable multiple selection
                ),
                className='me-3'
            )
        ],
        className="g-2",
    )
)

app.layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(html.H2(), md=3),
                dbc.Col(
                    html.H2('Open Weather Data', className='text-white'), md=9
                )
            ], align='center', className='bg-info'),
        dbc.Row(
            [
                dbc.Col(controls, align='start', md=3),
                # TEST Maria
                dbc.Col(dcc.Graph(id='map', figure={'data':[], 'layout':layout_map}), align='start', md=6),
                dbc.Col(dcc.Graph(id='bar-chart', figure={'data':[], 'layout':layout_bar}), align='start', md=3),
            ], align='center', className='bg-info',
        ),
    ],
    id='main-container',
    style={'display': 'flex', 'flex-direction': 'column'},
    fluid=True
)

# TEST Maria: Creates callback that disables one dropdown while the other one is being used
@app.callback(
    [Output('country-list', 'disabled'),
    Output('state-list', 'disabled')],
    [Input('country-list', 'value'),
     Input('state-list', 'value')]
)
def update_dropdowns(country_value, state_value):
    if country_value:
        return False, True
    elif state_value:
        return True, False
    else:
        return False, False

# TEST Maria: Creates callback for map with chosen countries or chosen states
@app.callback(Output('map', 'figure'),
              [Input('country-list', 'value')],
              [Input('state-list', 'value')])
def make_map(chosen_countries, chosen_states):
    # create empty lists when nothing has been chosen yet
    if chosen_countries is None:
        chosen_countries = []
    if chosen_states is None:
        chosen_states = []

    # get appropriate city weather stations for either a US state or a country
    if chosen_states:
        city_list_as_dict = GIS.get_cities_by_us_state(chosen_states)
        show_state = True
    else:
        city_list_as_dict = GIS.get_cities_by_country(chosen_countries)
        show_state = False

    open_weather = OpenWeather()
    traces = []

    traces_per_country_limit = 50  # Set the limit of traces per country for speedier process
    # Track the number of traces created for each country
    traces_per_country_count = defaultdict(int)

    traces_per_state_limit = 50  # Set the limit of traces per state speedier process
    # Track the number of traces created for each country
    traces_per_state_count = defaultdict(int)

    for city in city_list_as_dict.values():
        temperature = open_weather.execute(str(city.id))
        trace = dict(
            name=city.name,
            type='scattermapbox',
            lon=[city.longitude],
            lat=[city.latitude],
            showlegend=False,
            marker=dict(
                size=10,
                color=[temperature], # this will create a more intuitive color scale based on temperature
                colorscale='Viridis',
                cmin=0,
                cmax=100,
                colorbar=dict(title='Temperature'),
            ),
            visible=True,
        )

        # If we are displaying countries, keep track of traces per country to ensure we do not exceed limit
        if not show_state:
            country_code = city.country
            traces_created_for_country = traces_per_country_count[country_code]
            # Check if the limit for traces per country is reached
            if traces_created_for_country < traces_per_country_limit:
                traces.append(trace)
                traces_per_country_count[country_code] += 1

        # If we are displaying US states, keep track of traces per state to ensure we do not exceed limit
        else:
            state_code = city.state
            traces_created_for_state = traces_per_state_count[state_code]
            # Check if the limit for traces per state is reached
            if traces_created_for_state < traces_per_state_limit:
                traces.append(trace)
                traces_per_state_count[state_code] += 1

    figure_map = dict(data=traces, layout=layout_map)
    return figure_map

# TEST Maria: Creates callback for bar graph with chosen countries or chosen states
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('country-list', 'value')],
    [Input('state-list', 'value')])
def make_bar(chosen_countries, chosen_states):
    # creates empty lists when nothing has been chosen
    if chosen_countries is None:
        chosen_countries = []
    if chosen_states is None:
        chosen_states = []

    # get appropriate city weather stations for either a US state or a country
    if chosen_states:
        city_list_as_dict = GIS.get_cities_by_us_state(chosen_states)
        show_state = True
    else:
        city_list_as_dict = GIS.get_cities_by_country(chosen_countries)
        show_state = False

    open_weather = OpenWeather()
    traces = []

    traces_per_country_limit = 50  # Set the limit of traces per country
    # Track the number of traces created for each country
    traces_per_country_count = defaultdict(int)

    traces_per_state_limit = 50  # Set the limit of traces per state
    # Track the number of traces created for each state
    traces_per_state_count = defaultdict(int)

    for city in city_list_as_dict.values():
        temperature = open_weather.execute(str(city.id))
        trace = dict(
            name=city.name,
            x = [city.name], # new labeling for bar
            y=[temperature], # new labeling for bar
            type='bar',
            showlegend=False,
            text=[],
            marker=dict(
                color=[temperature], # to create more intuitive color scale based on temperature
                colorscale='Viridis',
                cmin=0,
                cmax=100,
            ),
            visible=True,
        )

        # Adds text to the bars to identify country or US state
        if not show_state:
            trace['text'].append(city.country)
        else:
            trace['text'].append(city.state)

        # If we are displaying countries, keep track of traces per country to ensure we do not exceed limit
        if not show_state:
            country_code = city.country
            traces_created_for_country = traces_per_country_count[country_code]
            # Check if the limit for traces per country is reached
            if traces_created_for_country < traces_per_country_limit:
                traces.append(trace)
                traces_per_country_count[country_code] += 1

        # If we are displaying US states, keep track of traces per state to ensure we do not exceed limit
        else:
            state_code = city.state
            traces_created_for_state = traces_per_state_count[state_code]
            # Check if the limit for traces per state is reached
            if traces_created_for_state < traces_per_state_limit:
                traces.append(trace)
                traces_per_state_count[state_code] += 1

    # Sort the traces based on temperature in descending order
    traces = sorted(traces, key=lambda trace: trace['y'][0], reverse=True)
    # Create bar figure
    figure_bar = {'data': traces, 'layout': layout_bar}

    return figure_bar

if __name__ == '__main__':
    app.run_server(debug=True)
