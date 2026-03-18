import yfinance as yf
import streamlit as st
import pandas as pd

#stockdata= "SP500.csv"
stockdata = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
readable = pd.read_csv(stockdata)
stockname = readable["Symbol"].tolist()

if "page" not in st.session_state:
    st.session_state.page = "welcome"

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
        time = st.selectbox('Timeframe', ['1 Month', '3 Months', '6 Months', '12 Months', '24 Months'],
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

    timeline = {"1 Month":"1mo", "3 Months": "3mo", "6 Months": "6mo", "12 Months":"12mo", "24 Months":"24mo"}

    history = yf.download(tickers=ticker, period=timeline[time])
    st.header(f"Last {time}")
    if history.empty:
        st.warning("No stock data found.")
    else:
        st.line_chart(history["Close"])

def main():

    print("Begin MAIN PROGRAM")
    with st.sidebar:
        st.sidebar.header("Enter your stock information")
        ticker = st.sidebar.text_input("Enter stock ticker (e.g. AAPL):", "AAPL")
        ticker = ticker.upper()
        invest = st.sidebar.number_input("Enter the Investment Amount")
        start_date = st.sidebar.text_input("Start Date", "2002-06-25")
        end_date = st.sidebar.text_input("End Date", "2025-10-09")

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

    print(price_data)
    print(price_data.head(1))
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
    else:
        percentage = (profit / invest) * 100
        st.subheader("Investment Summary")

        col1,col2,col3 = st.columns(3)
        with col1:
            st.metric(label="Investment Value", value=f"${invest:,.0f}",chart_type="line",border=True)
        with col2:
            col2 =  st.metric(label="Growth Percentage", value=f"+{percentage:.1f}%",chart_type="line",border=True)
        with col3:
            col3 =  st.metric(label="Current Growth Value", value=f"${profit:,.0f}",chart_type="line",border=True)

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
        final = final.values
        #st.write(final.iloc[:, 0])
        st.line_chart(final)

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

