import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="연극 동아리 활동 조회", page_icon="🎭")

st.title("🎭 동아리 공동 활동 조회")
st.write("두 사람을 입력하면 함께 참여한 공연을 보여줍니다.")

# 엑셀 파일 업로드
uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # 연도 정수 처리
    df['연도'] = df['연도'].astype(int)

    # 역할 출력 함수
    def format_role(role, character):
        if role == '배우' or '단역' and pd.notna(character):
            return f"{role} ({character})"
        else:
            return role

    # 사람 선택 (자동완성)
    names = df['부원명'].unique()

    person1 = st.selectbox("첫 번째 사람", names)
    person2 = st.selectbox("두 번째 사람", names)

    if st.button("공동 활동 찾기"):
        df1 = df[df['부원명'] == person1]
        df2 = df[df['부원명'] == person2]

        merged = pd.merge(
            df1,
            df2,
            on=['연도', '공연명'],
            suffixes=('_1', '_2')
        )

        if merged.empty:
            st.error("❌ 같이 참여한 공연이 없습니다.")
        else:
            st.success(f"🎉 {person1} & {person2} 공동 참여 공연")

            for _, row in merged.iterrows():
                role1 = format_role(row['역할_1'], row['배역_1'])
                role2 = format_role(row['역할_2'], row['배역_2'])

                st.markdown(f"""
                ### 📌 {row['연도']}년 - {row['공연명']}
                - **{person1}**: {role1}  
                - **{person2}**: {role2}
                """)
