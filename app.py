import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime

useetv_base_url = 'https://www.useetv.com/livetv/'
tvlist = ['tvri', 'beritasatu', 'indosiar', 'kompastv', 'metrotv', 'net', 'trans7', 'transtv', 'sctv']

def extract_text_from_tag(tag):
  return tag.text

def generate_date_a_week_ago():
  reference_date = date.today()
  dates_a_week = [reference_date.isoformat()]
  for i in range(6):
    result = (reference_date - timedelta(days = 1)).isoformat()
    dates_a_week.append(result)
    reference_date -= timedelta(days = 1)
  return dates_a_week

def extract_schedule_in_a_day(parser, date):
  schedule_by_date = parser.find("div", {"id": date})
  titles = list(map(extract_text_from_tag, schedule_by_date.select("h4")))
  times = list(map(extract_text_from_tag, schedule_by_date.select("p")))
  nrows = get_num_of_row_of_a_schedules(times)
  extract_schedule_into_list(titles, nrows)
  schedule = dict(zip(times, titles))
  return schedule

def extract_schedule_in_a_week(dates):
  page = requests.get(useetv_base_url + tvlist[3]) #kompastv
  parser = BeautifulSoup(page.content, 'html.parser')
  for date in dates:
    print(date)
    print(extract_schedule_in_a_day(parser, date))
    break

def get_num_of_row_of_a_schedules(times):
  nrows = []
  for i in range(len(times)):
    nrow = get_num_of_row_of_a_schedule(times[i])
    nrows.append(nrow)
  # print(times)
  # print(nrows)
  return nrows

def get_num_of_row_of_a_schedule(time):
  extracted_time = time.replace(' ', '').split('-')
  start_time = datetime.strptime(extracted_time[0], '%H:%M')
  end_time = datetime.strptime(extracted_time[1], '%H:%M')
  diff = end_time - start_time
  nrow = int(diff.total_seconds() / 1800)
  nrow = nrow + 48 if nrow < 0 else nrow
  return nrow

def extract_schedule_into_list(titles, nrows):
  if len(nrows) != len(titles):
    print("length of nrows should be same with length of titles! exit.")
    quit()
  schedule_in_a_day = []
  for i in range(len(titles)):
    for j in range(nrows[i]):
      schedule_in_a_day.append(titles[i])
  print(schedule_in_a_day)
  return schedule_in_a_day

dates = generate_date_a_week_ago()
extract_schedule_in_a_week(dates)
