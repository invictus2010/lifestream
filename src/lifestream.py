import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from matplotlib.pyplot import figure
from datetime import datetime
import matplotlib.ticker as mtick
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_transaction_log(
        df,
        orderid_col,
        datetime_col,
        customerid_col,
        quantity_col,
        unitprice_col,
):
    """
    Creates a transaction log that can be used in subsequent methods.

    The sample dataset from UC Irvine doesn't total up the value of 
    a single order/transaction. This method is to prep that transaction log.

    It accepts transaction data, and returns a DataFrame of a standard transaction
    log.

    Future state shall deal with other kinds of anomalies/cases.
    
    Parameters
    ----------
    df: :obj: DataFrame
        a Pandas DataFrame that contains your transactional data.
    orderid_col: string
        the column in df DataFrame that denotes the unique order_id.
    datetime_col:  string
        the column in df DataFrame that denotes the datetime the purchase was made.
    customerid_col: string
        the column in df DataFrame that denotes the unique customer_id.
    quantity_col: string
        the column in df DataFrame that denotes the quantity of items purchased in an order.
    unitprice_col: string
        the column in df DataFrame that denotes the unit price of items purchased in an order.
    Returns
    -------
    :obj: DataFrame
        A DataFrame with an order_id column, date column, customer_id column and a 'OrderValue' column, 
        which represents the total price of one transaction.
    """

    df['OrderValue'] = df[quantity_col] * df[unitprice_col]
    grouped = df.groupby([orderid_col, datetime_col, customerid_col])
    transaction_log = grouped.agg({'OrderValue': np.sum})
    transaction_log.reset_index(inplace=True)
    transaction_log[datetime_col] = transaction_log[datetime_col].astype(
        'datetime64[ns]')
    return transaction_log


def sales_chart(transaction_log,
                datetime_col,
                customerid_col,
                ordervalue_col,
                customer_count=True,
                title='Sales and Customers Per Month',
                ylabel1='Number of Customers Per Month',
                ylabel2='Sales ($) per Month'):
    """
    Creates a bar chart of monthly revenue with a line plot overlay of number of customers per month. 
    
    Parameters
    ----------
    transaction_log: :obj: DataFrame
        a Pandas DataFrame that contains your transaction log.
    datetime_col: string
        the column in transaction_log DataFrame that denotes the datetime of an order.
    ordervalue_col: string
        the column in transaction_log DataFrame that contains the total value of an order.
    customerid_col: string
        the column in transaction_log DataFrame that contains the unique customer_id.
    customer_count: boolean, optional
        boolean to select whether or not to plot number of customers per month on same plot.
    title: string, optional
        the plot's title. recommend changing if customer_count is False.
    ylabel1: string, optional
        the label for the line trace of the number of customers per month.
    ylabel2: string, optional
        the label for the bar plot of the revenue per month.
    
    -------
    axes: plotly.AxesSubplot
    """

    # Get time format correct of date column correct
    transaction_log[datetime_col] = pd.to_datetime(
        transaction_log[datetime_col])
    transaction_log = transaction_log.set_index(datetime_col)

    # Aggregate data on a monthly basis from transaction log. User user_id totals to create optional stacked
    # chart in the futre
    df = transaction_log.groupby(
        pd.Grouper(freq="M"))[ordervalue_col, customerid_col].agg({
            ordervalue_col:
            np.sum,
            customerid_col:
            pd.Series.nunique
        })

    # Plotting a dual axist chart depending on the user's preference, else
    # plot revenue/sales per month.
    if customer_count == True:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df.index,
                                 y=df[customerid_col].values,
                                 name=ylabel1),
                      secondary_y=True)
        fig.add_trace(go.Bar(x=df.index,
                             y=df[ordervalue_col].values,
                             name=ylabel2),
                      secondary_y=False)

        fig.update_layout(yaxis=dict(tickformat='$,'),
                          yaxis2=dict(tickformat=',', rangemode='tozero'),
                          title_text=title)
        fig.update_yaxes(title_text=ylabel1, secondary_y=True)
        fig.update_yaxes(title_text=ylabel2, secondary_y=False)
        fig.show()
    else:
        fig = px.bar(df,
                     x=df.index,
                     y=df[ordervalue_col],
                     labels={
                         ordervalue_col: ylabel2,
                         'x': 'Month-Year'
                     })
        fig.update_layout(yaxis=dict(tickformat='$,'), title_text=title)
        fig.update_traces(marker_color='#08A05C')
        fig.add_trace
        fig.show()


def cohort_retention_chart(transaction_log,
                           datetime_col,
                           ordervalue_col,
                           customerid_col,
                           cohort1,
                           cohort2,
                           cohort3,
                           title='Cohorts: User Retention',
                           ylabel="Percent of Cohort Purchasing"):
    """
    Creates a bar chart of monthly revenue. 
    
    Parameters
    ----------
    transaction_log: :obj: DataFrame
        a Pandas DataFrame that contains your transaction log.
    datetime_col: string
        the column in transaction_log DataFrame that denotes the datetime of an order.
    ordervalue_col: string
        the column in transaction_log DataFrame that contains the total value of an order.
    customerid_col: string
        the column in transaction_log DataFrame that contains the unique customer_id.
    cohort1: string
        the cohort in 'YYYY-MM' format whose monthly retention you want plotted.
    cohort2: string
        the cohort in 'YYYY-MM' format whose monthly retention you want plotted.
    cohort3: string
        the cohort in 'YYYY-MM' format whose montly retention you want plotted.
    title: string, optional
        the title of the plot.
    ylabel: string, optional
        the label for the y-axis of the plot.
    -------
    axes: matplotlib.AxesSubplot
    """
    # Define a monthly order period
    transaction_log['OrderPeriod'] = transaction_log[datetime_col].apply(
        lambda x: x.strftime('%Y-%m'))
    transaction_log.set_index(customerid_col, inplace=True)

    # Define the cohort group of a user
    transaction_log['CohortGroup'] = transaction_log.groupby(
        level=0)[datetime_col].min().apply(lambda x: x.strftime('%Y-%m'))
    transaction_log.reset_index(inplace=True)

    # Aggregate data based on cohort and monthly order period
    grouped = transaction_log.groupby(['CohortGroup', 'OrderPeriod'])
    cohorts = grouped.agg({
        customerid_col: pd.Series.nunique,
        ordervalue_col: np.sum
    })
    cohorts.rename(columns={customerid_col: 'TotalUsers'}, inplace=True)

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
    user_retention = cohorts['TotalUsers'].unstack(0).divide(cohort_group_size,
                                                             axis=1)

    #Plot it
    user_retention[[cohort1, cohort2, cohort3]].plot(figsize=(10, 5))
    plt.title(title)
    plt.xticks(np.arange(1, 12.1, 1))
    plt.xlim(1, 12)
    plt.ylabel(ylabel)


def new_customers_chart(transaction_log,
                        datetime_col,
                        customerid_col,
                        title='New Buyers by Month',
                        xlabel='Month of First Purchase',
                        ylabel='Number of New Buyers'):
    """
    Creates a bar chart of new buyers by month. 
    
    Parameters
    ----------
    transaction_log: :obj: DataFrame
        a Pandas DataFrame that contains your transaction log.
    datetime_col: string
        the column in transaction_log DataFrame that denotes the datetime of an order.
    customerid_col: string
        the column in transaction_log DataFrame that contains the unique customer_id.
    title: string, optional
        the title of the plot.
    xlabel: string, optional
        the label for the x-axis of the plot.
    ylabel: string, optional
        the label for the y-axis of the plot.
    -------
    axes: matplotlib.AxesSubplot
    """

    # Find which cohort a user belongs to. The cohort represents when they made their first purchase.
    transaction_log.set_index(customerid_col, inplace=True)
    transaction_log['CohortGroup'] = transaction_log.groupby(
        level=0)[datetime_col].min().apply(lambda x: x.strftime('%Y-%m'))
    transaction_log.reset_index(inplace=True)

    # Count number of unique customers in each cohort.
    grouped = transaction_log.groupby(['CohortGroup'])
    cohorts = grouped.agg({customerid_col: pd.Series.nunique})

    # Number of unique customer in each cohort represents the new buyers.
    cohorts.rename(columns={customerid_col: 'TotalUsers'}, inplace=True)
    cohorts.reset_index(inplace=True)
    cohorts.set_index(['CohortGroup'], inplace=True)

    # Plot it
    fig = px.bar(cohorts,
                 x=cohorts.index,
                 y='TotalUsers',
                 title=title,
                 labels={
                     'TotalUsers': ylabel,
                     'x': xlabel
                 })
    fig.update_traces(marker_color='#08A05C')
    fig.show()


def customer_type_revenue_mix(transaction_log,
                              datetime_col,
                              customerid_col,
                              ordervalue_col,
                              figsize=(12, 8),
                              rotation='vertical'):
    """
    Creates a stacked bar chart of percent of revenue by buyer type per month.
    Note: only a new buyer's first purchase counts towards new buyer revenue. If
    the customer repeats in the same month, subsequent transactions are counted as repeat buyer 
    revenue 
    
    Parameters
    ----------
    transaction_log: :obj: DataFrame
        a Pandas DataFrame that contains your transaction log.
    datetime_col: string
        the column in transaction_log DataFrame that denotes the datetime of an order.
    customerid_col: string
        the column in transaction_log DataFrame that contains the unique customer_id.
    ordervalue_col: string 
        the column in transaction_log DataFrame that contains the total value of an order.
    figsize: tuple, optional
        the size of the chart.
    rotation: string, optional
        rotation for x-axis tick marks; may be 'horizontal' or 'vertical'
    -------
    axes: matplotlib.AxesSubplot
    """
    # Identify a buyer's first transaction
    transaction_log.sort_values(datetime_col)
    transaction_log['NewBuyer'] = (
        ~transaction_log[customerid_col].duplicated()).astype(int)

    #Create an Initial Buyer DataFrame and Repeat Buyer DataFrame
    nb = transaction_log.loc[transaction_log['NewBuyer'] == 1]
    ob = transaction_log.loc[transaction_log['NewBuyer'] == 0]

    #Format New/Repeat Buyer DataFrames correctly
    nb[datetime_col] = nb[datetime_col].astype(
        'datetime64[ns]')  # This line causes a SettingWithCopyWarning
    nb['OrderPeriod'] = nb[datetime_col].apply(lambda x: x.strftime(
        '%Y-%m'))  # This line causes a SettingWithCopyWarning
    nb.set_index(customerid_col, inplace=True)
    grouped = nb.groupby(['OrderPeriod'])
    cohorts = grouped.agg({
        ordervalue_col: np.sum,
    })
    cohorts.rename(columns={ordervalue_col: 'TotalOrderValue'}, inplace=True)

    ob[datetime_col] = ob[datetime_col].astype(
        'datetime64[ns]')  # This line causes a SettingWithCopyWarning
    ob['OrderPeriod'] = ob[datetime_col].apply(lambda x: x.strftime(
        '%Y-%m'))  # This line causes a SettingWithCopyWarning
    ob.set_index(customerid_col, inplace=True)
    grouped2 = ob.groupby(['OrderPeriod'])
    cohorts2 = grouped2.agg({
        ordervalue_col: np.sum,
    })
    cohorts2.rename(columns={ordervalue_col: 'TotalOrderValue'}, inplace=True)

    # Format Axis Data for Plot
    cohorts.reset_index(inplace=True)
    cohorts.set_index('OrderPeriod', inplace=True)
    months = cohorts.index.to_numpy()
    r = []
    i = -1
    for x in months:
        i += 1
        r.append(i)

    # Get Data for Plot
    raw_data = {
        'InitialBuyers': cohorts['TotalOrderValue'],
        'RepeatBuyers': cohorts2['TotalOrderValue']
    }
    df = pd.DataFrame(raw_data)

    # Get Totals
    totals = [i + j for i, j in zip(df['InitialBuyers'], df['RepeatBuyers'])]
    greenBars = [i / j * 100 for i, j in zip(df['InitialBuyers'], totals)]
    orangeBars = [i / j * 100 for i, j in zip(df['RepeatBuyers'], totals)]

    # Plot Dimensions
    barWidth = 0.85
    plt.rcParams["figure.figsize"] = figsize

    # Create Initial Buyer Bars
    plt.bar(r,
            greenBars,
            color='#08A05C',
            edgecolor='white',
            width=barWidth,
            label='New Buyers')

    # Create Repeat Buyer Bars
    plt.bar(r,
            orangeBars,
            bottom=greenBars,
            color='#f9bc86',
            edgecolor='white',
            width=barWidth,
            label='Repeat Buyers')

    # Labels and Legend
    plt.xticks(r, months, rotation=rotation)
    plt.ylabel('Percent of Monthly Revenue')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    plt.show()


def customer_type_count(transaction_log,
                        datetime_col,
                        customerid_col,
                        figsize=(12, 8),
                        rotation='vertical'):
    """
    Creates a stacked bar chart of percent of buyer types per month
    Note: only a new buyer's first purchase counts towards new buyer. If
    the customer repeats in the same month, subsequent transactions are counted towards repeat buyer.
    
    
    Parameters
    ----------
    transaction_log: :obj: DataFrame
        a Pandas DataFrame that contains your transaction log.
    datetime_col: string
        the column in transaction_log DataFrame that denotes the datetime of an order.
    customerid_col: string
        the column in transaction_log DataFrame that contains the unique customer_id.
    ordervalue_col: string 
        the column in transaction_log DataFrame that contains the total value of an order.
    figsize: tuple, optional
        the size of the chart.
    rotation: string, optional
        rotation for x-axis tick marks; may be 'horizontal' or 'vertical'
    -------
    axes: matplotlib.AxesSubplot
    """
    # Identify a buyer's first transaction
    transaction_log.sort_values(datetime_col)
    transaction_log['NewBuyer'] = (
        ~transaction_log[customerid_col].duplicated()).astype(int)

    #Create an Initial Buyer DataFrame and Repeat Buyer DataFrame
    nb = transaction_log.loc[transaction_log['NewBuyer'] == 1]
    ob = transaction_log.loc[transaction_log['NewBuyer'] == 0]

    #Format New/Repeat Buyer DataFrames correctly
    nb[datetime_col] = nb[datetime_col].astype(
        'datetime64[ns]')  # This line causes a SettingWithCopyWarning
    nb['OrderPeriod'] = nb[datetime_col].apply(lambda x: x.strftime(
        '%Y-%m'))  # This line causes a SettingWithCopyWarning
    nb.set_index(datetime_col, inplace=True)
    grouped = nb.groupby(['OrderPeriod'])
    cohorts = grouped.agg({customerid_col: pd.Series.nunique})
    cohorts.rename(columns={customerid_col: 'CustomerCount'}, inplace=True)

    ob[datetime_col] = ob[datetime_col].astype(
        'datetime64[ns]')  # This line causes a SettingWithCopyWarning
    ob['OrderPeriod'] = ob[datetime_col].apply(lambda x: x.strftime(
        '%Y-%m'))  # This line causes a SettingWithCopyWarning
    ob.set_index(datetime_col, inplace=True)
    grouped2 = ob.groupby(['OrderPeriod'])
    cohorts2 = grouped2.agg({customerid_col: pd.Series.nunique})
    cohorts2.rename(columns={customerid_col: 'CustomerCount'}, inplace=True)

    # Format Axis Data for Plot
    cohorts.reset_index(inplace=True)
    cohorts.set_index('OrderPeriod', inplace=True)
    months = cohorts.index.to_numpy()
    r = []
    i = -1
    for x in months:
        i += 1
        r.append(i)

    # Get Data for Plot
    raw_data = {
        'InitialBuyers': cohorts['CustomerCount'],
        'RepeatBuyers': cohorts2['CustomerCount']
    }
    df = pd.DataFrame(raw_data)

    # Get Totals
    totals = [i + j for i, j in zip(df['InitialBuyers'], df['RepeatBuyers'])]
    greenBars = [i / j * 100 for i, j in zip(df['InitialBuyers'], totals)]
    orangeBars = [i / j * 100 for i, j in zip(df['RepeatBuyers'], totals)]

    # Plot Dimensions
    barWidth = 0.85
    plt.rcParams["figure.figsize"] = figsize

    # Create Initial Buyer Bars
    plt.bar(r,
            greenBars,
            color='#08A05C',
            edgecolor='white',
            width=barWidth,
            label='New Buyers')

    # Create Repeat Buyer Bars
    plt.bar(r,
            orangeBars,
            bottom=greenBars,
            color='#f9bc86',
            edgecolor='white',
            width=barWidth,
            label='Repeat Buyers')

    # Labels and Legend
    plt.xticks(r, months, rotation=rotation)
    plt.ylabel('Count of Customers')
    plt.legend(loc='upper left', bbox_to_anchor=(1, 1), ncol=1)
    plt.show()


def c3_chart(transaction_log,
             customer_id,
             datetime_col,
             ordervalue_col,
             title="Total Quarterly Sales by Acquisition Cohort Over Time"):
    """
    Creates a stacked area chart of revenue from acquisition cohort by time. Grouped and aggregated by
    quarter.
    
    Parameters
    ----------
    transaction_log: :obj: DataFrame
        a Pandas DataFrame that contains your transaction log.
    datetime_col: string
        the column in transaction_log DataFrame that denotes the datetime of an order.
    customerid_col: string
        the column in transaction_log DataFrame that contains the unique customer_id.
    ordervalue_col: string 
        the column in transaction_log DataFrame that contains the total value of an order.
    figsize: tuple, optional
        the size of the chart.
    rotation: string, optional
        rotation for x-axis tick marks; may be 'horizontal' or 'vertical'
    -------
    axes: matplotlib.AxesSubplot
    """

    # throw away all unwanted data
    transaction_log = transaction_log[[
        customer_id, datetime_col, ordervalue_col
    ]]
    #convert the date string to datetime object
    transaction_log[datetime_col] = pd.to_datetime(
        transaction_log[datetime_col])

    # copy the part of the original data into a pivot table to compute the min of order date
    # based on the customer id
    pivot1 = transaction_log.pivot_table(index=customer_id,
                                         values=datetime_col,
                                         aggfunc='min')
    # rename the column order date to birthday (the first day of purchase)
    pivot1 = pivot1.rename(columns={datetime_col: "birthday"})
    # make that into datetime just in case
    pivot1['birthday'] = pd.to_datetime(pivot1['birthday'])

    # merge computed data with original data
    merged = pd.merge(transaction_log, pivot1, on=customer_id, how='right')
    # turn the new dates and old dates into quaters for financial years
    merged['order_date'] = pd.PeriodIndex(merged[datetime_col], freq='Q')
    merged['birthday'] = pd.PeriodIndex(merged['birthday'], freq='Q')

    # make final pivot table to place the first dates quaters against the order dates quaters
    cohort_pivot = merged.pivot_table(index='birthday',
                                      columns=datetime_col,
                                      values=ordervalue_col,
                                      aggfunc='sum')

    # change the datetime.Period objects to string object to be plotted
    def quarterToString(cell):
        return cell.strftime('Q%q %Y')

    cohort_pivot.columns = cohort_pivot.columns.map(quarterToString)
    cohort_pivot.index = cohort_pivot.index.map(quarterToString)
    cohort_pivot.reindex()

    fig = go.Figure(layout={"title": title})
    for i in range(len(cohort_pivot.columns)):
        fig.add_trace(
            go.Scatter(name=cohort_pivot.columns.values[i],
                       x=cohort_pivot.index,
                       y=cohort_pivot.iloc[i, :],
                       stackgroup='one',
                       fill='tonexty',
                       mode='none'))

    fig.show()


def c3_pivot(transaction_log, customer_id, datetime_col, ordervalue_col):
    # throw away all unwanted data
    transaction_log = transaction_log[[
        customer_id, datetime_col, ordervalue_col
    ]]
    #convert the date string to datetime object
    transaction_log[datetime_col] = pd.to_datetime(
        transaction_log[datetime_col])

    # copy the part of the original data into a pivot table to compute the min of order date
    # based on the customer id
    pivot1 = transaction_log.pivot_table(index=customer_id,
                                         values=datetime_col,
                                         aggfunc='min')
    # rename the column order date to birthday (the first day of purchase)
    pivot1 = pivot1.rename(columns={datetime_col: "birthday"})
    # make that into datetime just in case
    pivot1['birthday'] = pd.to_datetime(pivot1['birthday'])

    # merge computed data with original data
    merged = pd.merge(transaction_log, pivot1, on=customer_id, how='right')
    # turn the new dates and old dates into quaters for financial years
    merged['order_date'] = pd.PeriodIndex(merged[datetime_col], freq='Q')
    merged['birthday'] = pd.PeriodIndex(merged['birthday'], freq='Q')

    # make final pivot table to place the first dates quaters against the order dates quaters
    cohort_pivot = merged.pivot_table(index='birthday',
                                      columns=datetime_col,
                                      values=ordervalue_col,
                                      aggfunc='sum')

    # change the datetime.Period objects to string object to be plotted
    def quarterToString(cell):
        return cell.strftime('Q%q %Y')

    cohort_pivot.columns = cohort_pivot.columns.map(quarterToString)
    cohort_pivot.index = cohort_pivot.index.map(quarterToString)
    return cohort_pivot.reindex()
