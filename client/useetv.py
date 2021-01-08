import requests
from bs4 import BeautifulSoup

USEETV_BASE_URL = 'https://www.useetv.com/livetv/'

def get_raw_schedule_by_channel(channel):
  page = requests.get(USEETV_BASE_URL + channel)
  parser = BeautifulSoup(page.content, 'html.parser')
  return parser

def get_raw_schedule_by_date(parser, date):
  return parser.find("div", {"id": date})

def get_titles_from_raw_schedule(raw_schedule):
  return list(map(get_text_from_tag, raw_schedule.select("h4")))

def get_times_from_raw_schedule(raw_schedule):
  return list(map(get_text_from_tag, raw_schedule.select("p")))

def get_text_from_tag(tag):
  return tag.text
