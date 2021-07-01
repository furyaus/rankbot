# API Practice Branch
# Version: 0.1
# Date: 01.07.21
# Current Authors: fury#1662, coopzr#3717, Jobelerno#7978
# Github: https://github.com/furyaus/rankbot
# Repl.it: https://replit.com/@furyaus/rankbot
# Original Author: Mazun19 from the PUBG community
# Original Date: 2019

import discord
import os
import requests
import json

bot_token = os.environ['discord_token_2']
API_key = os.environ['API_key']

client = discord.Client()

url = "https://api.pubg.com/shards/steam/"
 
headers = {
  "Authorization": "Bearer "+API_key,
  "Accept": "application/vnd.api+json"
}

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content
  if msg.startswith(".stats"):
    player_name = msg.split(".stats ",1)[1]
    print("Stats called for: "+player_name)
    player_stats_url = url + "players?filter[playerNames]=" + player_name

    r = requests.get(player_stats_url, headers = headers)
    if r.status_code == 200:
      print("Successfully Connected!!!")
    else:
      print("Failed to Connect!!!")
    player_stat = json.loads(r.text)

    def print_match_stats(match_stat):
      match_id = match_stat['data']['id']
      match_attributes = match_stat['data']['attributes']
      print("match_id: ", match_id)
      print(json.dumps(match_attributes, sort_keys=False, indent=4))
      return

    def print_participant_performance(player_name, match_stat):
      match_included = match_stat['included']
      for i in match_included:
        if (i['type'] == 'participant' and i['attributes']['stats']['name'] == player_name):
          sub = i['attributes']['stats']
          print(json.dumps(sub, sort_keys=False, indent=4))
      return

    match_id_list = player_stat['data'][0]['relationships']['matches']['data']

    for match in match_id_list:
      match_id = match['id']
      match_url = url + "matches/{}".format(match_id)
      match_r = requests.get(match_url, headers = headers)
      if match_r.status_code != 200:
        print("Failed to Connect!!!")
      match_stat = json.loads(match_r.text)

    class participant:
      def __init__(self, data):
        self._DBNOs = data['DBNOs']
        self._assists = data['assists']
        self._boosts = data['boosts']
        self._damageDealt = data['damageDealt']
        self._deathType = data['deathType']
        self._headshotKills = data['headshotKills']
        self._heals = data['heals']
        self._killPlace = data['killPlace']
        self._killStreaks = data['killStreaks']
        self._kills = data['kills']
        self._longestKill = data['longestKill']
        self._name = data['name']
        self._playerId = data['playerId']
        self._revives = data['revives']
        self._rideDistance = data['rideDistance']
        self._roadKills = data['roadKills']
        self._swimDistance = data['swimDistance']
        self._teamKills = data['teamKills']
        self._timeSurvived = data['timeSurvived']
        self._vehicleDestroys = data['vehicleDestroys']
        self._walkDistance = data['walkDistance']
        self._weaponsAcquired = data['weaponsAcquired']
        self._winPlace = data['winPlace']

    TotalKills = 0
    TotalWins = 0

    for match in match_id_list:
      match_id = match['id']
      match_url = url + "matches/{}".format(match_id)
      match_r = requests.get(match_url, headers = headers)
      
      if match_r.status_code != 200:
        print("Failed to Connect!!!")
      
      match_stat = json.loads(match_r.text)
      match_included = match_stat['included']
      
      for i in match_included:
        if (i['type'] == 'participant' and i['attributes']['stats']['name'] == player_name):
          sub = i['attributes']['stats']
          
          participant_ = participant(sub)
          TotalKills += participant_._kills
          TotalWins += 1 if participant_._winPlace == 1 else 0

    print("Stats for: ", player_name)
    print("TotalKills: ", TotalKills)
    print("TotalWins: ", TotalWins)

    await message.channel.send("Stats are total kills and total wins for previous 14 days")
    await message.channel.send("Total Kills: "+str(TotalKills))
    await message.channel.send("Total Wins: "+str(TotalWins))

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

client.run(bot_token)
