import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# 데이터 로딩
df = pd.read_csv("data/company_financials.csv")
X = df[['유동비율', '부채비율', '매출액', '영업이익률', 'ROA']]
y = df['승인여부']

# 학습/테스트 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 저장
model_path = ''
with open("rf_credit_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ 모델 학습 및 저장 완료: rf_credit_model.pkl")
