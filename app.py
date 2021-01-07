import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import pandas as pd
import math

useetv_base_url = 'https://www.useetv.com/livetv/'
channel_tv = ['tvri', 'beritasatu', 'indosiar', 'kompastv', 'metrotv', 'net', 'trans7', 'transtv', 'sctv']
problem_channel_tv = ['trans7', 'sctv']

times_on_csv = [
  '00.00 - 00.30', '00.30 - 01.00', '01.00 - 01.30', '01.30 - 02.00', '02.00 - 02.30', '02.30 - 03.00', 
  '03.00 - 03.30', '03.30 - 04.00', '04.00 - 04.30', '04.30 - 05.00', '05.00 - 05.30', '05.30 - 06.00', 
  '06.00 - 06.30', '06.30 - 07.00', '07.00 - 07.30', '07.30 - 08.00', '08.00 - 08.30', '08.30 - 09.00', 
  '09.00 - 09.30', '09.30 - 10.00', '10.00 - 10.30', '10.30 - 11.00', '11.00 - 11.30', '11.30 - 12.00', 
  '12.00 - 12.30', '12.30 - 13.00', '13.00 - 13.30', '13.30 - 14.00', '14.00 - 14.30', '14.30 - 15.00', 
  '15.00 - 15.30', '15.30 - 16.00', '16.00 - 16.30', '16.30 - 17.00', '17.00 - 17.30', '17.30 - 18.00', 
  '18.00 - 18.30', '18.30 - 19.00', '19.00 - 19.30', '19.30 - 20.00', '20.00 - 20.30', '20.30 - 21.00', 
  '21.00 - 21.30', '21.30 - 22.00', '22.00 - 22.30', '22.30 - 23.00', '23.00 - 23.30', '23.30 - 00.00'
]

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
  times = normalize_time(list(map(extract_text_from_tag, schedule_by_date.select("p"))))
  nrows = get_num_of_row_of_a_schedules(times)
  schedule = extract_schedule_into_list(titles, nrows)
  return schedule

def extract_schedule_in_a_week(dates):
  for date in dates:
    print(date)
    schedules = {}
    for channel in channel_tv:
      page = requests.get(useetv_base_url + channel)
      parser = BeautifulSoup(page.content, 'html.parser')
      schedule = extract_schedule_in_a_day(parser, date)
      schedules[channel] = schedule
    print(extract_schedules_to_dataframe(schedules))
    break

def get_num_of_row_of_a_schedules(times):
  nrows = []
  for time in times:
    nrow = get_num_of_row_of_a_schedule(time)
    nrows.append(nrow)
  return nrows

def get_num_of_row_of_a_schedule(time):
  extracted_time = time.replace(' ', '').split('-')
  start_time = datetime.strptime(extracted_time[0], '%H:%M')
  end_time = datetime.strptime(extracted_time[1], '%H:%M')
  diff = (end_time - start_time).total_seconds()
  if diff >= 0 and diff <= 900: # drop under-equal 15mins program
    return 0
  elif diff > 900 and diff < 2700: # resolve under 45mins program
    return 1
  else:
    nrow = math.ceil(diff / 1800)
    if nrow < 0: # resolve offset day
      nrow = nrow + 48
  return nrow

def extract_schedule_into_list(titles, nrows):
  if len(nrows) != len(titles):
    print("length of nrows should be same with length of titles! exit.")
    quit()
  schedule_in_a_day = []
  for i in range(len(titles)):
    for j in range(nrows[i]):
      schedule_in_a_day.append(titles[i])
  return schedule_in_a_day

def normalize_time(times):
  default_time = '00:00'
  if default_time not in times[0]:
    times[0] = times[0].replace(times[0][:5], default_time)
  if default_time not in times[-1]:
    times[-1] = times[-1].replace(times[-1][-5:], default_time)
  return times

def extract_schedules_to_dataframe(schedules):
  df = pd.DataFrame()
  df['Waktu'] = times_on_csv
  for key, value in schedules.items():
    df[key.upper()] = pd.Series(value)
  return df

dates = generate_date_a_week_ago()
extract_schedule_in_a_week(dates)
