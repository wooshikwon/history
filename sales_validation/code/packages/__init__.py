from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def format_date(ymd):

    date_obj = datetime.strptime(str(ymd), '%Y%m%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')

    return formatted_date

def get_previous_months(ymd):

    date_obj = datetime.strptime(str(ymd), '%Y%m%d')
    
    # 지난달 계산
    one_month_ago = date_obj.replace(day=1) - timedelta(days=1)
    one_month_ago_str = one_month_ago.strftime('%Y-%m')
    
    # 2달 전 계산
    two_months_ago = one_month_ago.replace(day=1) - timedelta(days=1)
    two_months_ago_str = two_months_ago.strftime('%Y-%m')
    
    return one_month_ago_str, two_months_ago_str

def get_previous_ymd(date_int):
    # 정수형 날짜를 문자열로 변환
    date_str = str(date_int)
    # 문자열을 날짜 객체로 변환
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    # 한 달 전의 날짜를 계산
    one_month_ago = date_obj - relativedelta(months=1)
    # 결과 날짜를 'YYYY-mm-dd' 형식의 문자열로 변환하여 반환
    return one_month_ago.strftime('%Y-%m-%d')