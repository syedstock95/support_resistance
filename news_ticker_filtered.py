
import streamlit as st
import pandas as pd
import requests
import feedparser
from datetime import datetime
import re
from io import BytesIO
import xlsxwriter
import os

# 💡 Config
FMP_API_KEY = "cn2AZpCgLd44PYFPCHVkmqZouGukDFXL"
TODAY = datetime.now().strftime("%Y-%m-%d")
NOW_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
SAVE_PATH = f"D:/OneDrive/Documents/shares/Pscripts/Python/News/ticker_filtered_news_{NOW_TIMESTAMP}.xlsx"

# 🚪 Exit Button at Top
if st.button("❌ Exit App", key="exit_top"):
    os._exit(0)

# 🎨 Inject Custom CSS (Headers + Font Sizes)
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-size: 20px !important;
        color: #333333;
        font-weight: normal;
    }
    .stDataFrame thead tr th {
        font-size: 22px !important;
        font-weight: bold !important;
        color: #0047AB !important;
        background-color: #f5f5f5;
    }
    .stDataFrame tbody tr td {
        font-size: 20px !important;
        font-weight: 500;
        color: #111111;
    }
    </style>
""", unsafe_allow_html=True)

# 🎯 Ticker Extraction
def extract_tickers(text):
    return list(set(re.findall(r'\b[A-Z]{2,5}\b', text)))

# 📥 Yahoo RSS
def fetch_yahoo_news():
    feed = feedparser.parse("https://finance.yahoo.com/news/rssindex")
    results = []
    for entry in feed.entries:
        title = entry.title
        date = datetime(*entry.published_parsed[:6])
        if date.strftime("%Y-%m-%d") == TODAY:
            tickers = extract_tickers(title)
            if tickers:
                results.append({
                    "source": "Yahoo",
                    "title": title,
                    "date": date.strftime("%Y-%m-%d %H:%M"),
                    "tickers": ", ".join(tickers)
                })
    return results

# 📥 Google RSS
def fetch_google_news():
    feed = feedparser.parse("https://news.google.com/rss/search?q=stock+market")
    results = []
    for entry in feed.entries:
        title = entry.title
        date = datetime(*entry.published_parsed[:6])
        if date.strftime("%Y-%m-%d") == TODAY:
            tickers = extract_tickers(title)
            if tickers:
                results.append({
                    "source": "Google",
                    "title": title,
                    "date": date.strftime("%Y-%m-%d %H:%M"),
                    "tickers": ", ".join(tickers)
                })
    return results

# 📥 FMP API
def fetch_fmp_news(endpoint_name, label):
    url = f"https://financialmodelingprep.com/api/v4/{endpoint_name}?page=0&apikey={FMP_API_KEY}"
    res = requests.get(url)
    results = []
    if res.ok:
        for item in res.json():
            title = item.get("title", "")
            date_str = item.get("publishedDate", "")
            if TODAY in date_str:
                tickers = extract_tickers(title)
                if tickers:
                    results.append({
                        "source": label,
                        "title": title,
                        "date": date_str,
                        "tickers": ", ".join(tickers)
                    })
    return results

# 🧾 Excel Export
def create_styled_excel_and_save(df):
    writer = pd.ExcelWriter(SAVE_PATH, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='News')

    wb = writer.book
    ws = writer.sheets['News']

    header_fmt = wb.add_format({'bold': True, 'font_color': 'blue', 'font_size': 24})
    for col_num, value in enumerate(df.columns.values):
        ws.write(0, col_num, value, header_fmt)

    content_fmt = wb.add_format({
        'text_wrap': True,
        'font_size': 20,
        'font_color': '#333333',
    })

    for row in range(1, len(df) + 1):
        for col in range(len(df.columns)):
            ws.write(row, col, df.iloc[row - 1, col], content_fmt)

    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).map(len).max(), len(col))
        ws.set_column(i, i, min(max_len + 2, 60))

    writer.close()

# 🖍️ UI Headings
st.markdown("<h1 style='color:#0047AB; font-size:32px;'>📈 <u>Tickers Mentioned in Financial News</u></h1>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#228B22; font-size:26px;'>📰 <u>Filtered News Headlines with Tickers</u></h2>", unsafe_allow_html=True)

# 🔁 Fetch All
news_data = (
    fetch_yahoo_news()
    + fetch_google_news()
    + fetch_fmp_news("general_news", "FMP-General")
    + fetch_fmp_news("stock-news-sentiments-rss-feed", "FMP-Stock")
    + fetch_fmp_news("crypto_news", "FMP-Crypto")
)
df = pd.DataFrame(news_data)

# 🛠 Debug View
if st.checkbox("🛠 Show Debug Mode (All Raw Headlines)", value=False):
    st.dataframe(df)

# ✅ Filtered View
df_filtered = df[df["tickers"].str.strip() != ""] if not df.empty else pd.DataFrame()

if not df_filtered.empty:
    st.dataframe(df_filtered)

    # Save styled Excel
    create_styled_excel_and_save(df_filtered)

    # In-app download
    download = BytesIO()
    with pd.ExcelWriter(download, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='News')
    download.seek(0)

    st.download_button(
        "📘 Download Ticker News (Excel)",
        data=download,
        file_name=f"filtered_ticker_news_{NOW_TIMESTAMP}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.success(f"📁 Excel file saved to: `{SAVE_PATH}`")
else:
    st.warning("⚠️ No ticker-based news found today.")
