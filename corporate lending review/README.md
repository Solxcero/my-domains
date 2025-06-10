✅ 프로젝트 제목
기업여신 자동심사 시스템 경량 시뮬레이터 개발

🎯 프로젝트 목표
재무제표 기반으로 기업의 여신 승인/거절 여부를 예측하는 ML 분류 모델 개발

승인 여부와 함께 심사 사유 및 주요 지표를 요약하는 시각화 자동화

실제 기업여신 심사의 흐름(데이터 입력 → 평가 → 의사결정)을 흉내 낸 Streamlit 인터페이스 구현

📦 프로젝트 범위 (신입 개인이 가능한 수준)
구분	범위
입력 데이터	20~30개 기업의 표준 재무제표 (직접 수집 또는 가공)
목표 변수	승인/거절 여부 (임의 기준 설정 가능: 예, 부채비율>300% → 거절 등)
분석 방법	Logistic Regression 또는 XGBoost 등 1~2개 모델
자동화 범위	Streamlit으로 웹 UI 구성, SHAP 값으로 영향 지표 시각화

📊 데이터 구성 예시
기업명	유동비율	부채비율	매출액	영업이익률	ROA	승인여부
A사	150%	200%	30억	3.2%	2.1%	1
B사	70%	380%	12억	-1.2%	-0.4%	0

※ 승인여부는 직접 만든 규칙으로 생성 가능 (if ROA > 1 and 부채비율 < 300% → 승인 등)

🛠 개발 구성
1. 데이터 수집 및 라벨링
DART 재무제표 크롤링 or 모의 데이터셋 생성

승인/거절 라벨은 수치 기준으로 임의 생성 (신입용 단순화)

2. 전처리 및 모델링
이상치 제거, 정규화

간단한 ML 알고리즘으로 분류 모델 (LogisticRegression, XGBoost)

모델 평가 (Accuracy, Confusion Matrix)

3. 모델 해석
SHAP or Feature importance로 영향 변수 시각화

"심사 사유 요약" 텍스트 자동화 (예: "높은 부채비율로 인해 거절됨")

4. Streamlit UI
기업명과 지표 입력 → 자동 심사 결과 출력

승인/거절 결과 + 주요 근거 시각화 + 보고서 요약

📄 파일 구조 예시
kotlin
복사
편집
corporate_credit_project/
├── data/
│   └── company_financials.csv
├── model/
│   └── trained_model.pkl
├── app/
│   └── streamlit_app.py
├── utils/
│   └── preprocessing.py
│   └── decision_rule.py
├── report/
│   └── output_example.pdf
├── README.md


🔍 포트폴리오 제출 구성
GitHub 저장소 링크 (README에 구조/데모 설명)

Streamlit 앱 영상 시연 or 링크

PDF 보고서 예시 (기업별 승인 결과 + 사유)

요약 PPT (문제정의, 모델링, 결과, 시사점)

🔧 사용 기술
분야	도구
분석	Pandas, Scikit-learn, XGBoost
해석	SHAP
UI	Streamlit
문서	Jupyter Notebook, ReportLab (선택)

📘 발전 방향 (심화 가능시)
DART 공시 + 뉴스 텍스트 분석 추가 (ESG, 부정이슈 등)

한도금액 추천 모델 추가

여러 모형 비교 및 앙상블

