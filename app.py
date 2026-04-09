import streamlit as st
import pandas as pd
import random

st.title("シフト自動作成アプリ（最終完全版）")

# ---------------------------
# スタッフ人数
# ---------------------------
num_staff = st.number_input("スタッフ人数", 1, 10, 6)
staff_names = [f"スタッフ{i+1}" for i in range(num_staff)]
hours = list(range(24))

# ---------------------------
# 勤務時間上限
# ---------------------------
max_hours = st.number_input("1人あたりの最大勤務時間", 1, 24, 8)

# ---------------------------
# 時間ラベル
# ---------------------------
st.subheader("時間")
cols = st.columns(24)
for i, h in enumerate(hours):
    cols[i].write(f"{h}")

# ---------------------------
# 必要人数
# ---------------------------
st.subheader("必要人数")
required = {}
cols = st.columns(24)
for i, h in enumerate(hours):
    required[h] = cols[i].number_input("", 0, num_staff, 3, key=f"req_{h}")

# ---------------------------
# 勤務希望・休憩希望
# ---------------------------
work_df = pd.DataFrame(0, index=staff_names, columns=hours)
break_df = pd.DataFrame(0, index=staff_names, columns=hours)

st.subheader("勤務（上）／休憩（下）")

for staff in staff_names:
    st.write(f"--- {staff} ---")

    cols = st.columns(24)
    for i, h in enumerate(hours):
        work_df.loc[staff, h] = 1 if cols[i].checkbox("", key=f"w_{staff}_{h}") else 0

    cols = st.columns(24)
    for i, h in enumerate(hours):
        break_df.loc[staff, h] = 1 if cols[i].checkbox("", key=f"b_{staff}_{h}") else 0

# ---------------------------
# オプション
# ---------------------------
long_break = st.checkbox("中抜け休憩を優先する")

# ---------------------------
# 実行
# ---------------------------
if st.button("実行"):

    schedule = work_df.copy()

    # ① 休憩反映
    for s in staff_names:
        for h in hours:
            if break_df.loc[s, h] == 1:
                schedule.loc[s, h] = 0

    # ② 中抜け休憩
    if long_break:
        for s in staff_names:
            work_hours = [h for h in hours if schedule.loc[s, h] == 1]
            if len(work_hours) > 4:
                schedule.loc[s, work_hours[len(work_hours)//2]] = 0

    # ③ 人数調整（1回目）
    for h in hours:
        current = schedule[h].sum()
        need = required[h]

        if current < need:
            candidates = [
                s for s in staff_names
                if schedule.loc[s, h] == 0
                and schedule.loc[s].sum() < max_hours
            ]
            random.shuffle(candidates)
            for s in candidates:
                if current >= need:
                    break
                schedule.loc[s, h] = 1
                current += 1

        elif current > need:
            candidates = [s for s in staff_names if schedule.loc[s, h] == 1]
            random.shuffle(candidates)
            for s in candidates:
                if current <= need:
                    break
                schedule.loc[s, h] = 0
                current -= 1

    # ④ 連続勤務ルール
    for s in staff_names:
        start = None
        length = 0

        for h in range(24):
            if schedule.loc[s, h] == 1:
                if start is None:
                    start = h
                    length = 1
                else:
                    length += 1
            else:
                if length == 1:
                    schedule.loc[s, start] = 0
                elif length == 2:
                    if start > 0 and schedule.loc[s].sum() < max_hours:
                        schedule.loc[s, start-1] = 1
                    elif h < 24 and schedule.loc[s].sum() < max_hours:
                        schedule.loc[s, h] = 1
                start = None
                length = 0

        if length == 1:
            schedule.loc[s, start] = 0

    # ⑤ 人数調整（2回目）
    for h in hours:
        current = schedule[h].sum()
        need = required[h]

        if current < need:
            candidates = [
                s for s in staff_names
                if schedule.loc[s, h] == 0
                and schedule.loc[s].sum() < max_hours
            ]
            random.shuffle(candidates)
            for s in candidates:
                if current >= need:
                    break
                schedule.loc[s, h] = 1
                current += 1

        elif current > need:
            candidates = [s for s in staff_names if schedule.loc[s, h] == 1]
            random.shuffle(candidates)
            for s in candidates:
                if current <= need:
                    break
                schedule.loc[s, h] = 0
                current -= 1

    # ⑥ 色付け
    def highlight(val):
        if val == 1:
            return "background-color: #90EE90"
        else:
            return "background-color: #DDDDDD"

    st.subheader("結果")
    st.dataframe(schedule.style.applymap(highlight))
