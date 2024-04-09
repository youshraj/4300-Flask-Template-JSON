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

actors_df = pd.read_csv('cleaned_celeb_info.csv')
interest_scores = []


for index, row in actors_df.iterrows():
    celebrity_name = row['Celebrity Name']
    popularity_score = get_celebrity_interest(celebrity_name)
    interest_scores.append(popularity_score)


actors_df['Interest Score'] = interest_scores

#overwrites existing file adding new column
actors_df.to_csv('cleaned_celeb_info.csv', index=False)

