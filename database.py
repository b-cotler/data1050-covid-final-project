import logging
import pymongo
import pandas as pd
import expiringdict

# import utils

IRL = "mongodb+srv://main_user:data1050@project-cluster.oo7x7.mongodb.net/admin"
client = pymongo.MongoClient(IRL)
logger = logging.Logger(__name__)
#utils.setup_logger(logger, 'db.log')
RESULT_CACHE_EXPIRATION = 10             # seconds


def upsert_data(collection_names):
    """
    Update MongoDB database `elections and covid` and all collections.
    """
    for collection_df in collection_names:
        db = client.get_database("elections_and_covid_5")
        collection = db.get_collection(collection_df[1])
        update_count = 0
        for record in collection_df[0].to_dict('records'):
            result = collection.replace_one(
                filter={"state": record["state"]},    # locate the document if exists
                replacement=record,                         # latest document
                upsert=True)                                # update if exists, insert if not
            if result.matched_count > 0:
                update_count += 1
            result = collection.insert_one(record)


def fetch_all_data():
    db = client.get_database("elections_and_covid_5")
    df_names = ["grouped", "roll7"]
    dfs = []

    for df_name in df_names:
        collection = db.get_collection(df_name)
        data = list(collection.find())
        logger.info(str(len(data)) + ' documents read from the db')
        df = pd.DataFrame.from_records(data)    
        df.drop('_id', axis=1, inplace=True)
        dfs.append(df)

    return dfs


if __name__ == '__main__':
    print(fetch_all_data())
