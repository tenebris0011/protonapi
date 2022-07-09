# Proton API EndPoint
I know that proton offers an interface for pulling your steam library 
and showing the score for each item in your library but hey, I like learning.

## Purpose
This API takes a steamid which you can get [here](https://www.steamidfinder.com/)
and retrieves your library, runs a search against the ProtonDB API to get its rating.

## How to get started
### Requirements
- Docker
- Docker Compose
- Python

### Running the project
- Clone the git repo down to your machine.
- Get a steam api key by going [here](https://steamcommunity.com/login/home/?goto=%2Fdev%2Fapikey) and logging in.
- Add your steam API key to the .env file.
- To run the API in production mode
  - Set the STAGE variable in .env to prod and execute the below command 
  ```bash
  docker compose --env-file ./.env up -d
  ```
- To run the API in dev mode
  - Set the STAG variable in .env to dev and execute the below command
  ```bash
  docker compose -f .\docker-compose.yml -f .\docker-compose.dev.yml --env-file ./.env up
  ```
- Once the container starts you can hit the API endpoint using http://127.0.0.1:8080/api/v1/games/all?steamid={YOUR_STEAM_ID}
- If you want to update the cache for all 2 million games in the steam library https://127.0.0.1:8080/api/v1/update_cache
  - This end point takes awhile to return and requires further optimization
## To Do
- Optimize the Update Cache endpoint.
  - This iterates through 2 million+ records. Need to find a better way to create this cache.
- Add an endpoint to retrieve user steam id.
- Process multiple requests to the same end point at once.
  - Currently, able to call update cache and the user game endpoint at the same time, but unable to run two calls to the same endpoint at once.
- Implement proper error handling.
- Implement logging.
## Completed
- Implement Redis caching.
- Fix issue with initial crash of protonapi Docker Container do to Redis Loading.