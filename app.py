import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta, datetime
import math
import pandas as pd
import xlsxwriter
import time

useetv_base_url = 'https://www.useetv.com/livetv/'
channel_tv = ['tvri', 'beritasatu', 'indosiar', 'kompastv', 'metrotv', 'net', 'trans7', 'transtv', 'sctv']
# problem_channel_tv = ['trans7', 'sctv']

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

def get_text_from_tag(tag):
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
  titles = list(map(get_text_from_tag, schedule_by_date.select("h4")))
  times = normalize_time(list(map(get_text_from_tag, schedule_by_date.select("p"))))
  nrows = get_num_of_row_of_a_schedules(times)
  schedule = extract_schedule_into_list(titles, nrows)
  return schedule

def get_channel_schedule_in_a_week(channel, dates):
  print("Start fetching schedules for " + channel)
  schedule_dict = {}
  page = requests.get(useetv_base_url + channel)
  parser = BeautifulSoup(page.content, 'html.parser')
  for date in reversed(dates):
    schedule = extract_schedule_in_a_day(parser, date)
    schedule_dict[date] = schedule
  print("Done fetch " + channel + " schedules")
  return schedule_dict

def get_all_channel_schedule_in_a_week(channels, dates):
  schedules_dict = {}
  for channel in channels:
    schedule = get_channel_schedule_in_a_week(channel, dates)
    schedules_dict[channel] = schedule
  transformed_schedules = transform_schedules_dict_to_dataframes(schedules_dict, dates)
  export_schedules_to_xlsx(transformed_schedules)

def transform_schedules_dict_to_dataframes(schedules_dict, dates):
  dataframes_dict = {}
  for date in reversed(dates):
    df = pd.DataFrame()
    df['Waktu'] = times_on_csv
    for channel in schedules_dict.keys():
      schedule = schedules_dict[channel][date]
      df[channel.upper()] = pd.Series(schedule)
    dataframes_dict[date] = df
  return dataframes_dict

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

def export_schedules_to_xlsx(schedules):
  print("Start export schedules to XLSX file...")
  writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
  for date, schedule in schedules.items():
    schedule.to_excel(writer, sheet_name=date, index=False)
  writer.save()
  print("Done write to XLSX file.")

start_time = time.time()
dates = generate_date_a_week_ago()
get_all_channel_schedule_in_a_week(channel_tv, dates)
end_time = time.time()
time_elapsed = end_time - start_time
print("Duration: " + str(time_elapsed) + " second")
