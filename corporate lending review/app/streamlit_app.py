import streamlit as st

# ✅ 페이지 설정은 반드시 최상단에서 먼저 호출!
st.set_page_config(page_title="기업여신 자동심사 시스템", layout="centered")

import pandas as pd
import pickle
import sys
import os

# 경로 설정 및 유틸 모듈 import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
from preprocessing import preprocess_input
from decision_rule import explain_decision


# 모델 로드
@st.cache_resource
def load_model():
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model", "rf_credit_model.pkl"))
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

model = load_model()

# Streamlit 앱 UI
st.title("💼 기업여신 자동심사 시뮬레이터")
st.markdown("기업의 주요 재무 지표를 입력하면 여신 승인 여부를 예측합니다.")

# 입력 받기
유동비율 = st.slider("유동비율 (%)", 0, 300, 100)
부채비율 = st.slider("부채비율 (%)", 0, 500, 250)
매출액 = st.number_input("매출액 (억원)", min_value=0.0, step=1.0)
영업이익률 = st.number_input("영업이익률 (%)", step=0.1)
ROA = st.number_input("ROA (%)", step=0.1)

# 예측 실행
if st.button("심사하기"):
    input_df = preprocess_input(유동비율, 부채비율, 매출액, 영업이익률, ROA)
    prediction = model.predict(input_df)[0]
    proba = model.predict_proba(input_df)[0][prediction]

    if prediction == 1:
        st.success(f"✅ 승인되었습니다. (신뢰도: {proba:.2%})")
    else:
        st.error(f"❌ 거절되었습니다. (신뢰도: {proba:.2%})")

    st.markdown("### 📌 주요 판단 근거")
    reasons = explain_decision(ROA, 부채비율)
    for r in reasons:
        st.write("-", r)
