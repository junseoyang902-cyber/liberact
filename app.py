import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="연극 동아리 활동 조회",
    page_icon="🎭",
    layout="centered"
)

# 제목
st.title("🎭 동아리 공동 활동 조회")
st.caption("두 명을 선택하면 함께 참여한 공연을 확인할 수 있습니다.")

st.divider()

# 상태 저장
if "df" not in st.session_state:
    st.session_state.df = None

# 🔥 데이터 없을 때 안내
if st.session_state.df is None:
    st.info("👇 먼저 아래에서 엑셀 파일을 업로드해주세요!")

# ---------------------------
# 📌 데이터가 있을 때만 기능 활성화
# ---------------------------
if st.session_state.df is not None:
    df = st.session_state.df

    st.subheader("👥 인물 선택")

    col1, col2 = st.columns(2)

    with col1:
        person1 = st.selectbox("첫 번째 사람", df['부원명'].unique())

    with col2:
        person2 = st.selectbox("두 번째 사람", df['부원명'].unique())

    st.write("")

    # 버튼 중앙 정렬
    col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
    with col_btn2:
        search = st.button("🔍 공동 활동 찾기", use_container_width=True, key="search_btn")

    st.divider()

    # 🔍 결과 출력
    if search:
        df1 = df[df['부원명'] == person1]
        df2 = df[df['부원명'] == person2]

        merged = pd.merge(
            df1,
            df2,
            on=['연도', '공연명'],
            suffixes=('_1', '_2')
        )

        # 🔥 연도 기준 정렬 추가
        merged = merged.sort_values(by='연도')

        if merged.empty:
            st.warning("❌ 함께 참여한 공연이 없습니다.")
        else:
            st.success(f"🎉 {person1} & {person2} 공동 참여 기록")

            for _, row in merged.iterrows():
                role1 = row['역할_1']
                role2 = row['역할_2']

                if role1 == '배우' and pd.notna(row['배역_1']):
                    role1 += f" ({row['배역_1']})"

                if role2 == '배우' and pd.notna(row['배역_2']):
                    role2 += f" ({row['배역_2']})"

                with st.container():
                    st.markdown(f"""
                    ### 📌 {int(row['연도'])}년 - {row['공연명']}
                    **{person1}**: {role1}  
                    **{person2}**: {role2}
                    """)
                    st.divider()

# ---------------------------
# 🤝 협업 분석
# ---------------------------
st.divider()
st.subheader("🤝 협업 분석")

if st.session_state.df is not None:
    df = st.session_state.df

    target = st.selectbox("기준 인물 선택", df['부원명'].unique(), key="target")

    if st.button("분석하기", key="analyze_btn"):
        target_df = df[df['부원명'] == target]

        # ---------------------------
        # 🔥 1️⃣ 전체 협업 TOP 5
        # ---------------------------
        merged_all = pd.merge(
            target_df[['연도', '공연명']],
            df,
            on=['연도', '공연명']
        )

        merged_all = merged_all[merged_all['부원명'] != target]

        # 🔥 정렬 보장
        top_all = merged_all['부원명'].value_counts().sort_values(ascending=False).head(5)

        st.markdown("### 🔥 가장 많이 작업한 사람 TOP 5")

        if top_all.empty:
            st.warning("데이터 없음")
        else:
            for i, (name, cnt) in enumerate(top_all.items(), 1):
                st.markdown(f"**{i}위. {name}** — {cnt}회")

        st.divider()

        # ---------------------------
        # 🎭 2️⃣ 배우끼리 협업 TOP 5
        # ---------------------------

        actor_df = target_df[target_df['역할'] == '배우']

        merged_actor = pd.merge(
            actor_df[['연도', '공연명']],
            df,
            on=['연도', '공연명']
        )

        merged_actor = merged_actor[
            (merged_actor['부원명'] != target) &
            (merged_actor['역할'] == '배우')
        ]

        # 🔥 정렬 보장
        top_actor = merged_actor['부원명'].value_counts().sort_values(ascending=False).head(5)

        st.markdown("### 🎭 가장 호흡을 많이 맞춘 배우 TOP 5")

        if top_actor.empty:
            st.warning("배우 협업 데이터 없음")
        else:
            for i, (name, cnt) in enumerate(top_actor.items(), 1):
                st.markdown(f"**{i}위. {name}** — {cnt}회")

# ---------------------------
# 📂 업로드 영역 (맨 아래)
# ---------------------------
st.subheader("📂 데이터 업로드")

uploaded_file = st.file_uploader(
    "엑셀 파일을 업로드하세요",
    type=["xlsx"]
)

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df['연도'] = df['연도'].astype(int)

    st.session_state.df = df
    st.success("✅ 데이터 업로드 완료!")
    st.info("👆 이제 위에서 인물을 선택하세요.")
