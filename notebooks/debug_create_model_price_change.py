#!/usr/bin/env python
# coding: utf-8

# # pyAstroTrader
# 
# # Create Model
# 
# After downloading the quotes data for the asset selected with the ASSET_TO_CALCULATE environment variable, we need to add the astrological data to the quotes and then generate a XGBoost model
# 
# First of all, we need to import the models that we need to process.

# In[ ]:


import os
import gc
import multiprocessing as mp
import pickle

import pandas as pd
import dask.dataframe as dd
from dask.multiprocessing import get
import numpy as np
import plotly.graph_objects as go

from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split as ttsplit
from sklearn.metrics import mean_squared_error as mse

import xgboost as xgb
from xgboost import XGBClassifier
from xgboost import plot_importance
from xgboost import plot_tree

from IPython.display import display, HTML

import eli5



# ```pyastrotrader``` is a python module that we created, in order to calculate astrological charts based on specific dates, and also to calculate aspects between charts

# In[ ]:


from pyastrotrader import calculate_chart, calculate_aspects, calculate_transits, get_degrees, get_degree
from pyastrotrader.utils import create_input_json
from pyastrotrader.constants import *


# Import all settings and helper functions that we will use in the next cells

# In[ ]:


from settings import *
from helpers import *

USING_CACHED_DATAFRAME = False
CACHE_FILE = './output/{}.{}.cache'.format(ASSET_TO_CALCULATE, datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d') )
CACHE_ASTRO_COLUMNS = './output/{}.{}.astro.cache'.format(ASSET_TO_CALCULATE, datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d') )

if os.path.isfile(CACHE_FILE):
    USING_CACHED_DATAFRAME = True


# Read the CSV file with the quotes downloaded, and also create a counter column to help in the calculated columns below

# In[ ]:


if not USING_CACHED_DATAFRAME:
    StockPrices = pd.read_csv("{}.csv".format(SOURCE_FILE))
    StockPrices['Counter'] = np.arange(len(StockPrices))


# Using several helper functions from ```helpers.py``` module, for each day we need to determine several indicators like:
# * The current trend
# * the future trend
# * If there was a change in the trend ( a swing trade opportunity )
# * current volatility for the previous days
# * and many other indicators

# In[ ]:


if not USING_CACHED_DATAFRAME:
    max_counter = StockPrices['Counter'].max()

    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['CorrectedDate'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : correct_date(x), axis =1)).compute(scheduler='processes')
    StockPrices['PreviousStartPrice'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : get_previous_stock_price(StockPrices, x, SWING_TRADE_DURATION), axis =1), meta='float').compute(scheduler='processes')
    StockPrices['FutureFinalPrice'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : get_future_stock_price(StockPrices, x, max_counter, SWING_TRADE_DURATION), axis =1 ), meta='float').compute(scheduler='processes')
    StockPrices['PreviousStartDate'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : get_previous_stock_date(StockPrices, x, SWING_TRADE_DURATION), axis =1 ), meta='float').compute(scheduler='processes')
    StockPrices['FutureFinalDate'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : get_future_stock_date(StockPrices, x, max_counter, SWING_TRADE_DURATION), axis =1 ), meta='float').compute(scheduler='processes')

    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['CurrentTrend'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : calculate_current_trend(x), axis = 1), meta='float').compute(scheduler='processes')

    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['FutureTrend'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : calculate_future_trend(x), axis = 1), meta='float').compute(scheduler='processes')

    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['SwingStrength'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : calculate_swing_strenght(x), axis =1), meta='float').compute(scheduler='processes')
    StockPrices['IntradayVolatility'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : calculate_intraday_volatility(StockPrices, x, SWING_TRADE_DURATION), axis =1), meta='float').compute(scheduler='processes')

    StockPrices['FutureTrendMax'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : get_future_stock_max_price(StockPrices, x, max_counter, SWING_TRADE_DURATION), axis = 1), meta='float').compute(scheduler='processes')
    StockPrices['FutureTrendMin'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : get_future_stock_min_price(StockPrices, x, max_counter, SWING_TRADE_DURATION), axis = 1), meta='float').compute(scheduler='processes')

    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['IsSwing'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : detect_swing_trade(x, SWING_EXPECTED_VOLATILITY), axis =1), meta='float').compute(scheduler='processes')
    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['IsSwing'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : clean_swing_trade(StockPrices, x, SWING_EXPECTED_VOLATILITY), axis =1), meta='float').compute(scheduler='processes')

    StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
    StockPrices['StockIncreasedPrice'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : detect_price_increase(x, STAGNATION_THRESHOLD), axis =1), meta='float').compute(scheduler='processes')
    StockPrices['StockDecreasedPrice'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : detect_price_decrease(x, STAGNATION_THRESHOLD), axis =1), meta='float').compute(scheduler='processes')
    StockPrices['StockStagnated'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : detect_price_stagnated(x, STAGNATION_THRESHOLD), axis =1), meta='float').compute(scheduler='processes')
    StockPrices['StockPriceChange'] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : calculate_price_change(StockPrices, x), axis =1), meta='float').compute(scheduler='processes')

    StockPrices['TARGET_IS_SWING'] = StockPrices['IsSwing']
    StockPrices['TARGET_PRICE_INCREASE'] = StockPrices['StockIncreasedPrice']
    StockPrices['TARGET_PRICE_DECREASE'] = StockPrices['StockDecreasedPrice']
    StockPrices['TARGET_PRICE_STAGNATION'] = StockPrices['StockStagnated']
    StockPrices['TARGET_PRICE_CHANGE'] = StockPrices['StockPriceChange']                                                                


# After all the analisys, we can generate a excel file in order to help debug the indicators generated above

# In[ ]:


if not USING_CACHED_DATAFRAME:
    output_excel_file='./output/{}.Analisys.xlsx'.format(ASSET_TO_CALCULATE)
    StockPrices.to_excel(output_excel_file)


# To debug the indicators, we can plot a stock chart with the swing indication, but this is commented out as it requires a lot of computational resources.

# In[ ]:


"""
swing_to_chart = []
for index, current_swing in StockPrices[StockPrices['IsSwing'] == 1].iterrows():
    swing_to_chart.append(dict(
        x0=current_swing['CorrectedDate'], 
        x1=current_swing['CorrectedDate'], 
        y0=0, 
        y1=1, 
        xref='x', 
        yref='paper',
        line_width=2))
"""


# In[ ]:


"""
fig = go.Figure(data=[go.Candlestick(
                x=StockPrices['CorrectedDate'],
                open=StockPrices['Open'],
                high=StockPrices['High'],
                low=StockPrices['Low'],
                close=StockPrices['Price'])])
fig.update_layout(
    title="{} Detected Swing Trade Opportunities".format(ASSET_TO_CALCULATE),
    width=1000,
    height=500,
    xaxis_rangeslider_visible=False,
    shapes=swing_to_chart,
    margin=go.layout.Margin(
        l=0,
        r=0,
        b=0,
        t=30,
        pad=4
    ),    
)
#fig.show()
"""


# Well, in order to calculate the astrological indicators for the current ASSET_TO_CALCULATE, we need to generate a natal chart of the asset, which traditionally is the first trade date on the current exchange 

# In[ ]:


if not USING_CACHED_DATAFRAME:
    asset_natal_chart_input = create_input_json(NATAL_DATE, 
                                            DEFAULT_PARAMETERS, 
                                            DEFAULT_CONFIG)

    asset_natal_chart = calculate_chart(asset_natal_chart_input)
    dates_to_generate = list(StockPrices['CorrectedDate'])


# Now, for all the dates on the pandas dataframe containing the quotes, we need to generate astrological charts with the list of planets to consider: ```PLANETS_TO_CALCULATE```, their aspects: ```ASPECTS_TO_CALCULATE```

# In[ ]:


if not USING_CACHED_DATAFRAME:
    def generate_charts(current_date):
        chart_input = create_input_json(current_date + 'T10:00:00-03:00', 
                                          DEFAULT_PARAMETERS, 
                                          DEFAULT_CONFIG)
        current_chart = calculate_chart(chart_input)
        return (current_date,
                current_chart, 
                calculate_transits(asset_natal_chart, current_chart, PLANETS_TO_CALCULATE, ASPECTS_TO_CALCULATE, 4),
                calculate_aspects(current_chart, PLANETS_TO_CALCULATE, ASPECTS_TO_CALCULATE, 4))

    with mp.Pool(processes = NPARTITIONS) as p:
        results = p.map(generate_charts, dates_to_generate)

    for x in results:
        charts[x[0]] = x[1]
        aspects[x[0]] = x[2]
        aspects_transiting[x[0]] = x[3]


# We have the natal chart and also all the charts for each date in the pandas dataframe, now we need to add to the pandas dataframe, the astrological aspects that occur in each date, we will set only to 1 if there is a aspect occuring or 0 if not, we also will check for aspects on the transiting chart as well as aspects between the natal chart and the transiting chart
# 
# **astro_columns** will indicate the name of the columns containing astrological indicators in the pandas dataframe

# In[ ]:


if not USING_CACHED_DATAFRAME:
    astro_columns = []

    for current_planet in PLANETS_TO_CALCULATE:
        if current_planet != SATURN:
            column_name="ASTRO_{}_POSITION".format(PLANETS[current_planet]).upper()
            StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
            StockPrices[column_name] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : int(get_degree_for_planet(x, current_planet) / 3), axis =1), meta='int').compute(scheduler='processes')
            StockPrices[column_name] = pd.to_numeric(StockPrices[column_name],  downcast='float', errors='coerce')   
            astro_columns.append(column_name)   
        for second_planet in PLANETS_TO_CALCULATE:
            if current_planet == second_planet:
                continue

            column_name="ASTRO_{}_{}_DIFF".format(PLANETS[current_planet], PLANETS[second_planet]).upper()
            StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
            StockPrices[column_name] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : int(int(get_degree_for_planet(x, current_planet) - get_degree_for_planet(x, second_planet))/ 3), axis =1), meta='int').compute(scheduler='processes')
            StockPrices[column_name] = pd.to_numeric(StockPrices[column_name],  downcast='float', errors='coerce')   
            astro_columns.append(column_name)   

            column_name="ASTRO_{}_{}_DIFF_ABS".format(PLANETS[current_planet], PLANETS[second_planet]).upper()
            StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
            StockPrices[column_name] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : abs(int(get_degree_for_planet(x, current_planet) - get_degree_for_planet(x, second_planet))/ 3), axis =1), meta='int').compute(scheduler='processes')
            StockPrices[column_name] = pd.to_numeric(StockPrices[column_name],  downcast='float', errors='coerce')   
            astro_columns.append(column_name)   


    for first_planet in PLANETS_TO_CALCULATE:
        for second_planet in PLANETS_TO_CALCULATE:
            for aspect in ASPECTS_TO_CALCULATE:
                column_name="ASTRO_{}_{}_{}".format(PLANETS[first_planet],ASPECT_NAME[aspect],PLANETS[second_planet]).upper()
                aspect_column_name = column_name
                astro_columns.append(column_name)
                StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
                StockPrices[column_name] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : is_aspected(x, first_planet, second_planet, aspect), axis =1), meta='float').compute(scheduler='processes')
                StockPrices[column_name] = pd.to_numeric(StockPrices[column_name],  downcast='float', errors='coerce')

                StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
                column_name="ASTRO_TRANSITING_{}_{}_{}".format(PLANETS[first_planet],ASPECT_NAME[aspect],PLANETS[second_planet]).upper()
                astro_columns.append(column_name)
                StockPrices[column_name] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : is_aspected_transiting(x, first_planet, second_planet, aspect), axis =1), meta='float').compute(scheduler='processes')
                StockPrices[column_name] = pd.to_numeric(StockPrices[column_name],  downcast='float', errors='coerce')                 


# We need also to determine which planets are retrograde in each date of the pandas dataframe

# In[ ]:


if not USING_CACHED_DATAFRAME:
    for first_planet in []:
        column_name="ASTRO_{}_RETROGADE".format(PLANETS[first_planet]).upper()
        astro_columns.append(column_name)
        StockPricesDask = dd.from_pandas(StockPrices, npartitions=NPARTITIONS)
        StockPrices[column_name] = StockPricesDask.map_partitions(lambda df : df.apply(lambda x : is_retrograde(x, first_planet), axis =1), meta='float').compute(scheduler='processes')
        StockPrices[column_name] = pd.to_numeric(StockPrices[column_name],  downcast='float',errors='coerce')

if USING_CACHED_DATAFRAME:        
    StockPrices = pd.read_pickle(CACHE_FILE)
    with open(CACHE_ASTRO_COLUMNS, 'rb') as f:
        astro_columns = pickle.load(f)    
else:
    StockPrices.to_pickle(CACHE_FILE)
    with open(CACHE_ASTRO_COLUMNS, 'wb') as f:
        pickle.dump(astro_columns, f)


# After the pandas dataframe has been populated with the astrological indicators, we can now train the XGBoost models in order to predict the following target variables:
# * Price Increase: There is a increase in price after that date
# * Price Decrease: There is a decrease in price after that date
# * Price Stagnation: There is a stagnation in price after that date
# * Swing Trade: There is a change in trend after that date
#     
# **Important to notice that we will use as input only the astro_columns columns which contains astrological indicators**

# In[ ]:


booster_price_change, score_price_change = get_best_booster('TARGET_PRICE_CHANGE', MAX_INTERACTIONS, StockPrices, astro_columns)
print("Best Score for Price Change Model:{}".format(score_price_change))


# We can now save each model score in a text file

# In[ ]:


if not USING_CACHED_DATAFRAME:
    score_price_change_file_name = './output/{}.score.price.change.txt'.format(ASSET_TO_CALCULATE)

    with open(score_price_change_file_name, 'w') as f:
        f.write("{}:{}".format(ASSET_TO_CALCULATE,str(score_price_change)))


# We can also calculate for each model the relevant astrological variables, used in each model

# In[ ]:


if not USING_CACHED_DATAFRAME:
    relevant_features_price_change = sorted( ((v,k) for k,v in booster_price_change.get_score().items()), reverse=True)

    display(relevant_features_price_change)


# We can now write such features to text files in order to improve the analisys of the model.

# In[ ]:


if not USING_CACHED_DATAFRAME:
    def write_features(f, list_to_write):
        for item_to_write in list_to_write:
            f.write('{}-{}'.format(ASSET_TO_CALCULATE,str(item_to_write).replace(')','').replace('(','').replace('\'','').replace(' ','') + '\n'))

    features_price_change_file_name = './output/{}.features.price.change.txt'.format(ASSET_TO_CALCULATE)

    with open(features_price_change_file_name, 'w') as f:
        write_features(f,relevant_features_price_change)    


# We can check the predicted value for each model on the pandas dataframe, creating a column for it 

# In[ ]:


if not USING_CACHED_DATAFRAME:
    StockPrices['PredictPriceChange'] = StockPrices.apply(lambda x:predict_score(x, booster_price_change, StockPrices, astro_columns), axis =1)


# And save the model for further use on the ```Predict.ipynb``` notebook

# In[ ]:


booster_price_change.save_model('./output/{}_price_change.model'.format(ASSET_TO_CALCULATE))


# And save a excel with all the data produced...

# In[ ]:


if not USING_CACHED_DATAFRAME:
    output_excel_file='./output/{}.Analisys.xlsx'.format(ASSET_TO_CALCULATE) 
    StockPrices.to_excel(output_excel_file)


# The plotting of charts has been commented out as it is very resource consuming...

# In[ ]:


"""
swing_to_chart = []
for index, current_swing in StockPrices[StockPrices['PredictSwingTradeScore'] > 0.9].iterrows():
    swing_to_chart.append(dict(
        x0=current_swing['CorrectedDate'], 
        x1=current_swing['CorrectedDate'], 
        y0=0, 
        y1=1, 
        xref='x', 
        yref='paper',
        line_width=2))
"""        


# In[ ]:


"""
fig = go.Figure(data=[go.Candlestick(
                x=StockPrices['CorrectedDate'],
                open=StockPrices['Open'],
                high=StockPrices['High'],
                low=StockPrices['Low'],
                close=StockPrices['Price'])])
fig.update_layout(
    title="{} Swing Trade Opportunities detected by XGBoost".format(ASSET_TO_CALCULATE),
    width=1000,
    height=500,
    xaxis_rangeslider_visible=False,
    shapes=swing_to_chart,
    margin=go.layout.Margin(
        l=0,
        r=0,
        b=0,
        t=30,
        pad=4
    ),    
)
#fig.show()
"""


# In[ ]:


"""
swing_to_chart = []
for index, current_swing in StockPrices[StockPrices['PredictPriceIncreaseScore'] > 5].iterrows():
    swing_to_chart.append(dict(
        x0=current_swing['CorrectedDate'], 
        x1=current_swing['CorrectedDate'], 
        y0=0, 
        y1=1, 
        xref='x', 
        yref='paper',
        line_width=2))
"""        


# In[ ]:


"""
fig = go.Figure(data=[go.Candlestick(
                x=StockPrices['CorrectedDate'],
                open=StockPrices['Open'],
                high=StockPrices['High'],
                low=StockPrices['Low'],
                close=StockPrices['Price'])])
fig.update_layout(
    title="{} Price Increase Opportunities detected by XGBoost (Min {}%)".format(ASSET_TO_CALCULATE, STAGNATION_THRESHOLD),
    width=1000,
    height=500,
    xaxis_rangeslider_visible=False,
    shapes=swing_to_chart,
    margin=go.layout.Margin(
        l=0,
        r=0,
        b=0,
        t=30,
        pad=4
    ),    
)
#fig.show()
"""


# In[ ]:





# In[ ]:




