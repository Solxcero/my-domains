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
    one_year_ago = date - timedelta(days=365 * years)
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

# 값치 점수

def valueScore(fundamental):
    fundamental = fundamental[fundamental['PER'] != 0].copy()
    fundamental = fundamental.replace([np.inf, -np.inf], np.nan).dropna(subset=['PER', 'PBR'])

    ep = (1 / fundamental['PER']).to_numpy()
    bp = (1 / fundamental['PBR']).to_numpy()

    ep_win = winsorize_series(ep)
    bp_win = winsorize_series(bp)

    ep_z = (ep_win - ep_win.mean()) / ep_win.std()
    bp_z = (bp_win - bp_win.mean()) / bp_win.std()

    vs = (ep_z + bp_z) / 2
    return pd.DataFrame({'VS': vs}, index=fundamental.index)

# 성장 점수
def growScore(ohlcv_today, ohlcv_past, eps_now, eps_past):
    ks = pd.merge(ohlcv_past['종가'], ohlcv_today['종가'],
                  left_index=True, right_index=True, how='inner')
    ks.columns = ['매수가', '매도가']
    mmt = ((ks['매도가'] - ks['매수가']) / ks['매수가'] * 100).to_numpy()

    mmt_win = winsorize_series(mmt)
    mmt_z = (mmt_win - mmt_win.mean()) / mmt_win.std()
    mmt_series = pd.Series(mmt_z, index=ks.index)

    eps = pd.merge(eps_past, eps_now, left_index=True, right_index=True, how='inner')
    eps.columns = ['EPS_2', 'EPS_1']
    eps['NetChange'] = eps['EPS_1'] - eps['EPS_2']
    eps = pd.merge(eps, ohlcv_today['종가'], left_index=True, right_index=True, how='inner')
    eps['approxPEG'] = eps['NetChange'] / eps['종가']
    eps['approxPEG'].replace([np.inf, -np.inf], np.nan, inplace=True)
    eps = eps.dropna()

    peg = eps['approxPEG'].to_numpy()
    peg_win = winsorize_series(peg)
    peg_win[eps['NetChange'].to_numpy() == 0] = 0
    peg_z = (peg_win - peg_win.mean()) / peg_win.std()

    mmt_df = pd.DataFrame({'stn_MM': mmt_z}, index=ks.index)
    peg_df = pd.DataFrame({'stn_P': peg_z}, index=eps.index)

    growth = pd.merge(mmt_df, peg_df, left_index=True, right_index=True, how='inner')
    growth['GS'] = (growth['stn_MM'] + growth['stn_P']) / 2

    return growth[['GS']]

# 시철

def totalCap(cap):
    return cap[['시가총액']]

# 참조 관계 범위에서 rank 계산 값은 Pandas 유지가 더 적합

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

# 메인

def main(date, market):
    print(f"\u23f3 Fetching data for {date}, {market}...")

    past1y = get_previous_business_day(date, 1)
    past3y = get_previous_business_day(date, 3)

    fundamental_today = stock.get_market_fundamental(date, market)
    cap_today = stock.get_market_cap(date, market)
    ohlcv_today = stock.get_market_ohlcv(date, market)
    ohlcv_past = stock.get_market_ohlcv(past1y, market)

    try:
        eps_now = stock.get_market_fundamental(date, market)[['EPS']]
        eps_past = stock.get_market_fundamental(past3y, market)[['EPS']]
    except:
        print("\u274c EPS \ub370\uc774\ud130 \ubc1c\uc0dd")
        eps_now = pd.DataFrame()
        eps_past = pd.DataFrame()

    value_S = valueScore(fundamental_today)
    growth_S = growScore(ohlcv_today, ohlcv_past, eps_now, eps_past)
    cap = totalCap(cap_today)

    return finalScore(value_S, growth_S, cap)

if __name__ == "__main__":
    import time
    date = sys.argv[1]
    market = sys.argv[2]

    start = time.time()

    final_result = main(date, market)
    name_dict = get_name_dict(market)
    plot(final_result, name_dict)

    end = time.time()
    print(f"Elapsed time: {end - start:.4f} sec")
