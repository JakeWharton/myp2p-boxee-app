#!/usr/bin/env python

from datetime import date
import time
import os
import re
import urllib2
import shutil

TITLE = re.compile(r'<a.*?href="threads/(?P<thread_id>\d+).*?".*?>NHL Today! (?P<month>[A-Za-z]+) (?P<day>\d{1,2})(?:th|nd|st)?,? (?P<year>\d{4})(?P<is_playoffs> \[Stanley Cup Playoffs\])?</a>')
GAME = re.compile(r'(?P<est_time>\d{1,2}:\d{2} (?:AM|PM)).*?<b>(?P<team_away>.*?)</b>.*?@.*?<b>(?P<team_home>.*?)</b>.*?<ul>(?P<streams>.*?)</ul>', re.DOTALL)
STREAM = re.compile(r'<li><a href="(?P<url>https?://.*?)".*?>(?P<name>.*?)</a></li>')
MONTHS = ['', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
URL = '[InternetShortcut]\r\nURL=%s'

base_dir = os.path.abspath(os.path.dirname(__file__))
for d in os.listdir(base_dir):
	if os.path.isdir(d):
		shutil.rmtree(d)

titles = urllib2.urlopen('http://www.myp2pforum.eu/forums/29-NHL-Icehockey?styleid=3').read()
games = 'http://www.myp2pforum.eu/threads/%s--?styleid=3'
for daymatch in TITLE.finditer(titles):
	day_id = daymatch.group('thread_id')
	day_date = date(int(daymatch.group('year')), MONTHS.index(daymatch.group('month').lower()), int(daymatch.group('day')))
	day_is_playoffs = daymatch.group('is_playoffs') is not None

	#Skip days in the past
	if day_date < date.today():
		continue

	games = urllib2.urlopen(games % day_id).read()
	for gamematch in GAME.finditer(games):
		game_time = time.strptime('%s %s EST' % (day_date, gamematch.group('est_time')), '%Y-%m-%d %I:%M %p %Z')

		#Skip games that occured more than 5 hours ago
		if time.localtime(time.mktime(game_time) + 5 * 60 * 60) < time.time():
			continue

		name = '%s - %s @ %s' % ( time.strftime("%Y-%m-%d %I:%M%p", game_time), gamematch.group('team_away').strip(), gamematch.group('team_home').strip())
		folder = os.path.join(base_dir, name)
		os.mkdir(folder)
		for streammatch in STREAM.finditer(gamematch.group('streams')):
			with open(os.path.join(folder, streammatch.group('name') + '.url'), 'w') as f:
				f.write(URL % streammatch.group('url'))
