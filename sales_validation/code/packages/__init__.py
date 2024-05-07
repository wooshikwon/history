from datetime import datetime

def format_date(ymd):

    date_obj = datetime.strptime(str(ymd), '%Y%m%d')
    formatted_date = date_obj.strftime('%Y-%m-%d')

    return formatted_date