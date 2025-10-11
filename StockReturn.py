import yfinance as yf
import streamlit as st


header = st.container()
with header:
    st.title('Welcome to my stock analysis app!')

def main():
    print("Begin MAIN PROGRAM")
    st.sidebar.header("Enter your stock information")
    ticker = st.sidebar.text_input("Enter stock ticker (e.g. AAPL):", "AAPL")

    start_date = st.sidebar.text_input("Start Date", "2002-06-25")
    end_date = st.sidebar.text_input("End Date", "2025-10-09")


    price_data = yf.download(tickers=ticker, start=start_date, end=end_date)


    print(price_data)
    original_amount = 10000
    print(price_data.head(1))
    start_price = price_data.head(1)["Close"].values[0][0]
    print(start_price)

    current_price = price_data.tail(1)["Close"].values[0][0]
    shares = original_amount // start_price
    print(shares)
    profit = int(shares * current_price)
    print(format(profit, ","))
    st.write("Your investment of 10,000 dollars is now ", format(profit,","))



main()
