import mc
import urllib
import re
from feedparser import feedparser
from datetime import date
import time

SPORTS = [
    {
        'title': 'NHL',
        'id': 29,
        'regex_title': re.compile(r'^NHL Today! (?P<month>[A-Za-z]+) (?P<day>\d{1,2})(?:th|nd|st)?,? (?P<year>\d{4})(?P<is_playoffs> \[Stanley Cup Playoffs\])?$'),
        'regex_game': re.compile(r'(?P<est_time>\d{1,2}:\d{2} (?:AM|PM)).*?<b>(?P<team_away>.*?)</b>.*?@.*?<b>(?P<team_home>.*?)</b>.*?<ul>(?P<streams>.*?)</ul>'),
        'regex_stream': re.compile(r'<li><a href="(?P<url>https?://.*?)".*?>(?P<name>.*?)</a>.*?</li>'),
    },
    {
        'title': 'NFL',
        'id': 32
    },
    {
        'title': 'NBA',
        'id': 10
    },
    {
        'title': 'MLB',
        'id': 22
    },
    {
        'title': 'NCAA',
        'id': 33
    },
]
FEED = 'http://www.myp2pforum.eu/external.php?type=RSS2&forumids=%s'
MONTHS = ['', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']


def loadSports():
    mc.ShowDialogWait()
    sportsList = mc.GetActiveWindow().GetList(9000)
    sportsItems = mc.ListItems()
    for sport in SPORTS:
        sportItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        sportItem.SetLabel(sport.get('title', 'Unknown'))
        sportItem.SetProperty("id", str(sport.get('id', -1)))
        sportsItems.append(sportItem)
    sportsList.SetItems(sportsItems)
    mc.HideDialogWait()


def loadSport(sport_id):
    mc.LogDebug("Loading sport %s" % sport_id)
    mc.ShowDialogWait()

    label = mc.GetActiveWindow().GetLabel(9010)
    sport = None
    for SPORT in SPORTS:
        if SPORT['id'] == sport_id:
            sport = SPORT
            break
    else:
        mc.LogError("Sport %s not found." % sport_id)
        mc.ShowDialogOk("Error", "Sport %s not found." % sport_id)
        mc.CloseWindow()
    label.SetLabel(sport['title'])

    gamesList = mc.GetActiveWindow().GetList(9000)
    gamesItems = mc.ListItems()

    content = feedparser.parse(urllib.urlopen(FEED % sport_id))
    for item in content['entries']:
        title = str(item.title)
        match = sport['regex_title'].match(title)
        if match:
            day_date = date(int(match.group('year')), MONTHS.index(match.group('month').lower()), int(match.group('day')))
            if day_date < date.today():
                continue

            for game in sport['regex_game'].finditer(str(item.content)):
                game_time = time.strptime('%s %s EST' % (day_date, game.group('est_time')), '%Y-%m-%d %I:%M %p %Z')
                #Skip games that occured more than 5 hours ago
                if time.localtime(time.mktime(game_time) + 5 * 60 * 60) < time.time():
                    continue
                
                name = '%s @ %s' % (game.group('team_away').strip(), game.group('team_home').strip())

                streams = []
                for stream in sport['regex_stream'].finditer(game.group('streams')):
                    mc.LogDebug('MYP2P::: "%s" - Stream "%s" (%s)' % (name, stream.group('name'), stream.group('url')))
                    streams.append(stream.groupdict())
                stream_string = '\n'.join(['%s\t%s' % (stream['name'], stream['url']) for stream in streams])

                gameItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
                gameItem.SetLabel(name)
                gameItem.SetProperty('streams', stream_string)
                gamesItems.append(gameItem)

    gamesList.SetItems(gamesItems)
    mc.HideDialogWait()


def sportClicked():
    sportsList = mc.GetActiveWindow().GetList(9000)
    selectedItem = sportsList.GetItem(sportsList.GetFocusedItem())
    mc.ActivateWindow(14001)
    loadSport(int(selectedItem.GetProperty("id")))

def gameClicked():
    gamesList = mc.GetActiveWindow().GetList(9000)
    selectedItem = gamesList.GetItem(gamesList.GetFocusedItem())

    streams = []
    for stream in selectedItem.GetProperty('streams').split('\n'):
        title, url = stream.split('\t', 1)
        streams.append({'title': title, 'url': url})

    #TODO: conditional for this...
    import xbmcgui
    selection = xbmcgui.Dialog().select("Choose Stream", [stream['title'] for stream in streams])
    #selection = mc.ShowDialogSelect("Choose Stream", [stream['title'] for stream in streams])

    if selection >= 0:
        item = mc.ListItem()
        item.SetPath(streams[selection]['url'])
        mc.GetPlayer().Play(item)