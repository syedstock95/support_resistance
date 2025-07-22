import streamlit as st
import pandas as pd
import os
from bs4 import BeautifulSoup

# Streamlit page settings
st.set_page_config(page_title="📈 Market & Crypto News Summary", layout="wide")
st.markdown("## 📈 Market & Crypto News Summary")

# Exit app button
if st.button("❌ Exit App"):
    os._exit(0)

# ✅ Portable working directory setup
NEWS_DIR = "news" if os.path.isdir("news") else "."

# Try to list .xlsx files in directory
xlsx_files = sorted([f for f in os.listdir(NEWS_DIR) if f.endswith(".xlsx")], reverse=True)

uploaded_file = st.file_uploader("📤 Or upload a news summary Excel file:", type=["xlsx"])

if not xlsx_files and not uploaded_file:
    st.warning("⚠️ No local news files found. Please upload an .xlsx file.")
    st.stop()

# Select a file to load
if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success(f"Loaded uploaded file ✅")
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        st.stop()
else:
    selected_file = st.selectbox("📁 Select a news summary file:", xlsx_files)
    file_path = os.path.join(NEWS_DIR, selected_file)
    try:
        df = pd.read_excel(file_path)
        st.success(f"Loaded {selected_file} ✅")
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

# Search bar
search = st.text_input("🔍 Search news by keyword (title, summary, or link):")
if search:
    df = df[df.apply(lambda row: search.lower() in str(row['title']).lower() or
                                 search.lower() in str(row['summary']).lower() or
                                 search.lower() in str(row['link']).lower(), axis=1)]

if df.empty:
    st.info("🔎 No matching news found.")
    st.stop()

# Display grouped news
for source, group in df.groupby("source"):
    st.markdown(f"### 📰 <u>{source}</u>", unsafe_allow_html=True)

    for _, row in group.iterrows():
        title = row['title'] or ""
        link = row['link'] or ""
        raw_summary = row['summary'] or ""

        # Strip HTML from summary
        try:
            soup = BeautifulSoup(raw_summary, "html.parser")
            for img in soup.find_all("img"):
                img.decompose()
            summary_text = soup.get_text().strip()
        except:
            summary_text = raw_summary

        # Format HTML blocks
        title_html = f"<div style='font-size:22px; color:#1f77b4; font-weight:bold'>{title}</div>"
        link_html = f"<a href='{link}' target='_blank' style='font-size:20px; font-weight:500'>🔗 Read more</a>"
        summary_html = f"<div style='color:#222; font-size:20px; margin-top:6px'>{summary_text}</div>"
        card_html = (
            "<div style='margin-bottom:28px'>"
            f"{title_html}"
            f"{link_html}"
            f"{summary_html}"
            "</div><hr style='border-top:1px solid #ccc'>"
        )

        st.markdown(card_html, unsafe_allow_html=True)
