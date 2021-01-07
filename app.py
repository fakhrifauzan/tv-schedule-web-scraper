import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta

page = requests.get('https://www.useetv.com/livetv/sctv')
parser = BeautifulSoup(page.content, 'html.parser')

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

def extract_schedule_in_a_day(date):
  schedule_by_date = parser.find("div", {"id": date})
  title = list(map(extract_text_from_tag, schedule_by_date.select("h4")))
  time = list(map(extract_text_from_tag, schedule_by_date.select("p")))
  schedule = dict(zip(time, title))
  return schedule

def extract_schedule_in_a_week(dates):
  for date in dates:
    print(date)
    print(extract_schedule_in_a_day(date))

dates = generate_date_a_week_ago()
extract_schedule_in_a_week(dates)
