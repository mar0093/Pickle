from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
import numpy
import csv
import mysql.connector
import pandas as pd

def create_table(ticker):

    df = pd.read_csv('/home/mar0093/mysite/static/yahoo/{}.csv'.format(ticker))
    df = df.dropna()

    cnx = mysql.connector.connect(user='mar0093', password='pickledb', host='mar0093.mysql.pythonanywhere-services.com', database='mar0093$pickledb_pyany')
    print('hello')
    cursor = cnx.cursor()
    ticker = ticker[:3]
    ticker = ticker.lower()
    cursor.execute("DROP TABLE IF EXISTS "+ticker)
    cursor.execute("CREATE TABLE IF NOT EXISTS "+ticker+"( Date VARCHAR(20), Open NUMERIC(10,4), High  NUMERIC(8,4), Low  NUMERIC(8,4), Close NUMERIC(8,4), Adj_Close NUMERIC(8,4), Volume INT(20))")
    i = 1
    for row in df.iterrows():
        list = row[1].values
        #list = numpy.insert(list, 0, int(i))
        i += 1
        cursor.execute("INSERT INTO "+ticker+"(Date, Open, High, Low, Close, Adj_Close, Volume) VALUES('%s','%f','%f','%f','%f','%f','%d')" % (tuple(list)))
    #cursor.execute("ALTER TABLE " + ticker + " ADD COLUMN tick VARCHAR(20) DEFAULT 0 AFTER Id")
    cnx.commit()
    cnx.close()

def ticker_list():
    with open('/home/mar0093/mysite/tickers.txt') as f:
        for line in f:
            try:
                line = line.replace('\r', '').replace('\n', '')
                create_table(line)
                print("Creating "+ line)
            except:
                print("fail :(")


ticker_list()
#create_table('DDR.AX')
