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
app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

dfs = fetch_all_data()
    
grouped = dfs[0]
roll7 = dfs[1].loc[:, "3/1/20_confirmed":]
roll7.reset_index(drop=True)

# Define component functions

def page_header():
    """
    Returns the page header as a dash `html.Div`
    """
    return html.Div(id='header', children=[
        html.Div([html.H3('Data1050 Final Project')],
                 className="ten columns"),
        html.A([html.Img(id='logo', src=app.get_asset_url('github.png'),
                         style={'height': '35px', 'paddingTop': '7%'}),
                html.Span('github', style={'fontSize': '2rem', 'height': '35px', 'bottom': 0,
                                                'paddingLeft': '4px', 'color': '#a3a7b0',
                                                'textDecoration': 'none'})],
               className="two columns row",
               href='https://github.com/b-cotler/data1050-covid-final-project'),
    ], className="row")


def description():
    """
    Returns top-level project description (About Page) in markdown
    """
    return html.Div(children=[dcc.Markdown('''
        # COVID-19 and Political Demographics

        ## About

        It's no secret that the COVID-19 pandemic has affected the lives of all Americans. At best,
        we've been sequestered at home in quarantine. At worst, we've lost the lives of people we
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
        This project was developed by Alex Zimbalist, Brett Cotler, Cameron Webster, and Chris Rohlicek

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

def static_scatter():
    return html.Div(children=[
        dcc.Markdown('''
        #
        ##
        #
        ## 
        # Covid-19 Cases and the Changing Electorate
        
        Donald Trump performed far worse in the 2020 election than he did in the 2016 election. It seems likely that
        this was in large part due to the coronavirus pandemic and his failure to effectively control the U.S. outbreak. 
        We wanted to know if the areas that were hit especially hard by covid-19 up until the election turned against 
        Trump more than areas that had fewer cases. We attempt to shed light on this question by calculating the difference 
        between the percent of the vote Trump received in each state in 2016 and the percent of the vote Trump received in 
        each state in 2020. Did Trump disproportionately underperform relative to 2016 in areas hit harder by the virus?

        The scatterplot below shows the cumulative number of confirmed cases along the y axis and the change in the percent 
        of the vote Trump received in 2016 and 2020 (where a positive change indicates better performance in 2020 than 
        in 2016) on the axis. As we can see, Trump performed worse in many states in 2020, and better in only a few (this 
        isn't terribly surprising, given that he won the 2016 election but lost the 2020 election). However, it appears 
        that Trump's diminished support was across-the-board; that is, he performed worse by a similar amount in both states 
        that were hit hard by the virus and states that had endured milder outbreaks. In other words, the scatterplot 
        does not show a strong correlation between the change in Trump's support from 2016 to 2020 and the severity of 
        the covid-19 pandemic in that area up until election day.

        ''', className='eleven columns', style={'paddingLeft': '5%'})
    ], className="row")

def static_scatter_tool():
    pct_trump_2020 = grouped["Donald Trump 2020"] / (grouped["Donald Trump 2020"] + grouped["Joe Biden"])
    pct_trump_2016 = grouped["Donald Trump 2016"] / (grouped["Donald Trump 2016"] + grouped["Hillary Clinton"])
    pct_change = pct_trump_2020 - pct_trump_2016
    election_day_total_cases = grouped["11/3/20_confirmed"]
    # fig = plt.figure()
    # plt.scatter(pct_change, election_day_total_cases)
    # plt.savefig('test2')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=pct_change, y=election_day_total_cases, mode='markers', name='static_scatter'))

    fig.update_layout(template='plotly_dark',
                      title="Covid-19 and Trump's Reelection Bid",
                      plot_bgcolor='#23272c',
                      paper_bgcolor='#23272c',
                      yaxis_title='Cumulative Covid Cases By State On Election Day',
                      xaxis_title='Change in Percentage of Trump Votes (2016 to 2020)')
    return fig

# static_scatter_tool()

def dynamic_scatter():
    """
    Returns scatterplot of relative covid rate v. political demographic - the interactive component
    """
    return html.Div(children=[
        dcc.Markdown('''
        # Relative Covid Rate v. Political Demographic
        Donald Trump has repeatedly dismissed covid-19 and encouraged his supporters to continue their lives as normal. 
        We wanted to see if areas where Trump received more support in the 2020 election had higher rates of covid-19 
        than the areas that voted more in favor of Joe Biden. We compare covid-19 cases among states by calculating a 
        "relative positivity rate" or "relative case density" for each state, which is the number of new daily cases per 
        person divided by the nation-wide positivity rate. For example, if a given state reports twice as many new cases 
        per 10,000 people than the country as a whole on a given day, that state's relative positivity rate on that day 
        would be 2. For each day since the beginning of the pandemic, we calculate the 7-day rolling average of confirmed 
        new positive cases in each state (of course, some states have more or less testing than others, so we must proceed 
        with some concern about the accuracy of our data). It appears that early on in the pandemic, democratic states were hit 
        harder than republican areas. This makes sense -- we recall that the early outbreaks of covid-19 were in cities, 
        which tend to be heavily democratic. Only once the pandemic progressed did the virus spread to more rural and 
        conservative parts of the country. Since the early days of the pandemic, we have seen the trend reverse: now, 
        heavily Trump-supporting states are doing worse than the states that backed Joe Biden in the election. This change in 
        trend can be seen by dragging the slider
        in the scatterplot below.

        We also note that the actual relationship between relative covid-19 positivity rate and political demographic
        is probably more robust than what is visible in the scatterplot. This is because democratic states tend to test
        more, and so Trump-supporting states likely have depressed case count data.


        ''', className='eleven columns', style={'paddingLeft': '5%'})
    ], className="row")


def dynamic_scatter_tool():
    """
    Returns the What-If tool as a dash `html.Div`. The view is a 8:3 division between
    demand-supply plot and rescale sliders.
    """

    mark_values = {}
    for i in range(len(roll7.columns)):
        if i % 30 == 0:
            mark_values[i+1] = str(roll7.columns[i])[:-10]
        else:
            mark_values[i+1] = ""

    return html.Div([
        # html.Div([
        #     html.Pre(children = "Covid Infections and Political Preference by State",
        #     style = {"text-align": "center", "font-size":"100%", "color":"black"})
        # ]),

        html.Div([
            dcc.Graph(id = 'dynamic_graph')
        ]),

        html.Div([
            dcc.Slider(id = 'date_slider',
                min = 1,
                max = len(roll7.columns),
                value = 1,
                marks = mark_values,
                step = None,
                included = False
                )
        ], style = {"width": "70%", "position": "absolute",
                    "left": "5%"}),
        dcc.Markdown('''
        #
        # 
        ''')
    ])


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
        Additionally, population data was taken from [The US Census Bureau](https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/)
        in order to compare per-capita statistics. 

        ### Technology Stack

        The website was produced using a Dash website application and is hosted using the Gitpod online environment.
        The `app.py` script hosts the Dash components as well as visualizations created using Plot.ly.

        ### ETL and Database Design

        Our data is read from the links provided into dataframes in the `data_aquire.py` script. Additionally, 
        the script reformats and extracts the columns relevant to our analysis before upserting the rows of each
        dataframe as documents to 5 different collections in a MongoDB database. These 5 collections hold vote
        counts for 2016, vote counts for 2020, the number of new deaths for each day since February by county, the 
        number of new cases for each day since February by county, and the population of each county. Each of these
        collections is linked by a county idenfitication variable, which is the name of the county and the state 
        where it is located. The `database.py` script then pulls the data from the database into dataframes that are
        used to create the visualizations in `app.py`

        [ETL-EDA](https://colab.research.google.com/drive/1yk5KtZ6xdPCvOOSZKm6PS5HfPsLzwOrt#scrollTo=baENtC0LzWy8)

        [Enhancement](https://colab.research.google.com/drive/1Yciqr2xjSUfUpXm_XNqHOY-IwcVS1rha#scrollTo=KovafjNXno78)
        
        [Visualization](https://colab.research.google.com/drive/1qfAKwnTV0_8X3j2STkA9Iacm1J6eSkZB#scrollTo=wC34L9RotdwA)

        ''', className='eleven columns', style={'paddingLeft': '5%'})], className="row")


# def architecture_summary():
#     """
#     Returns the text and image of architecture summary of the project.
#     """
#     return html.Div(children=[
       
#         dcc.Markdown('''
#             #
#             ##
#             ###
#             #
#             ##
#             ###
#             # Project Architecture
#             This project uses MongoDB as the database. All data acquired are stored in raw form to the
#             database (with de-duplication). An abstract layer is built in `database.py` so all queries
#             can be done via function call. For a more complicated app, the layer will also be
#             responsible for schema consistency. A `plot.ly` & `dash` app is serving this web page
#             through. Actions on responsive components on the page is redirected to `app.py` which will
#             then update certain components on the page.  
#         ''', className='row eleven columns', style={'paddingLeft': '5%'}),

#         html.Div(children=[
#             html.Img(src="https://docs.google.com/drawings/d/e/2PACX-1vQNerIIsLZU2zMdRhIl3ZZkDMIt7jhE_fjZ6ZxhnJ9bKe1emPcjI92lT5L7aZRYVhJgPZ7EURN0AqRh/pub?w=670&amp;h=457",
#                      className='row'),
#         ], className='row', style={'textAlign': 'center'}),

#         dcc.Markdown('''
        
#         ''')
#     ], className='row')


# # Sequentially add page components to the app's layout
def dynamic_layout():
    return html.Div([
        page_header(),
        html.Hr(),
        description(),
        # dcc.Graph(id='trend-graph', figure=static_stacked_trend_graph(stack=False)),
        # dcc.Graph(id='stacked-trend-graph', figure=static_stacked_trend_graph(stack=True)),
        dynamic_scatter(),
        dynamic_scatter_tool(),
        static_scatter(),
        dcc.Graph(id='static_scatter', figure=static_scatter_tool()),
    ], className='row', id='content')


# # set layout to a function which updates upon reloading
app.layout = dynamic_layout

@app.callback(
    dash.dependencies.Output("dynamic_graph", "figure"),
    [dash.dependencies.Input("date_slider", "value")]
)

def update(date_chosen):
    print(date_chosen)
    pct_trump = grouped["Donald Trump 2020"] / (grouped["Donald Trump 2020"] + grouped["Joe Biden"])
    x = pct_trump
    roll7.drop(["state"], axis = 1)
    y = roll7.iloc[:, date_chosen] / grouped["POPESTIMATE2019"] / (roll7.sum() / grouped["POPESTIMATE2019"].sum())[date_chosen]
    z = grouped["state"]
    new_df = pd.DataFrame(zip(x,y,z), columns = ['pct_trump', 'relative_case_density', 'state'])
    new_df.drop_duplicates(subset = ["state"], inplace = True)

    scatterplot = px.scatter(
        data_frame = new_df,
        x = 'pct_trump',
        y = 'relative_case_density',
        hover_data = ['state'],
        height = 550
    )

    scatterplot.update_traces(textposition = 'top center')
    scatterplot.update_layout(template='plotly_dark',
                title="Relative Covid-19 Rate v. 2020 Election Outcome by State",
                plot_bgcolor='#23272c',
                paper_bgcolor='#23272c',
                yaxis_title='Relative Covid-19 Rate',
                xaxis_title='2020 Percent Vote for Trump')
    scatterplot.add_annotation(dict(font=dict(color='yellow',size=15),
                                    x=0,
                                    y=-0.12,
                                    showarrow=False,
                                    text="You have selected the date " + str(roll7.columns[date_chosen-1][:-10]),
                                    textangle=0,
                                    xanchor='left',
                                    xref="paper",
                                    yref="paper"))
    
    return (scatterplot)

if __name__ == '__main__':
    app.run_server(debug=True, port=1050, host='0.0.0.0')
