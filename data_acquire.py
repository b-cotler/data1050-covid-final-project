"""
Bonneville Power Administration, United States Department of Energy
"""
import time
import sched
import pandas as pd
import logging
import requests
from io import StringIO

#import utils
from database import upsert_data


election_2020_url = "https://raw.githubusercontent.com/b-cotler/data1050-covid-final-project/main/data/president_county_candidate.csv" 
election_2016_url = "https://raw.githubusercontent.com/b-cotler/data1050-covid-final-project/main/data/countypres_2000-2016.csv"
confirmed_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
deaths_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"
population_url = "https://raw.githubusercontent.com/b-cotler/data1050-covid-final-project/main/data/pop_data.csv"
urls = [election_2016_url, election_2020_url, confirmed_url, deaths_url, population_url]

MAX_DOWNLOAD_ATTEMPT = 5
DOWNLOAD_PERIOD = 24*60*60         # second
logger = logging.Logger(__name__)
#utils.setup_logger(logger, 'data.log')


def download_data(urls=urls, retries=MAX_DOWNLOAD_ATTEMPT):
    """Returns BPA text from `BPA_SOURCE` that includes power loads and resources
    Returns None if network failed
    """
    text = None
    for i in range(retries):
        try:
            dfs = []
            for j in range(len(urls)):
                s = requests.get(urls[j]).content
                if j < 4:
                    #s.raise_for_status()
                    dfs.append(pd.read_csv(StringIO(s.decode('utf-8'))))
                else:
                    #s.raise_for_status()
                    dfs.append(pd.read_csv(StringIO(s.decode('ISO-8859-1'))))
        except requests.exceptions.HTTPError as e:
            logger.warning("Retry on HTTP Error: {}".format(e))
    if len(dfs) < 5:
        logger.error('download_data too many FAILED attempts')
    return dfs


def filter_data(dfs):
    """Converts `text` to `DataFrame`, removes empty lines and descriptions
    """
    df_2016 = dfs[0]
    df_2020 = dfs[1]
    df_confirmed = dfs[2]
    df_deaths = dfs[3]
    df_population = dfs[4]

    #Preprocess the deaths dataframe
    df_deaths["county_id"] = df_deaths["Province_State"] + ", " + df_deaths["Admin2"]
    df_deaths = df_deaths.loc[:, '1/22/20':]

    #Preprocess the poopulation dataframe
    df_population["CTYNAME"] = [s.replace(" County", "") for s in df_population["CTYNAME"]]
    df_population["county_id"] = df_population["STNAME"] + ", " + df_population["CTYNAME"]

    #Preprocess the confirmed cases dataframe
    df_confirmed['county_id'] = df_confirmed['Province_State'] + ', ' + df_confirmed['Admin2']
    df_confirmed = df_confirmed.loc[:, '1/22/20':]

    #Preprocess the 2016 election dataframe
    df_2016['county_id'] = df_2016['state']+', '+df_2016['county']
    df_2016.drop(columns=['county'],inplace=True)
    df_2016 = df_2016[df_2016['year'] == 2016]
    df_2016 = df_2016[df_2016['party'].isin(['democrat', 'republican'])]
    df_2016.head()
    municipal_cities = [k for k, v in df_2016['county_id'].value_counts().to_dict().items() if v > 2]
    for city in municipal_cities:
        df_city = df_2016[df_2016['county_id'] == city]
        hillary_votes = df_city[df_city['candidate'] == "Hillary Clinton"]['candidatevotes'].sum()
        trump_votes = df_city[df_city['candidate'] == "Donald Trump"]['candidatevotes'].sum()
        trump_row = df_city.iloc[1].to_dict()
        hillary_row = df_city.iloc[2].to_dict()
        total_votes = trump_row['totalvotes'] + hillary_row['totalvotes']
        trump_row['candidatevotes'] = trump_votes
        trump_row['totalvotes'] = total_votes
        hillary_row['candidatevotes'] = hillary_votes
        hillary_row['totalvotes'] = total_votes
        hillary_row['FIPS'] = trump_row['FIPS']
        df_2016 = df_2016[df_2016['county_id'] != city] # drop old columns
        df_2016 = df_2016.append(hillary_row, ignore_index=True)
        df_2016 = df_2016.append(trump_row, ignore_index=True)
    df_2016 = df_2016.pivot(index = "county_id", columns = "candidate", values = "candidatevotes")

    col1 = df_2016.index.to_numpy()
    cols2 = df_2016.to_numpy()

    df_2016 = pd.DataFrame(cols2, columns=["Donald Trump", "Hillary Clinton"])
    df_2016.insert(0, "county_id", col1)

    #Preprocess the 2020 election dataframe
    df_2020["county_id"] = df_2020["state"] + ', ' + df_2020["county"]
    df_2020["county_id"] = df_2020["county_id"].apply(lambda x: x.replace(" County", ""))
    df_2020["county_id"] = df_2020["county_id"].apply(lambda x: x.replace(" Parish", ""))
    df_2020["county_id"] = df_2020["county_id"].apply(lambda x: x.replace("ED", "District"))
    df_2020= df_2020[df_2020['party'].isin(['DEM','REP'])]
    df_2020 = df_2020.pivot(index = ["county_id", "state"], columns = "candidate", values = "total_votes")  

    col1 = df_2020.index.to_numpy()
    states = pd.DataFrame([i[1] for i in col1])
    county_id = pd.DataFrame([i[0] for i in col1])
    candidates = pd.DataFrame(df_2020.to_numpy())
    new = pd.concat([county_id, states, candidates], axis=1)
    new.columns = ["county_id", "state", "Donald Trump", "Joe Biden"]
    df_2020 = new

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
    grouped["state"] = grouped.index
    cases = grouped.loc[:, "1/23/20_confirmed":"1/22/20_deaths"].iloc[:, :-1]
    daily = [cases.iloc[:, i] - cases.iloc[:, i-1] for i in range(1,len(cases.columns))]
    for i in range(len(daily)):
        cases.iloc[:, i] = daily[i]

    roll7 = cases.loc[:, "1/29/20_confirmed":]
    roll7["state"] = grouped.index
    for i in range(len(roll7.columns)):
        avg = cases.iloc[:, i:i+7].mean(axis=1)
    roll7.iloc[:, i] = avg

    grouped["Donald Trump 2020"] / (grouped["Donald Trump 2020"] + grouped["Joe Biden"])
    collection_id = [(grouped, "grouped"), (roll7, "roll7")]
    #collection_id = [(df_2020, "df_2020"), (df_2016, "df_2016"), (df_confirmed, "df_confirmed"), (df_deaths, "df_deaths"), (df_population, "df_population")]
    return collection_id


def update_once():
    dfs = download_data()
    collection_id = filter_data(dfs)
    upsert_data(collection_id)


def main_loop(timeout=DOWNLOAD_PERIOD):
    scheduler = sched.scheduler(time.time, time.sleep)

    def _worker():
        try:
            update_once()
        except Exception as e:
            logger.warning("main loop worker ignores exception and continues: {}".format(e))
        scheduler.enter(timeout, 1, _worker)    # schedule the next event

    scheduler.enter(0, 1, _worker)              # start the first event
    scheduler.run(blocking=True)


if __name__ == '__main__':
    main_loop()


