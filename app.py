import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import pandas as pd
from dash.dependencies import Input, Output


from database import fetch_all_data

# Definitions of constants. This projects uses extra CSS stylesheet at `./assets/style.css`
COLORS = ['rgb(67,67,67)', 'rgb(115,115,115)', 'rgb(49,130,189)', 'rgb(189,189,189)']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/style.css']

# Define the dash app first
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Define component functions


def page_header():
    """
    Returns the page header as a dash `html.Div`
    """
    return html.Div(id='header', children=[
        html.Div([html.H3('Visualization with datashader and Plotly')],
                 className="ten columns"),
        html.A([html.Img(id='logo', src=app.get_asset_url('github.png'),
                         style={'height': '35px', 'paddingTop': '7%'}),
                html.Span('Blownhither', style={'fontSize': '2rem', 'height': '35px', 'bottom': 0,
                                                'paddingLeft': '4px', 'color': '#a3a7b0',
                                                'textDecoration': 'none'})],
               className="two columns row",
               href='https://github.com/blownhither/'),
    ], className="row")


def description():
    """
    Returns top-level project description (About Page) in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        # COVID-19's Association with 2020 Presidential Election Results

        It's no secret that the COVID-19 pandemic has affected the lives of all Americans. At best,
        we're been sequestered at home in quarantine. At worst, we've lost the lives of people we
        care about. We've been left to make our own opinions on the federal government's handling of 
        this crisis. As a result, the recent presidential election has been in part a referendum on
        the federal government's response.

        Given the polarized condition of national politics in this country, it's no wonder that voter
        sentiment on the federal response has largely fallen on party lines, but as certain jurisdictions
        have been more greatly affected by the pandemic than others, it's natural to speculate that these
        divisions have broken down and shifted sentiments in places that have seen large case and casualty
        counts.

        This dashboard aims to serve as a tool for retrospective analysis on how voter sentiment has changed
        from 2016 to 2020 and how these trends break down by state and by county.

        ### Team Members
        This project was developed by Alex Zimbalist, Brett Cotler, Cameron Webster, and Chris Rolichek

        ### Possible Next Steps
        This dashboard utilizes population data, presidential election results, and coronavired case and death counts.
        To build on this project, it would be interesting to merge demographc and economic information such as 
        unemployment data, income, and ethnicity as well as healthcare expenditures per capita.

        ### Related Work
        - [Mail-in-voting as it realted to COVID-19](https://www.nature.com/articles/d41586-020-02979-x)
        - [COVID-19's effects on the election](https://www.npr.org/sections/health-shots/2020/11/06/930897912/many-places-hard-hit-by-covid-19-leaned-more-toward-trump-in-2020-than-2016)
        - [Counties hit hardest voted for Trump](https://apnews.com/article/counties-worst-virus-surges-voted-trump-d671a483534024b5486715da6edb6ebf)

        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")

#     fig.update_layout(template='plotly_dark',
#                       title=title,
#                       plot_bgcolor='#23272c',
#                       paper_bgcolor='#23272c',
#                       yaxis_title='MW',
#                       xaxis_title='Date/Time')
#     return fig


def dynamic_scatter():
    """
    Returns scatterplot of relative covid rate v. political demographic - the interactive component
    """
    return html.Div(children=[
        dcc.Markdown('''
        # " What If "
        So far, BPA has been relying on hydro power to balance the demand and supply of power. 
        Could our city survive an outage of hydro power and use up-scaled wind power as an
        alternative? Find below **what would happen with 2.5x wind power and no hydro power at 
        all**.   
        Feel free to try out more combinations with the sliders. For the clarity of demo code,
        only two sliders are included here. A fully-functioning What-If tool should support
        playing with other interesting aspects of the problem (e.g. instability of load).
        ''', className='eleven columns', style={'paddingLeft': '5%'})
    ], className="row")


def dynamic_scatter_tool():
    """
    Returns the What-If tool as a dash `html.Div`. The view is a 8:3 division between
    demand-supply plot and rescale sliders.
    """
    dfs = fetch_all_data()
    
    df_2020 = dfs[0]
    df_2016 = dfs[1]
    df_confirmed = dfs[2]
    df_deaths = dfs[3]
    df_population = dfs[4]

    df_2020["Donald Trump 2020"] = df_2020["Donald Trump"]
    df_2016["Donald Trump 2016"] = df_2016["Donald Trump"]
    df_2016.drop(columns=["Donald Trump"], inplace=True)
    df_2020.drop(columns=["Donald Trump"], inplace=True)

    df_elections = df_2016.merge(df_2020, how='inner', left_on='county_id', right_on='county_id')
    df_covid = df_confirmed.merge(df_deaths, how='inner', left_on='county_id', right_on='county_id', suffixes=('_confirmed', '_deaths'))
    df = df_elections.merge(df_covid, how='inner', left_on='county_id', right_on='county_id')
    df = df.merge(df_population, how='inner', left_on='county_id', right_on='county_id')

    df = df.drop_duplicates()

    grouped = df.groupby("state").sum()
    cases = grouped.loc[:, "1/23/20_confirmed":"1/22/20_deaths"].iloc[:, :-1]
    daily = [cases.iloc[:, i] - cases.iloc[:, i-1] for i in range(1,len(cases.columns))]
    for i in range(len(daily)):
        cases.iloc[:, i] = daily[i]
    cases.head()

    roll7 = cases.loc[:, "1/29/20_confirmed":]
    for i in range(len(roll7.columns)):
        avg = cases.iloc[:, i:i+7].mean(axis=1)
    roll7.iloc[:, i] = avg

    date = "3/24/20_confirmed"
    pct_trump = grouped["Donald Trump 2020"] / (grouped["POPESTIMATE2019"])
# print(pct_trump)
    cases = roll7.loc[:, date]
    total_case_density = roll7.sum() / grouped["POPESTIMATE2019"].sum()
# print(total_case_density)
    relative_case_density = cases / grouped["POPESTIMATE2019"] / total_case_density[date]
# print(relative_case_density)
    fig = plt.figure()
    plt.scatter(pct_trump, relative_case_density, alpha = .5)
    fig.savefig("test")

    fig = plt.figure()

    mark_values = {}
    for i in range(len(roll7.columns)):
        mark_values[i+1] = str(roll7.columns[i])

    app.layout = html.Div([
        html.Div([
            html.Pre(children = "Covid Infections and Political Preference by State",
            style = {"text-align": "center", "font-size":"100%", "color":"black"})
        ]),

        html.Div([
            dcc.Graph(id = 'dynamic_graph')
        ]),

        html.Div([
            dcc.RangeSlider(id = 'date_slider',
                min = 1,
                max = len(roll7.columns),
                value = [1],
                marks = mark_values,
                step = None)
        ], style = {"width": "70%", "position": "absolute",
                    "left": "5%"})
    ])

    @app.callback(
        dash.dependencies.Output("dynamic_graph", "figure"),
        [dash.dependencies.Input("date_slider", "value")]
    )

    def update(date_chosen):
        x = pct_trump
        print(x)
        y = roll7.loc[:, date_chosen] / grouped["POPESTIMATE2019"] / (roll7.sum() / grouped["POPESTIMATE2019"].sum())[date_chosen]
        print(y)
        new_df = pd.DataFrame(zip(x,y), columns = ['pct_trump', 'relative_case_density'])
        print(new_df.head())
        
        scatterplot = px.scatter(
            data_frame = new_df,
            x = 'pct_trump',
            y = 'relative_case_density',
            hover_date = ['state'],
            text = 'state',
            height = 550
        )

        scatterplot.update_traces(testposition = 'top center')
        scatterplot.savefig("test2")
        
        return (scatterplot)

dynamic_scatter_tool()

# app.layout = dynamic_scatter_tool

def project_details():
    """
    Returns the project details component of the website
    """
    return html.Div(children=[dcc.Markdown('''
        # Project Details

        ### Data Sources
        The dashboard uses real-time case-count data from the [COVID-19 Data Repository by the Center for 
        Systems Science and Engineering (CSSE) at Johns Hopkins University](https://github.com/CSSEGISandData/COVID-19) 
        which updates daily. 
        
        General election results data from 2020 was taken from a publicy available dataset on [Kaggle]
        (https://www.kaggle.com/unanimad/us-election-2020) and 2016 general election data came from 
        the [MIT Election Lab](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX).
        Additionally, populaition data was taken from []() in order to compare per-capita statistics. 

        ### Technology Stack

        The website was produced using a Dash website application and is hosted using the Gitpod online environment.
        The `app.py` script hosts the Dash components as well as visualizations created using Plot.ly.

        ### ETL and Database Design

        Our data is read from the links provided inot dataframes in the `data_aquire.py` script. Additionally, 
        the script reformats and extracts the columns relevant to our analysis before upserting the rows of each
        dataframe as documents to 5 different collections in a MongoDB database. These 5 collections hold vote
        counts for 2016, vote counts for 2020, the number of new deaths for each day since February by county, the 
        number of new cases for each day since February by county, and the population of each county. Each of these
        collections is linked by a county idenfitication variable, which is the name of the county and the state 
        where it is located. The `database.py` script then pulls the data from the database into dataframes that are
        used to create the visualizations in `app.py`

        [ETL_ETA Notebook](link to EDL_ETA.ipynb)
        [Enhancement Notebook](link to Enhancement.ipynb)

        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")


def architecture_summary():
    """
    Returns the text and image of architecture summary of the project.
    """
    return html.Div(children=[
        dcc.Markdown('''
            # Project Architecture
            This project uses MongoDB as the database. All data acquired are stored in raw form to the
            database (with de-duplication). An abstract layer is built in `database.py` so all queries
            can be done via function call. For a more complicated app, the layer will also be
            responsible for schema consistency. A `plot.ly` & `dash` app is serving this web page
            through. Actions on responsive components on the page is redirected to `app.py` which will
            then update certain components on the page.  
        ''', className='row eleven columns', style={'paddingLeft': '5%'}),

        html.Div(children=[
            html.Img(src="https://docs.google.com/drawings/d/e/2PACX-1vQNerIIsLZU2zMdRhIl3ZZkDMIt7jhE_fjZ6ZxhnJ9bKe1emPcjI92lT5L7aZRYVhJgPZ7EURN0AqRh/pub?w=670&amp;h=457",
                     className='row'),
        ], className='row', style={'textAlign': 'center'}),

        dcc.Markdown('''
        
        ''')
    ], className='row')


# # Sequentially add page components to the app's layout
# def dynamic_layout():
#     return html.Div([
#         page_header(),
#         html.Hr(),
#         description(),
#         # dcc.Graph(id='trend-graph', figure=static_stacked_trend_graph(stack=False)),
#         dcc.Graph(id='stacked-trend-graph', figure=static_stacked_trend_graph(stack=True)),
#         what_if_description(),
#         what_if_tool(),
#         architecture_summary(),
#     ], className='row', id='content')


# # set layout to a function which updates upon reloading
# app.layout = dynamic_layout


# # Defines the dependencies of interactive components

# @app.callback(
#     dash.dependencies.Output('wind-scale-text', 'children'),
#     [dash.dependencies.Input('wind-scale-slider', 'value')])
# def update_wind_sacle_text(value):
#     """Changes the display text of the wind slider"""
#     return "Wind Power Scale {:.2f}x".format(value)


# @app.callback(
#     dash.dependencies.Output('hydro-scale-text', 'children'),
#     [dash.dependencies.Input('hydro-scale-slider', 'value')])
# def update_hydro_sacle_text(value):
#     """Changes the display text of the hydro slider"""
#     return "Hydro Power Scale {:.2f}x".format(value)



# @app.callback(
#     dash.dependencies.Output('what-if-figure', 'figure'),
#     [dash.dependencies.Input('wind-scale-slider', 'value'),
#      dash.dependencies.Input('hydro-scale-slider', 'value')])
# def what_if_handler(wind, hydro):
#     """Changes the display graph of supply-demand"""
#     df = fetch_all_data()
#     x = df['Datetime']
#     supply = df['Wind'] * wind + df['Hydro'] * hydro + df['Fossil/Biomass'] + df['Nuclear']
#     load = df['Load']

#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=x, y=supply, mode='none', name='supply', line={'width': 2, 'color': 'pink'},
#                   fill='tozeroy'))
#     fig.add_trace(go.Scatter(x=x, y=load, mode='none', name='demand', line={'width': 2, 'color': 'orange'},
#                   fill='tonexty'))
#     fig.update_layout(template='plotly_dark', title='Supply/Demand after Power Scaling',
#                       plot_bgcolor='#23272c', paper_bgcolor='#23272c', yaxis_title='MW',
#                       xaxis_title='Date/Time')
#     return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=1050, host='0.0.0.0')