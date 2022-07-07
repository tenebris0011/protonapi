from fastapi import FastAPI
import requests
import os


app = FastAPI(title="ProtonDB API")

apiKey = os.getenv('API_KEY')


# Retrieve list of games from steam API.
def findGame(appId):
    games = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/").json()
    for item in games['applist']['apps']:
        if appId == item['appid']:
            return item['name']


# Fetch game rating from Proton DB
def fetchRating(appId):
    protonResults = requests.get(f"https://www.protondb.com/api/v1/reports/summaries/{str(appId)}.json")
    if protonResults.status_code == 200:
        return protonResults.json()


# Fetch users library and get Proton Rating for each item.
@app.get('/api/v1/games/all')
async def getAllRatings(steamid: int):
    # start_time = time.time()
    if steamid:
        response = requests.get(
            f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={apiKey}&steamid={str(steamid)}&format=json")
        results = response.json()
        response = {}
        for game in results['response']['games']:
            results = fetchRating(game['appid'])
            if results:
                gameName = findGame(game['appid'])
                newGame = {
                    gameName: {'trendingTier': results['trendingTier'], 'bestReportedTier': results['bestReportedTier'],
                               'confidence': results['confidence']}}
                response.update(newGame)
            else:
                gameName = findGame(game['appid'])
                newGame = {gameName: {'trendingTier': "", 'bestReportedTier': "", 'confidence': ""}}
                response.update(newGame)
        return response
