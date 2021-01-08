import requests
from bs4 import BeautifulSoup

VIDIO_BASE_URL = 'https://www.vidio.com/live/'

def get_raw_schedule_by_channel(channel_id):
  page = requests.get(VIDIO_BASE_URL + channel_id + '/schedules')
  parser = BeautifulSoup(page.content, 'html.parser')
  return parser

def get_schedule_tag_id(date):
  return 'schedule-content-' + date.replace('-', '')

def get_raw_schedule_by_date(parser, date):
  return parser.find("div", {"id": get_schedule_tag_id(date)})

def get_titles_from_raw_schedule(raw_schedule):
  class_name = 'b-livestreaming-daily-schedule__item-content-title'
  return list(map(get_text_from_tag, raw_schedule.find_all(class_=class_name)))

def get_times_from_raw_schedule(raw_schedule):
  class_name = 'b-livestreaming-daily-schedule__item-content-caption'
  times = list(map(get_text_from_tag, raw_schedule.find_all(class_=class_name)))
  return remove_wib_word(times)

def get_text_from_tag(tag):
  return tag.text

def remove_wib_word(times):
  return [time.replace(' WIB', '') for time in times]
