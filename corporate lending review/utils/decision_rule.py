def explain_decision(ROA, 부채비율):
    """
    승인/거절 결과에 대한 주요 설명 사유 반환
    """
    reasons = []

    if ROA < 1.0:
        reasons.append("ROA가 낮아 수익성에 대한 우려가 있습니다.")
    if 부채비율 > 300:
        reasons.append("부채비율이 높아 재무건전성에 문제가 있을 수 있습니다.")
    if ROA > 2.0 and 부채비율 < 200:
        reasons.append("수익성과 안정성이 모두 양호한 상태입니다.")

    return reasons
