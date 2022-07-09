import json
import sys
from datetime import timedelta
import os
import httpx
import redis
from fastapi import FastAPI
from time import sleep


def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            password=os.getenv('REDIS_PASSWORD'),
            socket_timeout=5
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.AuthenticationError:
        print("AuthenticationError")
        sys.exit(1)
    except redis.exceptions.BusyLoadingError:
        sleep(5)
        try:
            client = redis.Redis(
                host=os.getenv('REDIS_HOST'),
                port=os.getenv('REDIS_PORT'),
                password=os.getenv('REDIS_PASSWORD'),
                socket_timeout=5
            )
            ping = client.ping()
            if ping is True:
                return client
        except redis.AuthenticationError:
            print("AuthenticationError")
            sys.exit(1)


client = redis_connect()


def getUserGames(steamid: int) -> dict:
    """Data from steam user library api."""
    data = get_routes_from_cache(key=steamid)

    if data is not None:
        data = json.loads(data)
        return data
    else:
        with httpx.Client() as client:
            base_url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001"
            apiKey = os.getenv('API_KEY')

            url = f"{base_url}/?key={apiKey}&steamid={str(steamid)}&format=json"

            data = client.get(url).json()
            data = json.dumps(data)
            state = set_routes_to_cache(key=steamid, value=data)

            if state is True:
                return json.loads(data)
        return data


def fetchGameRating(appid: int, gameName: str) -> dict:
    """Data from protondb api."""
    data = get_routes_from_cache(key=gameName)
    if data is not None:
        data = json.loads(data)
        return data
    else:
        with httpx.Client() as client:
            try:
                url = f"https://www.protondb.com/api/v1/reports/summaries/{str(appid)}.json"
                data = client.get(url).json()
                data = json.dumps(data)
                state = set_routes_to_cache(key=gameName, value=data)

                if state is True:
                    return json.loads(data)
            except json.decoder.JSONDecodeError:
                data = {'trendingTier': "", 'bestReportedTier': "", 'confidence': ""}
                data = json.dumps(data)
                state = set_routes_to_cache(key=gameName, value=data)

                if state is True:
                    return json.loads(data)

        return data


def fetchGames(key: str) -> dict:
    """Data from steam games api."""

    data = get_routes_from_cache(key=key)

    if data is not None:
        data = json.loads(data)
        return data

    else:
        with httpx.Client() as client:
            appId = ""
            apiKey = os.getenv('API_KEY')
            data = dict()
            x = 0
            while True:
                url = f"https://api.steampowered.com/IStoreService/GetAppList/v1/?&include_games=true&last_appid={appId}&max_results=50000&key={apiKey}"
            #url = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
                appList = client.get(url).json()

                for game in appList['response']['apps']:
                    data[x] = json.dumps(game)
                    x += 1
                try:
                    if appList['response']['have_more_results']:
                        appId = appList['response']['last_appid']
                    else:
                        break
                except KeyError:
                    break
            data = json.dumps(data)
            state = set_routes_to_cache(key=key, value=data)
            if state is True:
                return json.loads(data)
        return data


def get_routes_from_cache(key: str) -> str:
    """Data from redis."""
    val = client.get(key)
    return val


def set_routes_to_cache(key: str, value: str) -> bool:
    """Data to redis."""

    state = client.setex(key, timedelta(days=31), value=value, )
    return state


app = FastAPI(title="ProtonDB API")


@app.get('/api/v1/update_cache')
def updateGameRatingCache():
    allGames = fetchGames("games")
    state = False

    for item in allGames:
        item = json.loads(allGames[item])
        try:
            rating = fetchGameRating(item['appid'], item['name'])
            data = {"bestReportedTier": rating['bestReportedTier'], "trendingTier": rating['trendingTier'],
                    "confidence": rating["confidence"]}
            data = json.dumps(data)
            state = set_routes_to_cache(key=item['name'], value=data)
        except KeyError:
            data = {'trendingTier': "", 'bestReportedTier': "", 'confidence': ""}
            data = json.dumps(data)
            state = set_routes_to_cache(key=item['name'], value=data)
    if state is True:
        return "Cache successfully updated"


@app.get('/api/v1/games/all')
def getUserGameRatings(steamid: int) -> dict:
    if steamid:
        userGames = getUserGames(steamid)
        allGames = fetchGames("games")
        results = {}
        for game in userGames['response']['games']:
            for item in allGames:
                item = json.loads(allGames[item])
                if game['appid'] == item['appid']:
                    rating = fetchGameRating(item['appid'], item['name'])
                    data = {item['name']: {"bestReportedTier": rating['bestReportedTier'],
                                            "trendingTier": rating['trendingTier'], "confidence": rating["confidence"]}}
                    results.update(data)
        return results
