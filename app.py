import streamlit as st
import pandas as pd

st.title("シフト自動作成アプリ（iPhone対応）")

# ---------------------------
# スタッフ人数
# ---------------------------
num_staff = st.number_input("スタッフ人数", min_value=1, max_value=10, value=8, step=1)

# ---------------------------
# 時間軸
# ---------------------------
hours = [f"{h}:00" for h in range(5, 24)]  # 5時～23時
staff_names = [f"スタッフ{i+1}" for i in range(num_staff)]
df = pd.DataFrame(0, index=staff_names, columns=hours)

# ---------------------------
# 勤務希望チェックボックス
# ---------------------------
st.subheader("勤務希望をチェックしてください")
for i in df.index:
    for h in df.columns:
        checked = st.checkbox(f"{i} {h}", key=f"{i}_{h}")
        df.loc[i, h] = 1 if checked else 0  # True/False → 1/0

# ---------------------------
# 夜勤・準夜勤固定
# ---------------------------
st.subheader("夜勤・準夜勤")
night_staff = st.multiselect("夜勤スタッフ（22:00-7:00固定）", options=staff_names)
early_staff = st.multiselect("準夜勤スタッフ（17:00-22:00固定）", options=staff_names)

# ---------------------------
# 中抜け休憩長め優先
# ---------------------------
long_break = st.checkbox("中抜け休憩長め優先")

# ---------------------------
# 実行ボタン
# ---------------------------
if st.button("実行"):
    st.write("シフト割り当て中…")
    schedule = df.copy()

    # 夜勤固定
    for staff in night_staff:
        if staff in schedule.index:
            for h in hours:
                hour_int = int(h.split(":")[0])
                if hour_int >= 22 or hour_int < 7:
                    schedule.loc[staff, h] = 1

    # 準夜勤固定
    for staff in early_staff:
        if staff in schedule.index:
            for h in hours:
                hour_int = int(h.split(":")[0])
                if 17 <= hour_int < 22:
                    schedule.loc[staff, h] = 1

    # 自動割り当て（簡易例）
    auto_staff = [s for s in staff_names if s not in night_staff + early_staff]
    for staff in auto_staff:
        count = 0
        for h in hours:
            if schedule.loc[staff, h] == 1:
                count += 1
            else:
                if count > 0 and count < 2:  # 2時間未満禁止
                    schedule.loc[staff, h] = 1
                    count += 1
                else:
                    count = 0

    # 長め中抜け休憩優先
    if long_break:
        for staff in auto_staff:
            filled = [h for h in hours if schedule.loc[staff, h] == 1]
            if len(filled) > 4:
                mid = len(filled)//2
                schedule.loc[staff, filled[mid]] = 0

    st.subheader("自動割り当て結果")
    st.dataframe(schedule)
