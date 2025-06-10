import pandas as pd
# 이전 오류로 인해 X_train 등이 유실되었으므로 다시 정의
df = pd.read_csv(r"data\company_financials.csv")
X = df[['유동비율', '부채비율', '매출액', '영업이익률', 'ROA']]
y = df['승인여부']

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import set_korean_font  # 한글 폰트 설정
import numpy as np

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 모델 학습
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)

# 변수 중요도 추출
importances = rf_model.feature_importances_
features = X.columns
indices = np.argsort(importances)[::-1]

# 변수 중요도 시각화
plt.figure(figsize=(8, 5))
plt.title("Feature Importances")
plt.bar(range(X.shape[1]), importances[indices], align='center')
plt.xticks(range(X.shape[1]), [features[i] for i in indices], rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()
