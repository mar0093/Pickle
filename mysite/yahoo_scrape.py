import re
import requests
import pandas as pd
import os
import io
import csv
import time
import datetime
import mysql.connector



def get_yahoo_ticker_data(ticker, **keyword_parameters):
    res = requests.get('https://finance.yahoo.com/quote/' + ticker + '/history')
    yahoo_cookie = res.cookies['B']
    yahoo_crumb = None
    pattern = re.compile('.*"CrumbStore":\{"crumb":"(?P<crumb>[^"]+)"\}')
    for line in res.text.splitlines():
        m = pattern.match(line)
        if m is not None:
            yahoo_crumb = m.groupdict()['crumb']
    cookie_tuple = yahoo_cookie, yahoo_crumb
    current_date = int(time.time())
    if ('time_stamp' in keyword_parameters):
        start_date = keyword_parameters['time_stamp']
    else:
        start_date = "0"
    url_kwargs = {'symbol': ticker,'timestamp_start': start_date, 'timestamp_end': current_date,
        'crumb': cookie_tuple[1]}
    url_price = 'https://query1.finance.yahoo.com/v7/finance/download/' \
                '{symbol}?period1={timestamp_start}&period2={timestamp_end}&interval=1d&events=history' \
                '&crumb={crumb}'.format(**url_kwargs)
    response = requests.get(url_price, cookies={'B': cookie_tuple[0]}).content
    df = pd.read_csv(io.StringIO(response.decode('utf-8')))
    return df


def create_csv(stock, df):
    if not os.path.exists('/home/mar0093/mysite/static/yahoo/{}.csv'): #check for directory exist
            os.makedirs('/home/mar0093/mysite/static/yahoo/{}.csv')    #make directory if it doesn't
            print('making directory')
    if not os.path.exists('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock)): #check if stock exists
        df.to_csv('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock), index= False) #create stock in directory, ensure no index



def update_csv(stock, new_df):

    org_df = pd.read_csv('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock))
    print(new_df)
    exist_in_df = False
    for i in range(len(new_df)):
        #print("hi i")
        for j in range(len(org_df)):
            #print("hi j")
            if str(new_df['Date'][i]) == str(org_df['Date'][j]):
                exist_in_df = True
            if exist_in_df is True:
                break
        if exist_in_df is True:  # if in the org df, concat the two df at point i
            appendable_df = new_df.head(i)
            con_df = pd.concat([appendable_df, org_df])
            print(con_df)
            con_df.to_csv('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock), index=False) #return update to folder
            break


def reverse(stock):

    BC_file = open('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock), 'r')
    BC_reader = csv.reader(BC_file)
    print(BC_reader)
    next(BC_reader)
    my_list = []
    for row in reversed(list(BC_reader)):
        my_list.append(row)

    labels = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    df = pd.DataFrame.from_records(my_list, columns=labels)
    return df


def update_csv2(stock):
    org_df = pd.read_csv('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock))
    len_of_df = len(org_df.index)-1
    str_date = org_df['Date'][len_of_df]
    time_stamp = time.mktime(datetime.datetime.strptime(str_date, "%Y-%m-%d").timetuple())
    time_stamp = int(time_stamp)
    df = get_yahoo_ticker_data(stock, time_stamp=time_stamp)
    # df = df.iloc[::-1] flips df around
    df = df[3:]
    con_df = pd.concat([org_df, df])
    con_df.to_csv('/home/mar0093/mysite/static/yahoo/{}.csv'.format(stock), index=False)  # return update to folder

def yahoo_to_db(ticker, df):
    cnx = mysql.connector.connect(user='mar0093', password='pickledb', host='mar0093.mysql.pythonanywhere-services.com', database='mar0093$pickledb_pyany')
    cursor = cnx.cursor()
    ticker = ticker[:3]
    ticker = ticker.lower()
    cursor.execute("SELECT count(*) from  "+ticker)
    count = cursor.fetchone()
    count = count[0]
    df = df.dropna()

    if df.shape[0] >= count:
        cursor.execute("DROP TABLE IF EXISTS "+ticker)
        cursor.execute("CREATE TABLE IF NOT EXISTS "+ticker+"( Date VARCHAR(20), Open NUMERIC(10,4), High  NUMERIC(8,4), Low  NUMERIC(8,4), Close NUMERIC(8,4), Adj_Close NUMERIC(8,4), Volume INT(20))")
        i = 1
        for row in df.iterrows():
            list = row[1].values
            i += 1
            cursor.execute("INSERT INTO "+ticker+"(Date, Open, High, Low, Close, Adj_Close, Volume) VALUES('%s','%f','%f','%f','%f','%f','%d')" % (tuple(list)))
        cnx.commit()
        cnx.close()

def run_main(stock):
    df = get_yahoo_ticker_data(stock)
    yahoo_to_db(stock, df)

def update_one_ticker():
    try:
        ticker = input("Ticker please.")
        run_main(ticker)
        print("Gathering data")
    except:
        print("Parse error, trying again")
        time.sleep(2)
        print("Re-running main")
        run_main(ticker)
    print('Done.')

def update_yahoo_csv():
    '''
    Runs the stack scrape on all tickers and updates the ~/yahoo folder
    with all up to date ticker information.
    :return: nothing
    '''
    with open("/home/mar0093/mysite/tickers.txt") as f:
        content = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    content = [x.strip() for x in content]
    retry_list = []
    for i in content:
        try:
            ticker = i
            print("Current ticker: " + i)
            print("Gathering data")
            run_main(ticker)
        except:
            print("Parse error, trying again")
            time.sleep(2)
            print("Re-running main")
            try:
                ticker = i
                run_main(ticker)
                print("Gathering data a second time")
            except:
                print("Parse error, adding to retry list.")
                retry_list.append(i)
        print('Done.')
        print(' ')

    print("Length of second round tickers"+len(retry_list))
    for i in retry_list:
        try:
            ticker = i
            print("Current ticker: " + i)
            print("Gathering data")
            run_main(ticker)
        except:
            print("Parse error, trying again")
            time.sleep(2)
            print("Re-running main")
            try:
                ticker = i
                run_main(ticker)
                print("Gathering data a second time")
            except:
                print("Parse error, ignoring.")
        print('Done.')
        print(' ')


update_yahoo_csv()