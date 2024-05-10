from datetime import datetime, timedelta

def get_lastsunday(date_int):

    date_str = str(date_int)
    date_obj = datetime.strptime(date_str, '%Y%m%d')
    
    offset = (date_obj.weekday() + 1) % 7
    last_sunday = date_obj - timedelta(days=offset)

    return last_sunday.strftime('%Y-%m-%d')