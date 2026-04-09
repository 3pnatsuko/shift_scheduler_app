import streamlit as st
import pandas as pd
import random

st.title("24時間シフト作成アプリ（iPhone向け横スクロール）")

# ---------------------------
# スタッフ人数
# ---------------------------
num_staff = st.number_input("スタッフ人数", min_value=1, max_value=10, value=6, step=1)
staff_names = [f"スタッフ{i+1}" for i in range(num_staff)]
hours = [f"{h}:00" for h in range(0,24)]

# ---------------------------
# 必要人数入力（横スクロール対応）
# ---------------------------
st.subheader("時間ごとの必要人数")
required = {}
st.write("横にスクロールして入力してください")
req_cols = st.container()
with req_cols:
    scroll_cols = st.columns(24)
    for idx, h in enumerate(hours):
        required[h] = scroll_cols[idx].number_input(h, min_value=0, max_value=num_staff, value=3, key=f"req_{h}")

# ---------------------------
# 勤務希望と休憩希望（横スクロール）
# ---------------------------
st.subheader("勤務希望と休憩希望")
work_df = pd.DataFrame(0, index=staff_names, columns=hours)
break_df = pd.DataFrame(0, index=staff_names, columns=hours)

for staff in staff_names:
    st.write(f"--- {staff} ---")
    st.write("勤務希望")
    work_cols = st.container()
    with work_cols:
        row_cols = st.columns(24)
        for idx, h in enumerate(hours):
            checked = row_cols[idx].checkbox("", key=f"work_{staff}_{h}")
            work_df.loc[staff, h] = 1 if checked else 0

    st.write("休憩希望")
    break_cols = st.container()
    with break_cols:
        row_cols = st.columns(24)
        for idx, h in enumerate(hours):
            checked = row_cols[idx].checkbox("", key=f"break_{staff}_{h}")
            break_df.loc[staff, h] = 1 if checked else 0

# ---------------------------
# 中抜け休憩長め優先
# ---------------------------
long_break = st.checkbox("中抜け休憩長め優先")

# ---------------------------
# 実行ボタン
# ---------------------------
if st.button("実行"):
    st.write("自動割り当て中…")
    schedule = work_df.copy()

    # 休憩希望を反映
    for staff in staff_names:
        for h in hours:
            if break_df.loc[staff, h]==1:
                schedule.loc[staff, h]=0

    # 中抜け休憩長め優先
    if long_break:
        for staff in staff_names:
            filled = [h for h in hours if schedule.loc[staff, h]==1]
            if len(filled) > 4:
                mid = len(filled)//2
                schedule.loc[staff, filled[mid]] = 0

    # 必要人数に合わせて自動調整
    for h in hours:
        current_count = schedule[h].sum()
        needed = required[h]

        # 足りない場合
        if current_count < needed:
            candidates = [s for s in staff_names if schedule.loc[s, h]==0]
            random.shuffle(candidates)
            for s in candidates:
                if current_count >= needed:
                    break
                schedule.loc[s, h] = 1
                current_count += 1

        # 多い場合
        elif current_count > needed:
            candidates = [s for s in staff_names if schedule.loc[s, h]==1]
            random.shuffle(candidates)
            for s in candidates:
                if current_count <= needed:
                    break
                schedule.loc[s, h] = 0
                current_count -= 1

    st.subheader("自動割り当て結果")
    st.dataframe(schedule)
