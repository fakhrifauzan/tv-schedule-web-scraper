from client import useetv, vidio

def get_week_schedule_parser_by_source_and_channel(source, channel):
  if source == 'vidio':
    parser = vidio.get_raw_schedule_by_channel(channel)
  elif source == 'useetv':
    parser = useetv.get_raw_schedule_by_channel(channel)
  else:
    print('Source not supported. Please use useetv or vidio instead.')
    quit()
  return parser

def get_day_schedule_by_source_and_date(source, channel_parser, date):
  if source == 'vidio':
    schedule_by_date = vidio.get_raw_schedule_by_date(channel_parser, date)
    titles = vidio.get_titles_from_raw_schedule(schedule_by_date)
    times = vidio.get_times_from_raw_schedule(schedule_by_date)
  elif source == 'useetv':
    schedule_by_date = useetv.get_raw_schedule_by_date(channel_parser, date)
    titles = useetv.get_titles_from_raw_schedule(schedule_by_date)
    times = useetv.get_times_from_raw_schedule(schedule_by_date)
  else:
    print('Source not supported. Please use useetv or vidio instead.')
    quit()
  return titles, times
