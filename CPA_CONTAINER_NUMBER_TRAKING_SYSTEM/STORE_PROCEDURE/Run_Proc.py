import pymysql
import schedule
import time
import datetime
def job():
    conn = pymysql.connect(host='10.110.0.162',user='user1',password='user1test',db='ctmsmis',charset='utf8',
                                       cursorclass=pymysql.cursors.DictCursor)
    cur = conn.cursor()
    str = "CALL update_mis_ocr_temp_info()"
    todayDateTimePr = datetime.datetime.today().strftime("%Y-%m-%d, %H:%M:%S")
    print("pre executed at "+todayDateTimePr)
    cur.execute(str)
    todayDateTimePo = datetime.datetime.today().strftime("%Y-%m-%d, %H:%M:%S")
    print("post executed at "+todayDateTimePo)
    cur.close()
    conn.close()

#schedule.every(10).minutes.do(job)

while True:
    job()
    time.sleep(600)
