import streamlit as st
import pandas as pd

st.set_page_config(page_title="리액위키", page_icon="🎭")

st.title("🎭 리액위키")
st.caption("모든 데이터의 출처는 [리버액트 역대 공연 연혁](https://slowdemoc.notion.site/dd6b64eea8784adebb3363d6db65d591?source=copy_link) 페이지입니다.")
st.caption("🛠️ made by 양준서")

# ---------------------------
# 📂 공용 데이터 자동 로딩
# ---------------------------
if "df" not in st.session_state:
    try:
        df = pd.read_excel("data.xlsx")
        df['연도'] = df['연도'].astype(int)

        # 🔥 연출진 NaN 방지
        if '연출진' in df.columns:
            df['연출진'] = df['연출진'].fillna('')

        st.session_state.df = df
    except:
        st.error("❌ data.xlsx 파일을 찾을 수 없습니다.")
        st.stop()

df = st.session_state.df

# 🔥 공연용 데이터 (리버액트 n기 제외)
df_show = df[~df['공연명'].str.contains("리버액트", na=False)]

st.divider()

# ---------------------------
# 1️⃣ 무엇이 궁금하신가요?
# ---------------------------
st.subheader("1️⃣ 기능 선택")

col1, col2, col3, col4, col5 = st.columns(5)

if col1.button("📜 부원별 활동 기록"):
    st.session_state.menu = "부원별 활동 기록 보기"

if col2.button("🎬 공연별 참여 인원"):
    st.session_state.menu = "공연별 참여 부원 보기"

if col3.button("🏫 기수별 부원"):
    st.session_state.menu = "기수별 부원 보기"

if col4.button("🤝 어떻게 아는 사이세요?"):
    st.session_state.menu = "둘이 어떻게 아세요"

if col5.button("👑 리액 명예의 전당"):
    st.session_state.menu = "리액 이모저모 기록"

menu = st.session_state.get("menu", "부원별 활동 기록 보기")

st.divider()

# ---------------------------
# 2️⃣ 세부 사항
# ---------------------------
st.subheader("2️⃣ 세부 설정")

names = df['부원명'].unique()
shows = df_show['공연명'].unique()

# ---------------------------
# 기능 1️⃣
# ---------------------------
if menu == "부원별 활동 기록 보기":
    person = st.selectbox("부원 선택", names)

    result = df[df['부원명'] == person].sort_values(by='연도')

    st.subheader(f"📜 {person} 활동 기록")

    for _, row in result.iterrows():
        role = row['역할']
        
        if pd.notna(row['배역']):
            role += f" ({row['배역']})"

        st.markdown(
    f"<b>{row['연도']} - {row['공연명']}</b><br><span style='color:gray'>{role}</span>",
    unsafe_allow_html=True
)

# ---------------------------
# 기능 2️⃣
# ---------------------------
elif menu == "공연별 참여 부원 보기":

    def sort_leader(row):
    role = str(row["역할"])

    if "연출" in role:
        return 0
    elif any(x in role for x in ["연기감독", "연기지도", "연기고문", "연기부연출"]):
        return 1
    elif any(x in role for x in ["미술감독", "미술부연출"]):
        return 2
    elif "기획" in role:
        return 3
    else:
        return 4
    
    # ---------------------------
    # 📌 카테고리 분류
    # ---------------------------
    def classify_show(name):
        if "정기" in name:
            return "정기공연"
        elif "OB" in name:
            return "OB공연"
        elif "워크샵" in name:
            return "워크샵공연"
        elif "새터" in name:
            return "새터공연"
        else:
            return "기타"

    df_show = df_show.copy()
    df_show["카테고리"] = df_show["공연명"].apply(classify_show)

    # ---------------------------
    # 📌 카테고리 선택
    # ---------------------------
    category_order = ["정기공연", "OB공연", "워크샵공연", "새터공연", "기타"]

    available = [c for c in category_order if c in df_show["카테고리"].unique()]

    category = st.selectbox("공연 유형 선택", available)

    # ---------------------------
    # 📌 공연 선택 (최신순)
    # ---------------------------
    filtered = df_show[df_show["카테고리"] == category]

    shows_sorted = (
        filtered.sort_values(by="연도", ascending=False)["공연명"].unique()
    )

    show = st.selectbox("공연 선택", shows_sorted)

    result = filtered[filtered["공연명"] == show]

    st.subheader(f"🎬 {show} 참여 인원")

    # ---------------------------
    # 📌 역할 포맷
    # ---------------------------
    def format_role(row):
        role = str(row["역할"])

        if (
            ("배우" in role) or ("단역" in role)
        ) and pd.notna(row.get("배역")):
            role += f" ({row['배역']})"

        return role.replace(",", " / ")

    # ---------------------------
    # 🎯 1️⃣ 상단 그룹 (연출진 or 연출)
    # ---------------------------
    if category in ["워크샵공연", "새터공연"]:
        top_group = result[result["역할"].str.contains("연출", na=False)]
        top_title = "### ⭐ 연출"
    else:
        top_group = result[result["연출진"] == "O"]
        top_title = "### ⭐ 연출진"

    # ---------------------------
    # 🎯 2️⃣ 참여 부원 (겸직 허용)
    # ---------------------------
    others = result[
        (~result.index.isin(top_group.index)) |
        (result["역할"].str.contains(",", na=False))
    ]

    # ---------------------------
    # 📌 출력
    # ---------------------------
    if not top_group.empty:
        st.markdown(top_title)
        top_group = top_group.copy()
        top_group["정렬"] = top_group.apply(sort_leader, axis=1)
        top_group = top_group.sort_values(by="정렬")
        for _, row in top_group.iterrows():
            role = format_role(row)
            st.write(f"{row['부원명']} - {role}")

    st.markdown("### 👥 참여 부원")
    for _, row in others.iterrows():
        role = format_role(row)
        st.write(f"{row['부원명']} - {role}")
# ---------------------------
# 기능 3️⃣
# ---------------------------
elif menu == "기수별 부원 보기":
    import re

    # 🔥 공연명에서 기수 추출
    gens = df['공연명'].dropna().apply(
        lambda x: re.findall(r"리버액트 (\d+)기", str(x))
    )
    gens = sorted(set([int(g[0]) for g in gens if g]))

    gen = st.selectbox(
    "기수 선택",
    gens,
    format_func=lambda x: f"{x}기"
)

    # 🔥 선택된 기수 필터
    result = df[df['공연명'].str.contains(f"리버액트 {gen}기", na=False)]

    st.subheader(f"🏫 리버액트 {gen}기")

    if result.empty:
        st.warning("❌ 해당 기수 데이터 없음")
    else:
        leader = result[result['역할'].isin(['동장', '부동장'])]

        if not leader.empty:
            if gen > 1:
                st.markdown(f"### 👑 동장진 ({gen-1}기)")
            else:
                st.markdown("### 👑 동장진")
            for _, row in leader.iterrows():
                st.write(f"{row['역할']} - {row['부원명']}")

        members = sorted(
    result[~result['역할'].isin(['동장', '부동장'])]['부원명'].unique()
)

        st.markdown("### 👥 부원")

        col1, col2 = st.columns(2)

        for i, name in enumerate(members):
            if i % 2 == 0:
                col1.write(name)
            else:
                col2.write(name)            
# ---------------------------
# 기능 4️⃣
# ---------------------------
elif menu == "둘이 어떻게 아세요":
    col1, col2 = st.columns(2)

    with col1:
        p1 = st.selectbox("첫 번째 사람", names)
    with col2:
        p2 = st.selectbox("두 번째 사람", names)

    if st.button("검색", key="search_btn"):
        df1 = df[df['부원명'] == p1]
        df2 = df[df['부원명'] == p2]

        merged = pd.merge(df1, df2, on=['연도','공연명'], suffixes=('_1','_2'))
        merged = merged.sort_values(by='연도')

        if merged.empty:
            st.warning("❌ 둘이 모르는 사이라네요")
        else:
            for _, row in merged.iterrows():
                r1 = row['역할_1']
                r2 = row['역할_2']

                if pd.notna(row['배역_1']):
                    r1 += f" ({row['배역_1']})"
                if pd.notna(row['배역_2']):
                    r2 += f" ({row['배역_2']})"

                st.markdown(f"""
                ### 📌 {row['연도']} - {row['공연명']}
                {p1}: {r1}  
                {p2}: {r2}
                """)

# ---------------------------
# 기능 5️⃣
# ---------------------------
elif menu == "리액 이모저모 기록":

    st.subheader("📊 통계 분석")

    # 🔥 듀오 TOP (df_show + 중복 제거)
    pair_counts = df_show.groupby(['연도','공연명'])['부원명'].apply(lambda x: list(set(x)))

    pairs = {}
    for lst in pair_counts:
        for i in range(len(lst)):
            for j in range(i+1, len(lst)):
                pair = tuple(sorted([lst[i], lst[j]]))
                pairs[pair] = pairs.get(pair,0)+1

    pair_top = sorted(pairs.items(), key=lambda x: x[1], reverse=True)[:5]

    st.markdown("### 🤝 듀오 TOP 5")
    for i,(p,cnt) in enumerate(pair_top,1):
        st.write(f"{i}. {p[0]} & {p[1]} - {cnt}회")

    # 🔥 참여 TOP (df_show 기준)
    st.markdown("### 🏆 총 참여 횟수 TOP 5")
    top_all = df_show['부원명'].value_counts().head(5)
    for i,(n,c) in enumerate(top_all.items(),1):
        st.write(f"{i}. {n} - {c}회")

    # 🔥 배우 TOP (df_show 기준)
    st.markdown("### 🎭 배우 횟수 TOP 5")
    actors = df[df['역할'].str.contains('배우', na=False)]['부원명'].value_counts().head(5)
    for i,(n,c) in enumerate(actors.items(),1):
        st.write(f"{i}. {n} - {c}회")

    st.markdown("### ⭐ 연출진 기록 TOP 5")

    leaders = df[df['연출진'] == 'O']['부원명'].value_counts().head(5)

    for i, (name, count) in enumerate(leaders.items(), 1):
        st.write(f"{i}. {name} - {count}회")
