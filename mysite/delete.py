def ticker_list():
    with open('tickers.txt') as f:
        mlist = []
        for line in f:
            try:
                line = line.replace('\r', '').replace('\n', '')
                line = line[:3]
                mlist.append(line)
                line = line.lower()
                mlist.append(line)
                print("Creating " + line)
            except:
                pass
        print(mlist)

ticker_list()