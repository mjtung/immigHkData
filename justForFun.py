#%%

import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import numpy as np
from datetime import datetime, timedelta
import os
import plotly
import plotly.offline as py
py.init_notebook_mode(connected=True)
import plotly.graph_objects as go
import plotly.express as px #necessary for full plotting capability
from IPython.display import Image
#%% Part 1. scrape data
# dates = np.arange(datetime(2020,1,24), datetime(2022,2,20), timedelta(days=1))
dates = np.arange(datetime(2022,2,21), datetime(2022,4,10), timedelta(days=1))
DIRECTORY = '/Users/mjtung/Documents/2022'
res = pd.DataFrame()
for d in dates:
    dateStr = pd.to_datetime(d).strftime('%Y%m%d')
    url = r'https://www.immd.gov.hk/eng/stat_{}.html'.format(dateStr)

    r = requests.get(url)
    # df_list = pd.read_html(r.text) # this parses all the tables in webpages to a list
    # df = df_list[0]
    # # df.columns = df.columns.swaplevel(0,-1)  # swap main column header to the top
    # # df.head()
    # df.columns = df.columns.droplevel([1,2,3])
    # df.loc[df['Control Point']=='Total']
    soup = bs(r.content, 'html.parser')
    tbl = pd.read_html('<table>'+
        str(soup.find_all('tbody')[0])+
        '</table>'
        )[0]
    tbl = tbl.iloc[:, 2:]
    nunique = tbl.nunique()
    cols_to_drop = nunique[nunique == 1].index
    tbl = tbl.drop(cols_to_drop, axis=1)
    cols = soup.find('thead').find_all('tr')[-1]
    colNames = [x['id'] for x in cols.find_all('th')]
    colNames = ['Control_Point'] + colNames
    tbl.columns = colNames
    tbl = tbl.set_index('Control_Point')
    tbl = tbl.drop(index='Total', axis=0)
    tbl['Type'] = ['Airport' if x=='Airport' else 'Other' for x in tbl.index]
    summ = tbl.groupby('Type').sum().reset_index()
    summ['Date'] = d
    res = pd.concat((res, summ))
# %% Part 1b. Save Data
# res.to_csv(os.path.join(DIRECTORY, 'immigrationStats20210701-20220220.csv'))
# res.to_csv(os.path.join(DIRECTORY, 'immigrationStats20200124-20220220.csv'))
res.to_csv(os.path.join(DIRECTORY, 'immigrationStats20220221-20220410.csv'))
# %% Part 2a. Load data from CSV:
csvsToRead = ['immigrationStats20200124-20220220.csv', 'immigrationStats20220221-20220410.csv']
resTmp = []
for csv in csvsToRead:
    resTmp.append(pd.read_csv(os.path.join(DIRECTORY, csv)))
res = pd.concat(resTmp)
#%% Part 2b. Analyse Data
startDateAnalysis = '2020-03-21'
badDate = '2021-12-19'
pd.options.plotting.backend='plotly'

res['NetArrivals'] = res['Total_Arrival'] - res['Total_Departure']

plotThis = res.groupby('Date').sum()[['Total_Arrival', 'Total_Departure']]
plotThis.loc[badDate] = np.nan

rollingData = plotThis[plotThis.index>startDateAnalysis].rolling(7, min_periods=6).mean()
rollingData['Net_Arrival'] = rollingData.iloc[:,0] - rollingData.iloc[:,1]
fig = rollingData.plot(title='7 day average all HK ports (source Immigration Department)')
imgBytes = fig.to_image(format='png')
display(Image(imgBytes))

rollingData2 = plotThis[plotThis.index>startDateAnalysis].cumsum()
rollingData2['Net_Arrival'] = rollingData2.iloc[:,0] - rollingData2.iloc[:,1]
fig = rollingData2.iloc[:,-1].plot(title='Cumsum @ all HK ports (source Immigration Department)')
imgBytes = fig.to_image(format='png')
display(Image(imgBytes))
#%%
plotThis = res[res['Type']=='Airport'].groupby('Date').sum()[['Total_Arrival', 'Total_Departure']]
# plotThis.loc[badDate] = np.nan

rollingData = plotThis[plotThis.index>startDateAnalysis].rolling(7, min_periods=6).mean()
rollingData['Net_Arrival'] = rollingData.iloc[:,0] - rollingData.iloc[:,1]
fig = rollingData.plot(title='7 day average @ HKG airport (source Immigration Department)')
imgBytes = fig.to_image(format='png')
display(Image(imgBytes))

rollingData2 = plotThis[plotThis.index>startDateAnalysis].cumsum()
rollingData2['Net_Arrival'] = rollingData2.iloc[:,0] - rollingData2.iloc[:,1]
fig = rollingData2.plot(title='Cumsum @ HKG airport (source Immigration Department)')
imgBytes = fig.to_image(format='png')
display(Image(imgBytes))

#%%
plotThis = res.groupby('Date').sum()[['NetArrivals']]
plotThis.loc[badDate] = np.nan

fig = plotThis[plotThis.index>startDateAnalysis].cumsum().plot(title='Cumulative net arrivals (source Immigration Department)')
imgBytes = fig.to_image(format='png')
display(Image(imgBytes))
#%%
plotThis = res[res['Type']=='Airport'].groupby('Date').sum()[['NetArrivals']]
# plotThis.loc[badDate] = np.nan

fig = plotThis[plotThis.index>startDateAnalysis].cumsum().plot(title='Cumulative net arrivals @ HKG airport (source Immigration Department)')
imgBytes = fig.to_image(format='png')
display(Image(imgBytes))

# %%
