import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# 設定權限範圍
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive"]

# 判斷是本地執行還是雲端執行
try:
    # 嘗試讀取本地檔案 (本地開發用)
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
except:
    # 讀取 Streamlit Cloud 的 Secrets (雲端部署用)
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)
sheet = client.open("你的試算表名稱").sheet1

# 接下來是你的網頁內容...
st.title("我的雲端表單")
# ...
