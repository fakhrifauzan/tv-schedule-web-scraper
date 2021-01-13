from datetime import date, timedelta, datetime
from itertools import chain
from client import client
from csv import reader
import math
import pandas as pd
import xlsxwriter
import time
import locale

def generate_date_a_week_ago():
  reference_date = date.today()
  dates_a_week = [reference_date.isoformat()]
  for i in range(6):
    result = (reference_date - timedelta(days = 1)).isoformat()
    dates_a_week.append(result)
    reference_date -= timedelta(days = 1)
  return dates_a_week

def extract_schedule_in_a_day(source, channel_parser, date):
  titles, times = client.get_day_schedule_by_source_and_date(source, channel_parser, date)
  times = normalize_time(times)
  nrows = get_num_of_row_of_a_schedules(times)
  schedule = extract_schedule_into_list(titles, nrows)
  return schedule

def get_channel_schedule_in_a_week(channel, source, dates):
  schedule_dict = {}
  channel_parser = client.get_week_schedule_parser_by_source_and_channel(source, channel)
  for date in reversed(dates):
    schedule = extract_schedule_in_a_day(source, channel_parser, date)
    schedule_dict[date] = schedule
  return schedule_dict

def get_all_channel_schedule_in_a_week(channels, dates):
  schedules_dict = {}
  for channel in channels:
    channel_name = channel[0]
    channel_key = channel[1]
    channel_source = channel[2]
    print("Start fetching schedules for " + channel_name + " (" + channel_source + ")")
    schedule = get_channel_schedule_in_a_week(channel_key, channel_source, dates)
    schedules_dict[channel_name] = schedule
    print("Done fetch " + channel_name + " schedules")
  transformed_schedules = transform_schedules_dict_to_dataframes(schedules_dict, dates)
  export_schedules_to_xlsx(transformed_schedules)

def transform_schedules_dict_to_dataframes(schedules_dict, dates):
  dataframes_dict = {}
  for date in reversed(dates):
    df = pd.DataFrame()
    df['WAKTU'] = times_placeholder
    for channel in schedules_dict.keys():
      schedule = schedules_dict[channel][date]
      df[channel] = pd.Series(schedule)
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
  writer = pd.ExcelWriter('result.xlsx', engine='xlsxwriter')
  for date, schedule in schedules.items():
    schedule.to_excel(writer, sheet_name=convert_date(date), index=False)
  writer = custom_excel_formatting(writer)
  writer.save()
  print("Done write to XLSX file.")

def convert_date(date):
  formatted_date = datetime.strptime(date, '%Y-%m-%d')
  return formatted_date.strftime("%A, %d %B %Y")

def custom_excel_formatting(writer):
  for sheet_name in writer.sheets.keys():
    worksheet = writer.sheets[sheet_name]
    custom_format = writer.book.add_format({
      'font_name': 'Arial',
      'font_size': 10,
      'text_wrap': True,
      'valign': 'vcenter'
    })
    border_format = writer.book.add_format({
      'border': True
    })
    worksheet.conditional_format('A1:K49', {
      'type': 'no_errors',
      'format': border_format
    })
    worksheet.freeze_panes(1, 1)
    worksheet.set_column('A:A', 12, custom_format)
    worksheet.set_column('B:Z', 18, custom_format)
    for row in range(1, 49):
      worksheet.set_row(row, 25, custom_format)
  return writer

with open('channels_data.csv', 'r') as read_obj:
  csv_reader = reader(read_obj)
  raw_channel = list(csv_reader)
  raw_channel.pop(0) #remove header
  channels_data = raw_channel

with open('times_placeholder.csv', 'r') as read_obj:
  csv_reader = reader(read_obj)
  raw_times = list(csv_reader)
  times_placeholder = list(chain.from_iterable(raw_times))

locale.setlocale(locale.LC_TIME, "IND")
start_time = time.time()
dates = generate_date_a_week_ago()
get_all_channel_schedule_in_a_week(channels_data, dates)
end_time = time.time()
time_elapsed = end_time - start_time
print("Duration: " + str(time_elapsed) + " second")
