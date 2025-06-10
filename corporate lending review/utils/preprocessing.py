import pandas as pd

def preprocess_input(유동비율, 부채비율, 매출액, 영업이익률, ROA):
    """
    사용자 입력을 정제하여 모델 입력 형식으로 변환
    """
    input_dict = {
        '유동비율': [유동비율],
        '부채비율': [부채비율],
        '매출액': [매출액],
        '영업이익률': [영업이익률],
        'ROA': [ROA]
    }
    return pd.DataFrame(input_dict)
