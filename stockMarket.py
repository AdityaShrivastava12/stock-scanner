from enum import Enum
from datetime import date, timedelta
from nsepythonserver import *
import pandas as pd


date_format = "%d-%m-%Y"
# default_date_format = "%Y-%m-%d"

bhavcopy_of_latestdate_df = None
bhavcopy_of_comparatordate_df = None


def download_bhavcopy_file(date):
    try:
        return get_bhavcopy(date)
    except Exception as e:
        print(e)
        return None

def get_dates_for_bhavcopies():
    comparator_days = 5
    today = date.today()
    # today = today - timedelta(days=1)
    comparator_date = today - timedelta(days=comparator_days)

    if(today.strftime("%A") == "Saturday"):
        today = today - timedelta(days=1)
    if(comparator_date.strftime("%A") == "Saturday"):
        comparator_date = comparator_date - timedelta(days=1)

    return [today.strftime(date_format), comparator_date.strftime(date_format)]

[today_date, comparator_date] = get_dates_for_bhavcopies()


bhavcopy_of_latestdate_df = download_bhavcopy_file(today_date)
bhavcopy_of_comparatordate_df = download_bhavcopy_file(comparator_date)

bhavcopy_of_latestdate_df = bhavcopy_of_latestdate_df.loc[bhavcopy_of_latestdate_df[' SERIES'] == " EQ"]
bhavcopy_of_comparatordate_df = bhavcopy_of_comparatordate_df.loc[bhavcopy_of_comparatordate_df[" SERIES"] == " EQ"]

# print(bhavcopy_of_comparatordate_df.to_string())

masterdf = bhavcopy_of_latestdate_df.loc[:, ['SYMBOL',' SERIES', ' CLOSE_PRICE']]
masterdf.columns = ['SYMBOL','SERIES', 'CLOSE_PRICE_CURRENT_DATE']

masterdf = pd.merge(masterdf, bhavcopy_of_comparatordate_df.loc[:,["SYMBOL"," CLOSE_PRICE"]], on="SYMBOL")
masterdf.columns=['SYMBOL','SERIES', 'CLOSE_PRICE_CURRENT_DATE','CLOSE_PRICE_COMPARATOR_DATE']

marketcapdf = pd.read_excel("./files/marketcapdec2023.xlsx")
marketcapdf.columns = ["Sr.No","SYMBOL", "COMPANY NAME", "MARKETCAP(IN LAKHS)"]
marketcapdf = marketcapdf.loc[marketcapdf["MARKETCAP(IN LAKHS)"] != "*Not available for trading as on December 31, 2023"]
masterdf = pd.merge(masterdf, marketcapdf.loc[:, ["SYMBOL", "MARKETCAP(IN LAKHS)"]], on="SYMBOL")
filteredmasterdf = masterdf.loc[(masterdf["MARKETCAP(IN LAKHS)"] >= 1000000)]
filteredmasterdf.loc[:,"PERCENT CHANGE"] = ((filteredmasterdf["CLOSE_PRICE_CURRENT_DATE"] - filteredmasterdf["CLOSE_PRICE_COMPARATOR_DATE"])/filteredmasterdf["CLOSE_PRICE_COMPARATOR_DATE"])*100
positive_change_df = filteredmasterdf.loc[(filteredmasterdf["PERCENT CHANGE"] >= 1)]

final_sorted_df = positive_change_df.sort_values(by="PERCENT CHANGE", ascending=False)
print(final_sorted_df.to_string())
print(len(final_sorted_df)) 