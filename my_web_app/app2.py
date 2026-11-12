import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ==================== 設定 ====================
SPREADSHEET_ID = "1cgP0Uiu2AL3pmOjsRW5p2f0t-blCo2TjpYwWEKO82z0"
MENU_IMAGE = "123.jpg"  # 請換成實際的圖片路徑或網址
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
COLUMNS = ["姓名", "品項", "甜度", "冰塊"]  # 需與試算表第一列標題一致
SWEETNESS_OPTIONS = ["正常甜(10分甜)", "少糖(7分甜)", "半糖(5分甜)", "微糖(3分甜)", "無糖"]
ICE_OPTIONS = ["正常冰", "少冰", "微冰", "去冰", "熱"]


# ==================== 連線（快取，避免重複認證） ====================
@st.cache_resource
def get_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], SCOPE
    )
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID).sheet1


@st.cache_data(ttl=30)
def load_data():
    return pd.DataFrame(get_sheet().get_all_records(expected_headers=COLUMNS))


# ==================== 介面 ====================
st.title("飲料統計測試")

# 菜單區
@st.dialog("飲料菜單", width="large")
def show_menu():
    st.image(MENU_IMAGE, use_container_width=True)

st.subheader("📋 飲料菜單")
st.image(MENU_IMAGE, width=400)
if st.button("🔍 查看菜單大圖"):
    show_menu()

# 表單區
with st.form("input_form", clear_on_submit=True):
    st.write("請填寫以下資訊：")
    user_name = st.text_input("姓名")
    user_items = st.text_input("品項")
    user_sweetness = st.selectbox("甜度", SWEETNESS_OPTIONS)
    user_icecubes = st.selectbox("冰塊", ICE_OPTIONS)
    submitted = st.form_submit_button("送出資料")

if submitted:
    user_name = user_name.strip()
    if not user_name:
        st.warning("姓名不能空白喔！")
    elif not user_items.strip():
        st.warning("品項不能空白喔！")
    else:
        try:
            sheet = get_sheet()
            new_row = [user_name, user_items.strip(), user_sweetness, user_icecubes]

            matches = sheet.findall(user_name, in_column=1)
            cell = matches[0] if matches else None


            if cell:
                sheet.update(f"A{cell.row}:D{cell.row}", [new_row])
                st.success(f"{user_name} 的資料已覆蓋更新！")
            else:
                sheet.append_row(new_row)
                st.success(f"感謝 {user_name}，資料已成功存入！")

            load_data.clear()  # 寫入後清除快取，確保顯示最新資料
        except Exception as e:
            st.error(f"寫入失敗：{e}")

# 資料顯示區
st.divider()
st.subheader("目前的資料庫內容")

try:
    df = load_data()
except Exception as e:
    st.error(f"讀取資料失敗：{e}")
    st.write("請確認試算表 ID 正確，並已將服務帳號的 client_email 加入共用名單。")
    st.stop()

st.dataframe(df, use_container_width=True)

if not df.empty:
    df_count = df.assign(杯數=1)
    summary_df = df_count.groupby(["品項", "甜度", "冰塊"], as_index=False)["杯數"].sum()

    st.subheader("📊 飲料統計結果")
    st.dataframe(summary_df, use_container_width=True)
else:
    st.write("目前尚無資料。")
