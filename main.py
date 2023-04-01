from yfDataLoader import *
import datetime as dt

def main():
    # 获取数据下载时间
    # read time log
    with open('dmypy.json', 'r') as f:
        jsdata = json.load(f)

    now = dt.datetime.now()
    next_date = dt.datetime.strptime(jsdata['end_date'], '%Y-%m-%d') + dt.timedelta(days=1)

    if now >= next_date:
        start_date = next_date
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = now.strftime('%Y-%m-%d')
        jsdata['end_date'] = end_date

    # update time log
    with open('dmypy.json', 'w') as f:
        json.dump(jsdata, f, indent=4)
    
    yfd = YfinanceDataLoader(jsdata['folder_path'], )

if __name__ == "__main__":
    main()