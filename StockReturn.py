import yfinance as yf
import streamlit as st
import pandas as pd
import datetime

#stockdata= "SP500.csv"
stockdata = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
readable = pd.read_csv(stockdata)
stockname = readable["Symbol"].tolist()

if "page" not in st.session_state:
    st.session_state.page = "welcome"

st.set_page_config(layout="wide")

def welcome_screen():
    header = st.container()
    with header:
        st.title('StockPilot')
    st.markdown("""
    <style>

    .stApp {
        background: linear-gradient(45deg,#C9A477,#ECD59F,#FFBD71,#ABD1DC,#7097A8);
        background-size: 400% 400%;
        animation: gradient 10s ease infinite;
    }

    @keyframes gradient {
        0% {background-position:0% 50%;}
        50% {background-position:100% 50%;}
        100% {background-position:0% 50%;}
    }
    
    .center-box{
        text-align:center;
        padding-top:10px;
        
    .subtitle{
        font-size:50px;
        color:white;
        margin-top:20px;
    }
    
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="center-box">
        
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")

    col1, col2, col3 = st.columns([3,3,3])
    with col1:
        if st.button("Shares Calculator"):
            st.session_state.page = "new"
            st.rerun()

    with col2:
        if st.button("Investment Analysis"):
            st.session_state.page = "main"
            st.rerun()

    with col3:
        if st.button("Stock History"):
            st.session_state.page = "graph"
            st.rerun()


def graph():

    st.set_page_config(
        page_title="Stock History",
        page_icon=":chart:",
        layout="wide"
    )

    with st.sidebar:
        st.title("Data Scope")
        ticker = st.multiselect("Stock Tickers", placeholder="Enter Stock Ticker", options=sorted(set(stockname)),default=["AAPL"])
        time = st.selectbox('Timeframe', ['1 Month', '3 Months', '6 Months', '12 Months', '24 Months', '60 Months'],
                            index=3)

        if st.button("back"):
            st.session_state.page = "welcome"
            st.rerun()

    if len(ticker) == 0:
        st.warning("Please select a stock ticker")
        return

    cols = st.columns(2)
    cols[0].metric(label= f"Best Stock {ticker[0]}", value=0,chart_type="line",border=True)
    cols[1].metric(label=f"Worst Stock {ticker[0]}", value=0,chart_type="line",border=True)

    timeline = {"1 Month":"1mo", "3 Months": "3mo", "6 Months": "6mo", "12 Months":"12mo", "24 Months":"24mo", "60 Months":"60mo"}

    history = yf.download(tickers=ticker, period=timeline[time])
    st.header(f"Last {time}")
    if history.empty:
        st.warning("No stock data found.")
    else:
        st.line_chart(history["Close"])

def divreinvestment():
    st.header("Dividend Reinvestment")

    ticker = st.session_state.ticker1
    start = st.session_state.start1
    end = st.session_state.end1
    shares = st.session_state.share
    invest = st.session_state.invest
    stockp = st.session_state.price


    stockticker = yf.Ticker(ticker)
    div = stockticker.dividends
    divTime = div[start:end]


    if div.empty:
        st.info("This company does not provide Dividends.")
    elif divTime.empty:
        st.info("This company did not provide Dividends during this time period.")
    else:
        store = []
        store2 = []
        graph = []
        originalshares = shares
        shares2 = shares
        leftover = 0
        leftover2 = 0


        for date1, price in divTime.items():
            date1 = date1.date()

            closer = date1 + datetime.timedelta(days=2)
            stockcurr = yf.download(tickers=ticker, start=str(date1), end=closer)
            stockpricefull = stockcurr.iloc[-1]
            stockprice = stockcurr["Close"].values[0][0]

            #inital stock price
            initialprice = stockp["Close"].values[0][0]

            totaldiv = shares * price

            sharestobuy = totaldiv//stockprice


            if (totaldiv//stockprice) > 0:
                sharestobuy = totaldiv//stockprice
                #st.write("we can buy", sharestobuy)
                shares = shares + sharestobuy
                leftover = leftover + (totaldiv - (stockprice*sharestobuy))
                #st.write("REMAINDER AFTER REINVESTING: ", leftover)

            totaldiv2 = shares2 * price
            sharestobuy2 = totaldiv2//stockprice
            shares2 = shares2 + sharestobuy2
            leftover2 = leftover2 + (totaldiv2 - (stockprice * sharestobuy2))
            sharesfromremainder = leftover2 // stockprice

            total_value = shares * stockprice #regular dividend reinvestment
            total_value2 = shares2 * stockprice #divident reinvestment + remainder reinvestment

            if sharesfromremainder > 0:
                shares2 = shares2 + sharesfromremainder
                leftover2 = leftover2 - (stockprice * sharesfromremainder)
            totaldiv = f"${totaldiv:,.2f}"
            #stockprice = f"${stockprice:,.2f}"
            store.append({"Date": date1, "Dividend Per Share": f"${price:,.2f}", "Stock Price": f"${stockprice:,.2f}",
                          "Total Dividend Income": totaldiv, "Shares Bought": f"{sharestobuy:,.0f}",
                          "Total Shares": f"{shares:,.0f}", "Remainder After Reinvestment": f"${leftover:,.2f}"})

            store2.append({"Date": date1, "Dividend Per Share": f"${price:,.2f}", "Stock Price": f"${stockprice:,.2f}",
                           "Total Dividend Income": totaldiv, "Shares Bought From Dividend Reinvestment": f"{sharestobuy2:,.0f}",
                           "Shares Bought From Remainder": f"{sharesfromremainder:,.0f}", "Total Shares": f"{shares2:,.0f}",
                           "Remainder After Reinvestment": f"${leftover2:,.2f}"})

            tableinfo2 = pd.DataFrame(store2)
            tableinfo = pd.DataFrame(store)

            graph.append({"Dividend Payment Date": date1,"Total Market Value": f"${total_value:,.0f}"})

        col1, col2, col3= st.columns(3)
        with col1:
            st.subheader("Shares")
            st.metric(label="Initial Shares Owned", value=f"{originalshares:,.0f}")
            st.metric(label="Shares Owned After Dividend & Remainder Reinvestment", value=f"{shares2:,.0f}")
            st.metric(label="Shares Owned After Dividend Reinvestment", value=f"{shares:,.0f}")
        with col2:
            st.subheader("Investment Growth")
            st.metric(label="Initial Investment Value", value=f"${invest:,.0f}")
            st.metric(label="Total Stock Value After Dividend & Remainder Reinvestment", value=f"${total_value2:,.0f}")
            st.metric(label="Total Stock Value After Dividend Reinvestment", value=f"${total_value:,.0f}")
        with col3:
            st.subheader("Stock Prices")
            st.metric(label=f"Stock Price During Investment: {start}", value=f"${initialprice:,.2f} ")
            st.metric(label=f"Stock Price At End Of Timeline: {end}", value=f"${stockprice:,.2f}")

        #tables
        st.subheader("Dividend Reinvestment Summaries")
        with st.expander("Dividend Reinvestment Overview (No Remainder Reinvestment)"):
            st.table(tableinfo)
        with st.expander("Dividend Reinvestment Overview (Remainder Reinvestment Included)"):
            st.table(tableinfo2)

        graphdata = pd.DataFrame(graph)
        graphdata = graphdata.set_index("Dividend Payment Date")

        st.subheader("Shares Performance")
        st.line_chart(graphdata)
        st.subheader("Dividend Payment Intervals")
        st.write(divTime)

    if st.button("Return to Investment Analysis"):
        st.session_state.page = "main"
        st.rerun()

def div():
    st.header("Dividend Data")
    ticker = st.session_state.ticker1
    start = st.session_state.start1
    end = st.session_state.end1
    shares = st.session_state.share
    profit = st.session_state.profit

    stockticker = yf.Ticker(ticker)
    div = stockticker.dividends
    divTime = div[start:end]

    if div.empty:
        st.info("This company does not provide Dividends.")
    elif divTime.empty:
        st.info("This company did not provide Dividends during this time period.")
    else:

        # most recent value dividend
        latest = divTime.iloc[-1]

        latest_AT = div.iloc[-1]
        at_date = div.index[-1]
        at_date = at_date.date()

        totalDiv = divTime.sum()
        gain = shares * totalDiv
        total = profit + gain
        st.subheader(f"Dividends Investment Overview for {ticker}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Timeframe: ", value=f"{start} to {end}", chart_type="line")
        with col2:
            st.metric(label=f"Latest Dividend Payment: {end}", value=f"${latest:,.2f}")
        with col3:
            st.metric(label=f"Current Investment Value:", value=f"${profit:,.2f}")

        col4, col5,col6= st.columns(3)
        with col4:
            st.metric(label="Shares owned", value=f"{shares:.0f}")
        with col5:
            st.metric(label="Total Dividends from investment", value=f"${gain:,.2f}")
        with col6:
            st.metric(label="Total Investment Value including Dividends", value=f"${total:,.2f}")


        st.line_chart(divTime)
        st.write("Raw Data")
        st.write(divTime)

        st.subheader(f"Dividends from All Time Overview for {ticker}")
        c1, c2= st.columns(2)
        with c1:
            st.metric(label="Latest Dividend Payment Date", value=str(at_date))
        with c2:
            st.metric(label="Latest Dividend Per Share", value=f"${latest_AT:,.2f}")

        st.line_chart(div)
        st.write("Raw Data")
        st.write(div)

    if st.button("Return to Investment Analysis"):
        st.session_state.page = "main"
        st.rerun()


def main():

    print("Begin MAIN PROGRAM")
    with st.sidebar:
        st.sidebar.header("Enter your stock information")

        ticker = st.sidebar.text_input("Enter stock ticker (e.g. AAPL):", value=st.session_state.get("savedTicker","AAPL"), key="tickersave")
        ticker = ticker.upper()
        invest = st.sidebar.number_input("Enter the Investment Amount",value=st.session_state.get("savedInvest",1), key="investsave")
        start_date = st.sidebar.text_input("Start Date", value=st.session_state.get("savedStart", "2002-06-25"),key="startsave")
        end_date = st.sidebar.text_input("End Date", value=st.session_state.get("savedEnd","2025-10-09"), key="endsave")


        if st.button("Back"):
            st.session_state.page = "welcome"
            st.rerun()

    if len(start_date) != 10 or start_date[4] != "-" or start_date[7] != "-":
        st.warning("Date must be entered in YYYY-MM-DD format. Please enter a valid date.")
        return

    year = start_date[0:4]
    month = start_date[5:7]
    day = start_date[8:10]

    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        st.warning("Date must contain numbers only. Please enter a valid date.")
        return

    try:
        price_data = yf.download(tickers=ticker, start=start_date, end=end_date)

        if price_data.empty:
            st.warning("Invalid Stock Ticker or no data found. Please try again.")
            return
    except Exception:
        st.warning("Unable to download stock data. Please enter valid stock ticker.")
        return

    start_price = price_data.head(1)["Close"].values[0][0]
    print(start_price)
    current_price = price_data.tail(1)["Close"].values[0][0]
    shares = invest // start_price
    profit = int(shares * current_price)
    invest = int(invest)
    print(format(profit, ","))

    if invest <= 0:
        st.warning("Please enter a valid investment amount.")
        return
    elif invest < start_price:
        st.info("Unable to purchase stock at current market value")
    else:
        increase = profit - invest
        percentage = (increase / invest) * 100
        st.subheader("Investment Summary")

        col1,col2,col3 = st.columns(3)
        with col1:
            st.metric(label="Investment Value", value=f"${invest:,.0f}",chart_type="line",border=True)
        with col2:
            st.metric(label="Growth Percentage", value=f"+{percentage:.1f}%",chart_type="line",border=True)
        with col3:
            st.metric(label="Current Growth Value", value=f"${profit:,.0f}",chart_type="line",border=True)

        one = yf.download(tickers=ticker, period="max")

        if one.empty:
            publicdate = "N/A"
        else:
            publicdate = one.index[0]

        information = yf.Ticker(ticker)
        companyname = ticker
        industry = "N/A"
        country = "N/A"
        market = "N/A"
        website = "N/A"

        try:
            info = information.info

            if info != None:
                companyname = info.get("longName", ticker)
                industry = info.get("sector", "N/A")
                country = info.get("country","N/A")
                market = info.get("marketCap", "N/A")
                website = info.get("website", "N/A")
        except:
            st.warning("Could not load company information at this time.")

        st.subheader("Overview")
        row1, row2 = st.columns([2, 1])
        with row1:
            st.metric(label="Company:", value=companyname)
        with row2:
            st.metric(label="Industry", value=industry)

        with st.expander("More Information"):
            st.write("IPO Date:", publicdate)
            st.write("Country:", country)
            st.write("Market Cap: ", market)
            st.write("Website:", website)

        st.subheader("Stock Growth Since Investment")
        final = price_data["Close"]

        if ticker.endswith(".to".upper()):
            final = final.values.flatten()
            final = pd.Series(final, index=price_data.index)

        st.line_chart(final)

        #Saved values
        st.session_state.savedTicker = ticker
        st.session_state.savedInvest = invest
        st.session_state.savedStart = start_date
        st.session_state.savedEnd = end_date

        #set the linked variables to find dividend of company
        st.session_state.ticker1 = ticker
        st.session_state.start1 = start_date
        st.session_state.end1 = end_date
        st.session_state.share = shares
        st.session_state.profit = profit
        st.session_state.invest = invest
        st.session_state.price = price_data

        if st.button("View Dividend Information"):
            st.session_state.page = "div"
            st.rerun()

        if st.button("View Dividend Reinvestment Information"):
            st.session_state.page = "divreinvestment"
            st.rerun()


def numreturn():
    with st.sidebar:
        st.sidebar.header("Shares Calculator")
        ticker = st.text_input("Enter Stock Ticker (e.g. AAPL)", "AAPL")
        money = st.number_input("How much money would you like to invest?")

        if st.button("back"):
            st.session_state.page = "welcome"
            st.rerun()

    if money <= 0:
        st.warning("Please enter a valid investment amount.")
        return

    if len(ticker) == 0:
        st.warning("Please input a valid stock ticker")
        return

    currentdata = yf.download(tickers=ticker, period="1d")

    if currentdata.empty:
        st.warning("Invalid Stock Ticker or no data found. Please try again.")
        return

    price = currentdata["Close"].values[0][0]

    shares = money//price
    spent = shares*price
    spare = money - spent
    st.subheader("Shares Investment Summary")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Stock Price", f"${price:.2f}", chart_type="line",border=True)
    with col2:
        st.metric("Total shares that can be purchased", int(shares), chart_type="line",border=True)
    with col3:
        st.metric("Investment Remainder", f"${format(round(spare,2), ",")}", chart_type="line",border=True)

    row = st.columns(1)
    st.metric("Value of total shares", f"${format(round(spent,2), ",")}", chart_type="line",border=True)


#Page traversal
if st.session_state.page == "welcome":
    welcome_screen()

if st.session_state.page == "main":
    main()

if st.session_state.page == "new":
    numreturn()

if st.session_state.page == "graph":
    graph()

if st.session_state.page == "div":
    div()

if st.session_state.page == "divreinvestment":
    divreinvestment()



