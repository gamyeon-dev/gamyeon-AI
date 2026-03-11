"""
실수형 데이터를 소수점 정규화 하는 유틸

도메인 전역에서 단일 함수로 통일해 데이터 정규화 누락 방지
"""

def r2(v: float) -> float :
    """실수형 값을 소수점 2자리로 정규화"""
    return round(v, 2)

def r3(v: float) -> float :
    """실수형 값을 소수점 3자리로 정규화"""
    return round(v, 3)