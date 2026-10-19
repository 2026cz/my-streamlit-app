import os
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. 從 Streamlit Secrets 讀取 JSON 內容
# 假設您在 Secrets 裡設定的 key 是 "gcp_service_account"
creds_dict = st.secrets["gcp_service_account"]

# 2. 設定權限範圍
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# 3. 使用字典進行認證 (不再需要讀取檔案)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# 4. 打開試算表 (請將下方的 ID 換成你自己的)
# 獲取方式：打開你的試算表，網址列中 /d/ 後面到 /edit 前面那串亂碼就是 ID
spreadsheet_id = "1cgP0Uiu2AL3pmOjsRW5p2f0t-blCo2TjpYwWEKO82z0"

try:
    sheet = client.open_by_key(spreadsheet_id).sheet1

    # 測試：讀取第一格資料
    data = sheet.get_all_records()
    st.write("成功連線到試算表！")
    st.write(data)

except Exception as e:
    st.error(f"發生錯誤：{e}")
    st.write("請確認：")
    st.write("1. 試算表 ID 是否正確。")
    st.write("2. 是否已將 credentials.json 內的 client_email 加入試算表的「共用」名單中。")

st.title("飲料統計測試")

# 建立一個表單
with st.form("input_form", clear_on_submit=True):
    st.write("請填寫以下資訊：")

    # 建立輸入欄位
    user_name = st.text_input("姓名")
    user_items = st.text_input("品項",)
    user_Sweetness = st.text_input("甜度")
    user_icecubes = st.text_input("冰塊")

    # 送出按鈕
    submitted = st.form_submit_button("送出資料")

    if submitted:
        if user_name == "":
            st.warning("姓名不能空白喔！")
        else:
            # 將資料寫入 Google Sheets
            # 這裡的順序要對應你試算表的欄位順序
            sheet.append_row([user_name, user_items, user_Sweetness, user_icecubes])
            st.success(f"感謝 {user_name}，資料已成功存入！")

# 顯示目前的資料庫內容
st.divider()
st.subheader("目前的資料庫內容")
data = sheet.get_all_records()
df = pd.DataFrame(data)
st.dataframe(df)