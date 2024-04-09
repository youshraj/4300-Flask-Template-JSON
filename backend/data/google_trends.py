import time
from pytrends.request import TrendReq
from pytrends.exceptions import ResponseError
import pandas as pd

def get_celebrity_interest(celebrity_name, retries=6):
    attempt = 0
    #time.sleep(60)
    while attempt < retries:
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            #pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25), proxies=['https://34.203.233.13:80','https://35.201.123.31:880',], retries=2, backoff_factor=0.1, requests_args={'verify':False})
            #trending within the last three months in the US (can change if needed)
            pytrends.build_payload([celebrity_name], timeframe='today 3-m', geo="US") 
            interest_over_time_df = pytrends.interest_over_time()
            popularity_score = interest_over_time_df[celebrity_name].iloc[-1]
            return popularity_score
        except ResponseError as e:
            if e.response.status_code == 429:  # TooManyRequestsError
                wait_time = 2 ** attempt
                print(f"Too many requests. Retrying in {wait_time} seconds.")
                time.sleep(wait_time)
                attempt += 1
        except KeyError as e:
            popularity_score = 0
            return popularity_score
    raise Exception("Failed after multiple retries.")

# celebrity_names = ["Ariana Grande", "Tom Hanks", "Taylor Swift", "Messi", "Morgan Wallen"]
actors_df = pd.read_csv('cleaned_celeb_info.csv')
interest_scores = []
# try:
#     last_index = pd.read_csv('last_index.csv')['Index'][0]
# except FileNotFoundError:
#     last_index = 0


for index, row in actors_df.iterrows():
    celebrity_name = row['Celebrity Name']
    popularity_score = get_celebrity_interest(celebrity_name)
    interest_scores.append(popularity_score)
# for index, row in actors_df.iloc[last_index:].iterrows():
#     celebrity_name = row['Celebrity Name'] 
#     try:
#         popularity_score = get_celebrity_interest(celebrity_name)
#         actors_df.loc[index, 'Interest Score'] = popularity_score
#     except Exception as e:
#         print(f"Failed to get popularity score for {celebrity_name}: {e}")
#         actors_df.loc[index, 'Interest Score'] = None  # Set to NaN if request failed

#     # Save the current index to resume from in case of failure
#     pd.DataFrame({'Index': [index]}).to_csv('last_index.csv', index=False)

actors_df['Interest Score'] = interest_scores

#overwrites existing file adding new column
actors_df.to_csv('cleaned_celeb_info.csv', index=False)

