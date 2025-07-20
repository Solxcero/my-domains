from pykrx import stock
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import sys
import holidays
import warnings
warnings.filterwarnings('ignore')

# 한국 공휴일 반영
def get_previous_business_day(date_str, years=1):
    kr_holidays = holidays.KR()
    date = datetime.strptime(date_str, "%Y%m%d")
    one_year_ago = date - timedelta(days=365*years)
    while one_year_ago.weekday() >= 5 or one_year_ago in kr_holidays:
        one_year_ago -= timedelta(days=1)
    return one_year_ago.strftime("%Y%m%d")

# numpy 기반 winsorize
def winsorize_series(series, limit=0.05):
    low = np.percentile(series, limit * 100)
    high = np.percentile(series, (1 - limit) * 100)
    return np.clip(series, low, high)

# 종목명 매핑 함수
def get_name_dict(market):
    return {code: stock.get_market_ticker_name(code)
            for code in stock.get_market_ticker_list(market=market)}

# 가치 점수
def valueScore(fundamental):
    fundamental = fundamental[fundamental['PER'] != 0].copy()
    fundamental['E/P'] = 1 / fundamental['PER']
    fundamental['B/P'] = 1 / fundamental['PBR']

    ep = fundamental['E/P']
    bp = fundamental['B/P']

    ep_win = winsorize_series(ep)
    bp_win = winsorize_series(bp)

    ep_z = (ep_win - np.mean(ep_win)) / np.std(ep_win)
    bp_z = (bp_win - np.mean(bp_win)) / np.std(bp_win)

    df = pd.DataFrame({'VS': (ep_z + bp_z) / 2}, index=fundamental.index)
    return df

# 성장 점수
def growScore(date, market, ohlcv_today, ohlcv_past, eps_now, eps_past):
    # 12개월 모멘텀
    ks = pd.merge(ohlcv_past['종가'], ohlcv_today['종가'],
                  left_index=True, right_index=True, how='inner')
    ks.columns = ['매수가', '매도가']
    ks['Momentum'] = (ks['매도가'] - ks['매수가']) / ks['매수가'] * 100
    ks['win_MM'] = winsorize_series(ks['Momentum'])
    ks['stn_MM'] = (ks['win_MM'] - ks['win_MM'].mean()) / ks['win_MM'].std()

    # PEG 유사값
    eps = pd.merge(eps_past, eps_now, left_index=True, right_index=True, how='inner')
    eps.columns = ['EPS_2', 'EPS_1']
    eps['NetChange'] = eps['EPS_1'] - eps['EPS_2']

    eps = pd.merge(eps, ohlcv_today['종가'], left_index=True, right_index=True, how='inner')
    eps['approxPEG'] = eps['NetChange'] / eps['종가']
    eps['approxPEG'].replace([np.inf, -np.inf], np.nan, inplace=True)
    eps = eps.dropna()

    eps['win_P'] = winsorize_series(eps['approxPEG'])
    eps.loc[eps['NetChange'] == 0, 'win_P'] = 0
    eps['stn_P'] = (eps['win_P'] - eps['win_P'].mean()) / eps['win_P'].std()

    growth = pd.merge(ks['stn_MM'], eps['stn_P'], left_index=True, right_index=True, how='inner')
    growth['GS'] = (growth['stn_MM'] + growth['stn_P']) / 2
    return growth[['GS']]

# 시총
def totalCap(cap):
    return cap[['시가총액']]

# 최종 스타일 그룹 분류
def finalScore(value_S, growth_S, cap):
    style = pd.merge(value_S, growth_S, left_index=True, right_index=True, how='inner')
    style = pd.merge(style, cap, left_index=True, right_index=True, how='inner')

    style['GS_Rank'] = style['GS'].rank(ascending=False)
    style['VS_Rank'] = style['VS'].rank(ascending=False)
    style['Rank'] = style['GS_Rank'] / style['VS_Rank']

    style.sort_values('Rank', inplace=True)
    total_cap = style['시가총액'].sum()
    style['cap_ratio'] = style['시가총액'] / total_cap
    style['cum_cap'] = style['cap_ratio'].cumsum()

    style.loc[style['cum_cap'] <= 0.33, 'group'] = 'growth'
    style.loc[(style['cum_cap'] > 0.33) & (style['cum_cap'] <= 0.67), 'group'] = 'neutral'
    style.loc[style['cum_cap'] > 0.67, 'group'] = 'value'

    return style

# 시각화
def plot(final_style, name_dict):
    final_style = final_style.copy()
    final_style['종목명'] = final_style.index.map(lambda x: name_dict.get(x, "Unknown"))
    final_style['label'] = final_style.index + ' (' + final_style['종목명'] + ')'

    fig = go.Figure()
    for group, color in [('growth', 'red'), ('neutral', 'gray'), ('value', 'blue')]:
        data = final_style[final_style['group'] == group]
        fig.add_trace(go.Scatter(
            x=data['GS'], y=data['VS'], mode='markers',
            marker=dict(color=color, size=8),
            hovertext=data['label'], name=group.capitalize() + " Group"
        ))

    fig.update_layout(
        xaxis_title='Growth Score',
        yaxis_title='Value Score',
        margin=dict(l=0, r=0, t=20, b=0),
        width=800,
        height=600
    )
    fig.show()

# 메인 실행 함수
def main(date, market):
    print(f"⏳ Fetching data for {date}, {market}...")

    # 전처리 날짜
    past1y = get_previous_business_day(date, 1)
    past3y = get_previous_business_day(date, 3)

    # 공통 데이터
    fundamental_today = stock.get_market_fundamental(date, market)
    cap_today = stock.get_market_cap(date, market)
    ohlcv_today = stock.get_market_ohlcv(date, market)
    ohlcv_past = stock.get_market_ohlcv(past1y, market)

    try:
        eps_now = stock.get_market_fundamental(date, market)[['EPS']]
        eps_past = stock.get_market_fundamental(past3y, market)[['EPS']]
    except:
        print("❌ EPS 데이터 불러오기 실패")
        eps_now = pd.DataFrame()
        eps_past = pd.DataFrame()

    value_S = valueScore(fundamental_today)
    growth_S = growScore(date, market, ohlcv_today, ohlcv_past, eps_now, eps_past)
    cap = totalCap(cap_today)

    return finalScore(value_S, growth_S, cap)

# 실행
if __name__ == "__main__":
    date = sys.argv[1]
    market = sys.argv[2]

    final_result = main(date, market)
    name_dict = get_name_dict(market)
    plot(final_result, name_dict)
