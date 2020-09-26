import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.pyplot import figure
from datetime import datetime
import matplotlib.ticker as mtick

def sales_chart(transaction_log, date_col, monetary_val, user_id):
  
  #Get time format correct of date column correct
  transaction_log[date_col] = pd.to_datetime(transaction_log[date_col])
  transaction_log['date'] = transaction_log[date_col].dt.date
  transaction_log['date'] = pd.to_datetime(transaction_log['date'])
  transaction_log = transaction_log.set_index('date')
  
  #Aggregate data on a monthly basis from transaction log
  df = transaction_log.groupby(pd.Grouper(freq="M"))[monetary_val, user_id].agg({monetary_val: 'sum', user_id: 'count'})
  
  #Plot
  fig, ax = plt.subplots()
  plt.gcf().autofmt_xdate()
  height = df[monetary_val]
  bars = pd.to_datetime(df.index)
  bars = bars.strftime("%b-%Y")
  y_pos = np.arange(len(bars))
  fmt = '${x:,.0f}'
  tick = mtick.StrMethodFormatter(fmt)
  ax.yaxis.set_major_formatter(tick)
  ax.set_xlabel('Month')
  ax.set_ylabel('Sales ($)')
  ax.set_title('Sales Over Time')
  plt.xticks(y_pos, bars)
  plt.bar(y_pos, height)
  every_nth = 4
  for n, label in enumerate(ax.xaxis.get_ticklabels()):
      if n % every_nth != 0:
          label.set_visible(False)

def create_transaction_log(df, invoicenum, date_col, quantity, unitprice, customerid):
    grouped = df.groupby(['InvoiceNo', 'InvoiceDate','CustomerID'])
    transaction_log = grouped.agg({
    'OrderValue': np.sum
    })
    transaction_log.rename(columns ={
    'OrderValue': 'monetary_val'
    }, inplace=True)
    transaction_log.reset_index(inplace = True)
    transaction_log['InvoiceDate'] = transaction_log['InvoiceDate'].astype('datetime64[ns]') 
    return transaction_log

def cohort_retention_chart(df, date_col, order_id, user_id, monetary_val, cohort1, cohort2, cohort3):
     # Define a monthly order period
    df['OrderPeriod'] = df[date_col].apply(lambda x: x.strftime('%Y-%m'))
    df.set_index(user_id, inplace=True)
    
    # Define the cohort group of a user
    df['CohortGroup'] = df.groupby(level=0)[date_col].min().apply(lambda x: x.strftime('%Y-%m'))
    df.reset_index(inplace=True)
    
    # Aggregate data based on cohort and monthly order period
    grouped = df.groupby(['CohortGroup', 'OrderPeriod'])
    cohorts = grouped.agg({user_id: pd.Series.nunique,
                       order_id: pd.Series.nunique,
                       monetary_val: np.sum})
    cohorts.rename(columns={user_id: 'TotalUsers',
                        order_id: 'TotalOrders'}, inplace=True)

    # Create a cohort period column, which reflects number of months on site. Month of first purchase = 1
    def cohort_period(df):
        df['CohortPeriod'] = np.arange(len(df)) + 1
        return df
    cohorts = cohorts.groupby(level=0).apply(cohort_period)

    # reindex the DataFrame
    cohorts.reset_index(inplace=True)
    cohorts.set_index(['CohortGroup', 'CohortPeriod'], inplace=True)

    # create a Series holding the total size of each CohortGroup
    cohort_group_size = cohorts['TotalUsers'].groupby(level=0).first()

    #User Retention Matrix
    user_retention = cohorts['TotalUsers'].unstack(0).divide(cohort_group_size, axis=1)

    #Plot it
    user_retention[[cohort1, cohort2, cohort3]].plot(figsize=(10,5))
    plt.title('Cohorts: User Retention')
    plt.xticks(np.arange(1, 12.1, 1))
    plt.xlim(1, 12)
    plt.ylabel('% of Cohort Purchasing')
