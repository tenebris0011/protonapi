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

## To Do
- Optimize the API to return results quicker.
  - This API is slow... Like really slow...
- Add an endpoint to retrieve user steam id.
- ~~Fix issue with initial crash of protonapi Docker Container do to Redis Loading~~