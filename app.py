import streamlit as st
import pandas as pd
import random

st.title("24時間シフト作成アプリ（夜勤固定なし）")

# ---------------------------
# スタッフ人数
# ---------------------------
num_staff = st.number_input("スタッフ人数", min_value=1, max_value=10, value=8, step=1)
staff_names = [f"スタッフ{i+1}" for i in range(num_staff)]
hours = [f"{h}:00" for h in range(0,24)]
df = pd.DataFrame(0, index=staff_names, columns=hours)

# ---------------------------
# 時間ごとの必要人数
# ---------------------------
st.subheader("時間ごとの必要人数")
required = {}
cols = st.columns(24)
for idx, h in enumerate(hours):
    required[h] = cols[idx].number_input(h, min_value=0, max_value=num_staff, value=3, key=f"req_{h}")

# ---------------------------
# 勤務希望チェック
# ---------------------------
st.subheader("勤務希望チェック")
for staff in staff_names:
    st.write(staff)
    row_cols = st.columns(24)
    for idx, h in enumerate(hours):
        checked = row_cols[idx].checkbox("", key=f"{staff}_{h}")
        df.loc[staff, h] = 1 if checked else 0

# ---------------------------
# 休憩時間指定
# ---------------------------
st.subheader("休憩時間指定（任意）")
breaks = {}
for staff in staff_names:
    st.write(staff)
    start = st.number_input(f"{staff} 休憩開始時刻", min_value=0, max_value=23, value=12, key=f"break_start_{staff}")
    length = st.number_input(f"{staff} 休憩時間（時間）", min_value=0, max_value=4, value=1, key=f"break_length_{staff}")
    breaks[staff] = (start, length)

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

    # 指定休憩時間を反映
    for staff, (start, length) in breaks.items():
        for i in range(length):
            hour = (start + i) % 24
            schedule.loc[staff, f"{hour}:00"] = 0

    # 中抜け休憩長め優先
    if long_break:
        for staff in staff_names:
            filled = [h for h in hours if schedule.loc[staff, h]==1]
            if len(filled) > 4:
                mid = len(filled)//2
                schedule.loc[staff, filled[mid]] = 0

    # ---------------------------
    # 自動人数調整
    # ---------------------------
    for h in hours:
        current_count = schedule[h].sum()
        needed = required[h]
        if current_count < needed:
            # 自動割り当て可能スタッフ
            candidates = [s for s in staff_names if schedule.loc[s, h]==0]
            random.shuffle(candidates)
            for s in candidates:
                if current_count >= needed:
                    break
                schedule.loc[s, h] = 1
                current_count +=1
        elif current_count > needed:
            # 多すぎる場合は任意スタッフから減らす
            candidates = [s for s in staff_names if schedule.loc[s, h]==1]
            random.shuffle(candidates)
            for s in candidates:
                if current_count <= needed:
                    break
                schedule.loc[s, h] = 0
                current_count -=1

    st.subheader("自動割り当て結果")
    st.dataframe(schedule)
