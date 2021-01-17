
import sys
import os
from flask import send_from_directory
import time
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators



from functools import wraps
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import mpld3
import pandas as pd
import matplotlib.dates as dates
from matplotlib import ticker
import matplotlib.animation as animation
import matplotlib.animation as manimation; manimation.writers.list()
import mpl_finance
#from sklearn import preprocessing, cross_validation, svm
#from sklearn.linear_model import LinearRegression, Ridge
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from statistics import mean



app = Flask(__name__)


#configuring MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pickle'
app.config['MYSQL_DB'] = 'pickledb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init MySQL
mysql = MySQL(app)

#add secret key
app.secret_key = 'my_pickle'
## Below pulls articles from data.py##
#Articles = Articles()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/watchlist')
def shares():
    cur = mysql.connection.cursor()
    # Get articles
    result = cur.execute("SELECT * FROM articles")
    # Get all articles
    articles = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('watchlist.html', articles=articles)
    else:
        flash('No Articles Found.', 'danger')
        return render_template('watchlist.html')
    # CLose connection

@app.route('/shares/<string:id>/')
def shares_disp(id):
    cur = mysql.connection.cursor()
    # Get articles
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    # Get all articles
    article = cur.fetchone()
    return render_template('share_disp.html', article=article)

@app.route('/shares2/<string:aticker>/<string:graph_type>',methods=['GET', 'POST'])
def shares_disp2(aticker, graph_type):
    cur = mysql.connection.cursor()
    # Get articles
    cap_id = aticker.upper()
    aticker = aticker.lower()
    result = cur.execute("SELECT * FROM " + aticker)
    # Get all articles
    my_result = cur.execute("SELECT * FROM " + aticker + " ORDER BY Date DESC LIMIT 1")
    my_result = cur.fetchone()
    cur.close()
    cur = mysql.connection.cursor()
    print('b')
    sql = "SELECT * FROM " + aticker
    cur.execute(sql)
    all_result = cur.fetchall()
    AI_df = pd.DataFrame(list(all_result), columns=['Close', 'Open', 'High', 'Low', 'Volume'])
    #ai_values, last_ai_value = AI(30,AI_df)
    df = pd.DataFrame(list(all_result), columns=["Date", "Open", "Close", "High", "Low", "Volume"])
    df["Close_av_100"] = df['Close'].rolling(100).mean()
    df["Close_av_30"] = df['Close'].rolling(30).mean()
    if graph_type =="default":
        df = df.tail(60)
    else:
        df = df.tail(int(graph_type))
    print("c")
    df["mpld3_date"] =[dt.datetime.strptime(d, '%Y-%m-%d') for d in df["Date"]]
    df["Date"] = [dt.datetime.strptime(d, '%Y-%m-%d').toordinal() for d in df["Date"]]
    ai_first_date = df["Date"].iloc[-1]
    ai_dates = []
    for i in range(1,31):
        ai_dates.append(i + ai_first_date)
    df = df.set_index(df["Date"])
    quotes = [tuple([df["Date"].tolist()[i],
                     df["Open"].tolist()[i],
                     df["High"].tolist()[i],
                     df["Low"].tolist()[i],
                     df["Close"].tolist()[i]]) for i in range(len(df.index))]  # _1

    fig, [ax, ax2] = plt.subplots(2, 1,figsize=(12, 7), sharex=True)
    ax = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=2, colspan=1,sharex=ax)
    print("d")
    mpl_finance.candlestick_ohlc(ax, quotes,  colorup='g', colordown='r',width=0.6)
    print("e")
    ax.plot(df["Date"].tolist(), df["Close_av_100"],label='MA_100')
    ax.plot(df["Date"].tolist(), df["Close_av_30"],label='MA_30')
    candle_colours = []
    for i in range(len(df["Date"].tolist())):
        if df["Open"].tolist()[i] >= df["Close"].tolist()[i]:
            candle_colours.append('r')
        else:
            candle_colours.append('g')
    ax2.bar(df["Date"].tolist(), df["Volume"], color=candle_colours)
    ax.legend()
    ax.xaxis_date()
    ax2.xaxis_date()
    print("f")
    fig.autofmt_xdate()
    fig.tight_layout()

    #This is including AI
    fig2, [ax, ax2] = plt.subplots(2, 1,figsize=(12, 7), sharex=True)
    ax = plt.subplot2grid((6, 1), (0, 0), rowspan=5, colspan=1)
    ax2 = plt.subplot2grid((6, 1), (5, 0), rowspan=2, colspan=1,sharex=ax)
    mpl_finance.candlestick_ohlc(ax, quotes,  colorup='g', colordown='r',width=0.6)
    #Try adding new AI
    close_list, high_list, low_list, open_list = beta_candlestick_AI( AI_df)

    ai_quotes = [tuple([ai_dates[i],
                        open_list[i],
                        high_list[i],
                        low_list[i],
                        close_list[i]]) for i in range(len(ai_dates))]

    mpl_finance.candlestick_ohlc(ax, ai_quotes,  colorup='#52D017', colordown='#F535AA',width=0.6)


    ax.plot(df["Date"].tolist(), df["Close_av_100"],label='MA_100')
    ax.plot(df["Date"].tolist(), df["Close_av_30"],label='MA_30')
    #ax.plot(ai_dates, ai_values, label='ridge_Prediction')
    candle_colours = []
    for i in range(len(df["Date"].tolist())):
        if df["Open"].tolist()[i] >= df["Close"].tolist()[i]:
            candle_colours.append('r')
        else:
            candle_colours.append('g')
    ax2.bar(df["Date"].tolist(), df["Volume"], color=candle_colours)
    ax.legend()
    ax.xaxis_date()
    ax2.xaxis_date()
    fig2.autofmt_xdate()
    fig2.tight_layout()

    end = int(len(df["Open"])-1)
    pct_change = round(((df['Open'].iloc[end]/df['Open'].iloc[0])-1)*100,2)
    test_var = mpld3.fig_to_html(fig)
    print('here')
    test_var2 = mpld3.fig_to_html(fig2)
    cur.close()
    return render_template('share_disp2.html', test_var=test_var, test_var2=test_var2, id=cap_id, result=my_result, pct_change=pct_change)

def sigmoid(x):
    return 1.0/(1 + np.exp(-x))

def sigmoid_derivative(x):
    return x * (1.0 - x)

class NeuralNetwork:
    """
    This is the modified Neural network

    It has a minmaxscaler for the traits (x values)
    The y values have been normalized
    """
    def __init__(self, x, y):
        np.random.seed(666)
        self.input      = x
        self.train_mean = np.mean(x)
        self.train_std  = np.std(x)
        self.stdize     = (x - self.train_mean)/self.train_std
        self.z          = np.array([6.4])
        self.weights1   = np.random.rand(self.input.shape[1], 29)
        self.weights2   = np.random.rand(29, 1)
        self.y          = [float(i)/self.z for i in y[:, ]]# normalize y data
        self.output     = np.zeros(y.shape)
        self.data_test  = self.y

    def denormalize_data(self, value):
        return float(value * self.z)

    def feedforward(self):
        self.layer1 = sigmoid(np.dot(self.stdize, self.weights1))
        self.output = sigmoid(np.dot(self.layer1, self.weights2))


    def backprop(self):
        # application of the chain rule to find derivative of the loss function with respect to weights2 and weights1
        d_weights2 = np.dot(self.layer1.T, (2 * (self.y - self.output) * sigmoid_derivative(self.output)))
        #print("d_weights2 is " + str(d_weights2.shape))
        #d_weights1 = np.dot(np.squeeze(np.asarray(self.train_test.T)), (np.dot(np.squeeze(np.asarray(2 * (self.data_test - self.output) * sigmoid_derivative(self.output))), np.squeeze(np.asarray(self.weights2.T) * sigmoid_derivative(self.layer1)))))
        d_weights1 = np.dot(self.stdize.T, (np.dot(2 * (self.y - self.output) * sigmoid_derivative(self.output), self.weights2.T) * sigmoid_derivative(self.layer1))) #original (broken for my case)

        #print("d_weights1 is " + str(d_weights1.shape))
        # update the weights with the derivative (slope) of the loss function
        self.weights1 += d_weights1
        self.weights2 += d_weights2
        #print("self.weights1 is " + str(self.weights1.shape))

    # The neural network thinks.
    def think(self, inputs):
        std_value = (inputs - self.train_mean)/self.train_std
        self.layer1 = sigmoid(np.dot(std_value, self.weights1))
        self.output = sigmoid(np.dot(self.layer1, self.weights2))
        return self.output

    def static_think_2500(self, inputs):
        nn_2500_weights1 = np.load('nn_2500_weights1.npy')
        nn_2500_weights2 = np.load('nn_2500_weights2.npy')
        nn_2500_train_mean = np.load('nn_2500_train_mean.npy')
        nn_2500_train_std = np.load('nn_2500_train_std.npy')
        std_value = (inputs - nn_2500_train_mean) / nn_2500_train_std
        layer1 = sigmoid(np.dot(std_value, nn_2500_weights1))
        output = sigmoid(np.dot(layer1, nn_2500_weights2))
        return output

    def static_think_2000(self, inputs):
        nn_2000_weights1 = np.load('nn_2000_weights1.npy')
        nn_2000_weights2 = np.load('nn_2000_weights2.npy')
        nn_2000_train_mean = np.load('nn_2000_train_mean.npy')
        nn_2000_train_std = np.load('nn_2000_train_std.npy')
        std_value = (inputs - nn_2000_train_mean) / nn_2000_train_std
        layer1 = sigmoid(np.dot(std_value, nn_2000_weights1))
        output = sigmoid(np.dot(layer1, nn_2000_weights2))
        return output

    def static_think_1500(self, inputs):
        nn_1500_weights1 = np.load('nn_1500_weights1.npy')
        nn_1500_weights2 = np.load('nn_1500_weights2.npy')
        nn_1500_train_mean = np.load('nn_1500_train_mean.npy')
        nn_1500_train_std = np.load('nn_1500_train_std.npy')
        std_value = (inputs - nn_1500_train_mean) / nn_1500_train_std
        layer1 = sigmoid(np.dot(std_value, nn_1500_weights1))
        output = sigmoid(np.dot(layer1, nn_1500_weights2))
        return output

    def static_think_1000(self, inputs):
        nn_1000_weights1 = np.load('nn_1000_weights1.npy')
        nn_1000_weights2 = np.load('nn_1000_weights2.npy')
        nn_1000_train_mean = np.load('nn_1000_train_mean.npy')
        nn_1000_train_std = np.load('nn_1000_train_std.npy')
        std_value = (inputs - nn_1000_train_mean) / nn_1000_train_std
        layer1 = sigmoid(np.dot(std_value, nn_1000_weights1))
        output = sigmoid(np.dot(layer1, nn_1000_weights2))
        return output


class Traits:
    """
    Have to remember to include a trait that brings open, close, high, low together.
    """
    def __init__(self, df, df_col):
        self.df = df
        self.df_col = df_col
        self.close_values = np.array(list(df["Close"].tail(120)), dtype=np.float64)


    def day_gradient(self, start, remove_days=0):
        if remove_days == 0:
            ys = self.close_values[-start:, ]
        else:
            ys = self.close_values[-start:, ]
            ys = ys[:start-remove_days, ]
        x = list(range(0, start-remove_days))
        xs = np.array(x, dtype=np.float64)
        print(ys)
        print(xs)
        m = round((((mean(xs)*mean(ys)) - mean(xs*ys)) /
             ((mean(xs)**2) - mean(xs**2)))*100, 5)
        print(m)
        return m, ys

    def sos_error(self, data_points):
        ys = data_points
        mean_ys = mean(ys)
        sum = 0
        for i in range(0,len(ys)):
            err = (ys[i] - mean_ys)**2
            sum += err
        sum = round(sum, 5)
        print(sum)
        return sum

    def previous_close_price(self):
        pcp = float(self.close_values[len(self.close_values) - 1])
        print(pcp)
        return pcp

    def recent_price(self, days):
        rcp = float(self.close_values[len(self.close_values) - 1 - days])
        print(rcp)
        return rcp

def beta_candlestick_AI(df):
    nn_dummy = NeuralNetwork(np.ones([29, 1], dtype=int), np.ones([29, 1], dtype=int))
    true_close_prices = list(df["Close"].tail(30))
    normalized_true_close_prices = []
    for i in range(0, len(true_close_prices)):
        normalized_true_close_prices.append(float(float(true_close_prices[i]) / nn_dummy.z))
    false_nn_2500_prices = []
    false_nn_2000_prices = []
    false_nn_1500_prices = []
    false_nn_1000_prices = []
    close_trait = Traits(df, "Close")  ############################## Needs to happen inside the for loop

    for i in range(0, len(true_close_prices)):
        ### Close
        m30, d30 = close_trait.day_gradient(60, 30)
        m7, d7 = close_trait.day_gradient(37, 30)
        m60_30, d60_30 = close_trait.day_gradient(90, 60)
        m14_7, d14_7 = close_trait.day_gradient(44, 37)
        m21_14, d21_14 = close_trait.day_gradient(51, 44)
        m28_21, d28_21 = close_trait.day_gradient(68, 51)
        sumd30 = close_trait.sos_error(d30)
        sumd7 = close_trait.sos_error(d7)
        sumd60_30 = close_trait.sos_error(d60_30)
        sumd14_7 = close_trait.sos_error(d14_7)
        sumd21_14 = close_trait.sos_error(d21_14)
        sumd28_21 = close_trait.sos_error(d28_21)
        pcp = close_trait.previous_close_price()
        rcp_2c = close_trait.recent_price(2)
        rcp_3c = close_trait.recent_price(3)
        rcp_4c = close_trait.recent_price(4)
        rcp_7c = close_trait.recent_price(7)
        rcp_14 = close_trait.recent_price(14)
        rcp_17 = close_trait.recent_price(17)
        rcp_21 = close_trait.recent_price(21)
        rcp_41 = close_trait.recent_price(41)
        rcp_61 = close_trait.recent_price(61)
        rcp_81 = close_trait.recent_price(81)
        X_close = [m30, sumd30, m7, sumd7, m60_30, sumd60_30, m14_7, sumd14_7, m21_14, sumd21_14, m28_21,
                   sumd28_21, pcp, rcp_2c, rcp_3c, rcp_4c, rcp_7c,
                   rcp_14, rcp_17, rcp_21, rcp_41, rcp_61, rcp_81]
        nn_2500_output = nn_dummy.static_think_2500(X_close)
        nn_2000_output = nn_dummy.static_think_2000(X_close)
        nn_1500_output = nn_dummy.static_think_1500(X_close)
        nn_1000_output = nn_dummy.static_think_1000(X_close)
        false_nn_2500_prices.append(nn_2500_output[0])
        false_nn_2000_prices.append(nn_2000_output[0])
        false_nn_1500_prices.append(nn_1500_output[0])
        false_nn_1000_prices.append(nn_1000_output[0])
        ## for close_traits
        # remove last day
        close_trait.close_values = close_trait.close_values[1:]
        # add newday
        close_trait.close_values = np.append(close_trait.close_values, nn_dummy.denormalize_data(nn_2500_output))

    ai_prices_nn_2500 = [nn_dummy.denormalize_data(i) for i in false_nn_2500_prices]
    ai_prices_nn_2000 = [nn_dummy.denormalize_data(i) for i in false_nn_2000_prices]
    ai_prices_nn_1500 = [nn_dummy.denormalize_data(i) for i in false_nn_1500_prices]
    ai_prices_nn_1000 = [nn_dummy.denormalize_data(i) for i in false_nn_1000_prices]  # perhaps has to be denormalize by own neural network
    low_list = []
    high_list = []
    open_list = []
    close_list = []
    low_list.append( min([ai_prices_nn_2500[0], ai_prices_nn_2000[0], ai_prices_nn_1500[0], ai_prices_nn_1000[0]]))
    high_list.append(max([ai_prices_nn_2500[0], ai_prices_nn_2000[0], ai_prices_nn_1500[0], ai_prices_nn_1000[0]]))
    close_list.append(ai_prices_nn_2000[0])
    open_list.append(ai_prices_nn_1500[0])
    #Arrange estimates into correct categories
    for i in range(1, len(ai_prices_nn_2500)):
        low = min([ai_prices_nn_2500[i], ai_prices_nn_2000[i], ai_prices_nn_1500[i], ai_prices_nn_1000[i]])
        high = max([ai_prices_nn_2500[i], ai_prices_nn_2000[i], ai_prices_nn_1500[i], ai_prices_nn_1000[i]])
        p2h = second_largest([ai_prices_nn_2500[i], ai_prices_nn_2000[i], ai_prices_nn_1500[i], ai_prices_nn_1000[i]]) #possible 2nd highest
        p2l = second_smallest([ai_prices_nn_2500[i], ai_prices_nn_2000[i], ai_prices_nn_1500[i], ai_prices_nn_1000[i]]) #possible 2nd lowest
        low_list.append(low)
        high_list.append(high)
        if p2h < close_list[i-1]:
            close_list.append(ai_prices_nn_2000[i])
            open_list.append(ai_prices_nn_1500[i])
        else:
            close_list.append(ai_prices_nn_1500[i])
            open_list.append(ai_prices_nn_2000[i])
    return close_list, high_list, low_list, open_list

def second_largest(numbers):
    count = 0
    m1 = m2 = float('-inf')
    for x in numbers:
        count += 1
        if x > m2:
            if x >= m1:
                m1, m2 = x, m1
            else:
                m2 = x
    return m2 if count >= 2 else None


def second_smallest(numbers):
    count = 0
    ms = m2 = float('-inf')
    for x in numbers:
        count += 1
        if x < m2:
            if x <= ms:
                ms, m2 = x, ms
            else:
                m2 = x
    return m2 if count >= 2 else None

def AI(days,df):
    df = df.dropna()
    use_len = df.shape[0]-1
    df = df[[ 'Close', 'Open', 'High', 'Low', 'Volume']].tail(use_len)
    last_price = df['Close'].iloc[-1]
    forecast_out = int(days) # predicting 30 days into future
    df['Prediction'] = df[['Close']].shift(-forecast_out) #  label column with data shifted 30 units
    X = np.array(df.drop(['Prediction'], 1))
    X = preprocessing.scale(X)
    X_forecast = X[-forecast_out:] # set X_forecast equal to last 30
    X = X[:-forecast_out]
    y = np.array(df['Prediction']) # set to adj close
    y = y[:-forecast_out] # removing the last 30 days that are 'NaN'
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.2)
    clf = Ridge(alpha=0)
    clf.fit(X_train, y_train)
    forecast_prediction = clf.predict(X_forecast)
    list_pred = list(forecast_prediction)
    return list_pred, last_price


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data)) ###################################################################

        #create cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)",
        (name, email, username, password))

        #commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered and can log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get form fields
        username = request.form['username']
        password_canidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #Compare passwords.
            if sha256_crypt.verify(password_canidate, password):
                app.logger.info('PASSWORD MATCHED')
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in.', 'success')
                return redirect(url_for('index'))
            else:
                app.logger.info('WRONG PASSWORD')
            flash('Incorrect Password.', 'danger')
            #Close current session
            cur.close()
        else:
            app.logger.info('NO USER')
            flash('Unknown Username', 'danger')
    return render_template('login.html')

#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

#user home page
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    # Get articles
    result = cur.execute("SELECT * FROM articles")
    # Get all articles
    articles = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        flash('No Articles Found.', 'danger')
        return render_template('dashboard.html')
    # CLose connection

#user home page
@app.route('/scout')
@is_logged_in
def scout():
    cur = mysql.connection.cursor()
    # Get articles
    result = cur.execute("SELECT * FROM watchlist where User = '"+session['username']+"'")
    # Get all articles
    watchlist = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    for i in watchlist:
        loop_ticker = i["Ticker"]
        latest_data = cur.execute("SELECT * FROM " + loop_ticker + " ORDER by Date DESC LIMIT 1" )
        latest_data = cur.fetchone()
        #print(latest_data['Close'])
        i["Live_Close"] = latest_data['Close']
        i['Pct_Chg'] = round((i["Live_Close"]- i['Close'])/i['Close']*100, 2)
    mysql.connection.commit()
    cur.close()

    if result > 0:
        return render_template('scout.html', watchlist=watchlist)
    else:
        flash('Nothing in Watchlist', 'danger')
        return render_template('scout.html')
    # CLose connection




@app.route('/add_scout', methods=['GET', 'POST'])
@is_logged_in
def add_scout():
    """Only need the ticker name, can get the rest from sql and session."""
    print("into scout")
    if request.method == 'POST':
        print("post recognised")

        ticker = request.form.get('add')
        ticker = ticker.lower()
        print('ticker is ' + str(ticker))
        #create Cursor
        cur = mysql.connection.cursor()

        #Execute
        #result = cur.execute("SELECT * FROM " + ticker.lower())
        other_result = cur.execute("SELECT * FROM "+ ticker + " ORDER BY Date DESC LIMIT 1")
        all_result = cur.fetchall()
        df = pd.DataFrame(list(all_result), columns=["Date", "Open", "Close", "High", "Low", "Adj_Close", "Volume"])

        # prevent duplicate added to watchlist
        watchlist_result = cur.execute("SELECT * FROM watchlist")
        all_result2 = cur.fetchall()
        df2 = pd.DataFrame(list(all_result2), columns=["User","Ticker"])

        duplicate_count = False
        for i in range(len(df2)):
            if df2["User"].iloc[i] == session['username'] and df2["Ticker"].iloc[i] == ticker:
                duplicate_count = True
                break
        if duplicate_count:
            flash('Already in scout', 'danger')
        else:
            cur.execute(
                "INSERT INTO watchlist(Ticker, Watchlist_title, User, Open, High, Low, Close, Adj_Close, Volume) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (ticker, 1, session['username'], df['Open'].iloc[0], df['High'].iloc[0], df['Low'].iloc[0], df['Close'].iloc[0], df['Adj_Close'].iloc[0], df['Volume'].iloc[0]))
            #commit to db
            mysql.connection.commit()

            #close connection
            cur.close()

            flash('Added to scout', 'success')


    return render_template('index.html')

#article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data

        #create Cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    #Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    #get form
    form = ArticleForm(request.form)

    #populate article form fields (title & body)
    form.title.data = article['title']
    form.body.data = article['body']
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        #create Cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)

#Delete article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # create cursor
    cur = mysql.connection.cursor()

    #execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    #Commit to db
    mysql.connection.commit()

    #Close connection
    cur.close()
    flash('Article deleted.', 'success')

    return redirect(url_for('dashboard'))

#Delete row
@app.route('/delete_row/<string:id>', methods=['POST'])
@is_logged_in
def delete_row(id):
    # create cursor
    cur = mysql.connection.cursor()

    #execute
    cur.execute("DELETE FROM watchlist WHERE id = %s", [id])

    #Commit to db
    mysql.connection.commit()

    #Close connection
    cur.close()
    flash('Share removed.', 'success')

    return redirect(url_for('scout'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')

if __name__ == '__main__':

    app.secret_key = 'my_pickle'
    app.run()


