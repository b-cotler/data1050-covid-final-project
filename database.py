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


# def upsert_data(collection_names):
#     """
#     Update MongoDB database `energy` and collection `energy` with the given `DataFrame`.
#     """
#     for collection_df in collection_names:
#         db = client.get_database("elections_and_covid")
#         collection = db.get_collection(collection_df[1])
#         update_count = 0
#         for record in collection_df[0].to_dict('records'):
#             result = collection.replace_one(
#                 filter={'county_id': record['county_id']},    # locate the document if exists
#                 replacement=record,                         # latest document
#                 upsert=True)                                # update if exists, insert if not
#             if result.matched_count > 0:
#                 update_count += 1
#             result = collection.insert_one(record)


def fetch_all_data():
    db = client.get_database("elections_and_covid_4")
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


# _fetch_all_bpa_as_df_cache = expiringdict.ExpiringDict(max_len=1,
#                                                        max_age_seconds=RESULT_CACHE_EXPIRATION)


# def fetch_all_bpa_as_df(allow_cached=False):
#     """Converts list of dicts returned by `fetch_all_bpa` to DataFrame with ID removed
#     Actual job is done in `_worker`. When `allow_cached`, attempt to retrieve timed cached from
#     `_fetch_all_bpa_as_df_cache`; ignore cache and call `_work` if cache expires or `allow_cached`
#     is False.
#     """
#     def _work():
#         data = fetch_all_bpa()
#         if len(data) == 0:
#             return None
#         df = pds.DataFrame.from_records(data)
#         df.drop('_id', axis=1, inplace=True)
#         return df

#     if allow_cached:
#         try:
#             return _fetch_all_bpa_as_df_cache['cache']
#         except KeyError:
#             pass
#     ret = _work()
#     _fetch_all_bpa_as_df_cache['cache'] = ret
#     return ret


if __name__ == '__main__':
    pass
    # print(fetch_all_data())
