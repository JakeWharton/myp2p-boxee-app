import mc

SPORTS = [
    {'title': 'NHL' , 'id': 29},
    {'title': 'NFL' , 'id': 32},
    {'title': 'NBA' , 'id': 10},
    {'title': 'MLB' , 'id': 22},
    {'title': 'NCAA', 'id': 33},
]

def loadSports(listId):
    sportsList = mc.GetActiveWindow().GetList(listId)
    sportsItems = mc.ListItems()
    for sport in SPORTS:
        sportItem = mc.ListItem(mc.ListItem.MEDIA_UNKNOWN)
        sportItem.SetLabel(sport.get('title', 'Unknown'))
        sportsItems.append(sportItem)
    sportsList.SetItems(sportsItems)
