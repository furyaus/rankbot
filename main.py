# RankedBot
# Version: 1.0
# Date: 30.06.21
# Current Authors: fury#1662, coopzr#3717, Jobelerno#7978
# Github: https://github.com/furyaus/rankbot
# Repl.it: https://replit.com/@furyaus/rankbot
# Original Author: Mazun19 from the PUBG community
# Original Date: 2019

import discord
from discord.ext import commands, tasks
from operator import itemgetter
import requests
import json
from json import loads, dumps
import os
import datetime
import asyncio

# Frustrating new discord requirements to pull user.id
clientintents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=clientintents)
client.remove_command("help")

# Global variables
json_file_path = "users.json"
curr_season = "division.bro.official.pc-2018-12"
prev_season = "division.bro.official.pc-2018-11"
prev_prev_season = "division.bro.official.pc-2018-10"
bot_token = os.environ['discord_token']
API_key_fury = os.environ['API_key_fury']
API_key_ocker = os.environ['API_key_ocker']
API_key_p4 = os.environ['API_key_p4']
API_key_progdog = os.environ['API_key_progdog']
d_server = int(os.environ['discord_server'])
announce_channel = int(os.environ['announce_channel'])
stats_channel = int(os.environ['stats_channel'])
general_channel = int(os.environ['general_channel'])
botinfo_channel = int(os.environ['botinfo_channel'])
botinfo_msg = int(os.environ['botinfo_msg'])
top25ranks_channel = int(os.environ['top25ranks_channel'])
top25ranks_msg = int(os.environ['top25ranks_msg'])
top25kda_channel = int(os.environ['top25kda_channel'])
top25kda_msg = int(os.environ['top25kda_msg'])
top25adr_channel = int(os.environ['top25adr_channel'])
top25adr_msg = int(os.environ['top25adr_msg'])
admin_roles = ["Moderators", "Admin", "Boss", "The General", "The Punisher", "The Terminator",]
no_requests = 0
curr_key = 0

# Keys in order - furyaus, ocker, p4, progdog
keys = ["Bearer " + API_key_fury, "Bearer " + API_key_ocker, "Bearer " + API_key_p4, "Bearer " + API_key_progdog]
header = {"Authorization": "Bearer " + API_key_fury,"Accept": "application/vnd.api+json"}

# Open user list and load into arrray
def get_data():
    with open(json_file_path, "r") as file:
        return json.loads(file.read())

def set_data(server_list):
    with open(json_file_path, 'w') as file:
        json.dump(server_list, file, indent=2)

# Catch unknown commands
@client.event
async def on_command_error(ctx, error):
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="Error:",value=f"An error occured: {str(error)}",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Help
@client.command(pass_context=True)
async def help(ctx):
    help_msg = discord.Embed(colour=discord.Colour.orange(),title="Help for Rank Bot",description="Rank Bot manages the roles, ranks and other stats for gamers in The 101 Club.")
    help_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    help_msg.add_field(name=".link:",value="This links your discord userid with your PUBG in-game name. ```.link furyaus```",inline=False)
    help_msg.add_field(name=".stats:",value="Retireve live PUBG API data for a single user and display. No stats, ranks or roles are changed or stored. ```.stats 0cker```",inline=False)
    help_msg.add_field(name=".mystats:",value="Queries PUBG API for your latest data, updates ranks, roles and stats which are stored via a JSON file. ```.mystats```",inline=False)
    help_msg.add_field(name="Report issues: ",value="Head to github and create a new issue or feature request [https://github.com/furyaus/rankbot/issues](https://github.com/furyaus/rankbot/issues)",inline=False)
    help_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=help_msg)

# Admin help
@client.command(pass_context=True)
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def adminhelp(ctx):
    help_msg = discord.Embed(colour=discord.Colour.orange(),title="Admin help for Rank Bot",description="Admin users can remove users and call for global updates.")
    help_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    help_msg.add_field(name=".linked:",value="Returns the total number of currently stored players in JSON file. ```.linked```",inline=False)
    help_msg.add_field(name=".norequests:",value="Returns the total number of requests made to the PUG API. ```.norequests```",inline=False)
    help_msg.add_field(name=".remove:",value="Will allow admin to remove link between Discord user id and PUBG IGN. User can then complete a link again. ```.remove @P4```",inline=False)
    help_msg.add_field(name=".resync:",value="This will force a full resync for all stored players with PUBG API. Only do once per hour. ```.resync```",inline=False)
    help_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=help_msg)

# Support help
@client.command(pass_context=True)
async def support(ctx):
    help_msg = discord.Embed(colour=discord.Colour.orange(),title="Support for The 101 Club members",description="Rank Bot is here to support you through that 3rd, 14th place in scrims")
    help_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    help_msg.add_field(name=".inspire:",value="Responses with inspiration quotes, to really get you back on track```.inspire```",inline=False)
    help_msg.add_field(name=".keywords",value="Rank Bot monitors The 101 Club for PBT (PUBG Burnout). Just let the Bot know. ```Bot is here for you```",inline=False)
    help_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=help_msg)

# Inspire your day
@client.command()
async def inspire(ctx):
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    response_msg.add_field(name="Quote:", value=quote, inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Say
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def say(ctx, *, text):
    channel = client.get_channel(general_channel)
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="Rank Bot says:", value=f"{text}", inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# announce
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def announce(ctx, *, text):
    channel = client.get_channel(announce_channel)
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="Announcement:", value=f"{text}", inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# Report how many users in JSON file
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def linked(ctx):
    user_list=get_data()
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="Users stored: ",value="```" + str(len(user_list)) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Report number of PUBG API requests
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def norequests(ctx):
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="PUG API Requests: ",value="```" + str(no_requests) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)

# Remove user from JSON file
@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def remove(ctx, member: discord.Member):
    user_list=get_data()
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    del user_list[str(member.id)]
    response_msg.add_field(name="Removed: ",value="```" + str(member.name) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)
    set_data(user_list)

# Report top25rank to leaderboard
@tasks.loop(hours=.05)
async def top25ranks():
    user_list=get_data()
    channel = client.get_channel(top25ranks_channel)
    message = await channel.fetch_message(top25ranks_msg)
    new_user_list = sorted(user_list.values(), key=itemgetter('c_rank_points'))
    response_msg = discord.Embed(colour=discord.Colour.orange(),title="Top 25 rank holders in the 101 Club",)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    top_50_string = ''
    i = -1
    total_length = len(new_user_list)
    j = 1 
    while i > -(total_length+1):
        ign = new_user_list[i]['IGN']
        player_rank_points = new_user_list[i]['c_rank_points']
        player_rank = new_user_list[i]['Rank'] 
        curr_line = "%i : %s, %s, %.0f\n" % (abs(j), ign,player_rank,player_rank_points)
        top_50_string += curr_line
        j += 1
        if j == 26:
            break
        i -= 1
    response_msg.add_field(name="Top rank holders:", value="```"+top_50_string+"```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    #await channel.send(embed=response_msg)
    await message.edit(embed=response_msg)
    print("top25ranks updated")

# Report top25kda to leaderboard
@tasks.loop(hours=.05)
async def top25kda():
    user_list=get_data()
    channel = client.get_channel(top25kda_channel)
    message = await channel.fetch_message(top25kda_msg)
    response_msg = discord.Embed(colour=discord.Colour.orange(),title="Top 25 KDA in the 101 Club",)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    new_user_list = sorted(user_list.values(), key=itemgetter('KDA'))
    top_50_string = ''
    total_length = len(new_user_list)
    i = -1
    j = 1
    while i > -(total_length+1):
        ign = new_user_list[i]['IGN']
        player_adr = new_user_list[i]['KDA']
        curr_line = "%i : %s, KDA = %.2f\n" % (abs(j), ign, player_adr)
        top_50_string += curr_line
        j += 1
        if j == 26:
            break
        i -= 1
    response_msg.add_field(name="Top KDA:", value="```"+top_50_string+"```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    #await channel.send(embed=response_msg)
    await message.edit(embed=response_msg)
    print("top25kda updated")

# Report top25adr to leaderboard
@tasks.loop(hours=.05)
async def top25adr():
    user_list=get_data()
    channel = client.get_channel(top25adr_channel)
    message = await channel.fetch_message(top25adr_msg)
    response_msg = discord.Embed(colour=discord.Colour.orange(),title="Top 25 ADR in the 101 Club",)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    new_user_list = sorted(user_list.values(), key=itemgetter('ADR'))
    top_50_string = ''
    total_length = len(new_user_list)
    i = -1
    j = 1
    while i > -(total_length+1):
        ign = new_user_list[i]['IGN']
        player_adr = new_user_list[i]['ADR']
        curr_line = "%i : %s, ADR = %.0f\n" % (abs(j), ign, player_adr)
        top_50_string += curr_line
        j += 1
        if j == 26:
            break
        i -= 1
    response_msg.add_field(name="Top ADR:", value="```"+top_50_string+"```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    #await channel.send(embed=response_msg)-Needed for the first time a post is made, msg id needs updating
    await message.edit(embed=response_msg)
    print("top25adr updated")

# Check my stats - live, direct api data response - allows any PUBG IGN
@client.command()
async def stats(ctx, user_ign):
    global keys
    global header
    global no_requests
    user_list=get_data()
    channel = client.get_channel(stats_channel)
    user_ign = user_ign.replace("<", "")
    user_ign = user_ign.replace(">", "")
    user_ign = user_ign.replace("@", "")
    user_ign = user_ign.replace("!", "")
    for user in user_list:
        if (user == user_ign):
            user_ign = user_list[user]['IGN']
    response_msg = discord.Embed(colour=discord.Colour.orange(),title="Stats for " + user_ign,)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
    initial_r = requests.get(url, headers=curr_header)
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    no_requests += 1
    if initial_r.status_code != 200:
        response_msg.add_field(name="Error: ",value="Incorrect PUBG IGN (case sensitive) or PUBG API is down.",inline=False)
    else:
        player_info = json.loads(initial_r.text)
        player_id = player_info['data'][0]['id'].replace('account.', '')
        season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
        second_request = requests.get(season_url, headers=curr_header)
        curr_header['Authorization'] = keys[no_requests % (len(keys))]
        no_requests += 1
        season_info = json.loads(second_request.text)
        c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
        c_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['subTier']
        c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
        h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
        h_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['subTier']
        h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
        games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
        ADR = round(season_damage / games_played, 0)
        KDA = round(KDA, 2)
        response_msg.add_field(name="Rank:",value=f"Current rank is: {c_rank} {c_tier}: {c_rank_points}\nHighest rank is: {h_rank} {h_tier}: {h_rank_points}",inline=False)
        response_msg.add_field(name="KDA:",value=f"Kills and assists per death: {KDA}",inline=False)
        response_msg.add_field(name="ADR:",value=f"Average damage per game: {ADR}",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# Link Discord user id with PUBG IGN and create user
@client.command(pass_context=True)
async def link(ctx, user_ign):
    global keys
    global header
    global no_requests
    user_list=get_data()
    channel = client.get_channel(stats_channel)
    response_msg = discord.Embed(
        colour=discord.Colour.orange(),
        title="Linking " + user_ign,)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in user_list:
        response_msg.add_field(name="Issue: ",value="Your IGN has already been added to the list, just use .mystats to update your rank",inline=False)
    else:
        url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
        initial_r = requests.get(url, headers=curr_header)
        no_requests += 1
        if initial_r.status_code != 200:
            response_msg.add_field(name="Issue: ",value="Incorrect PUBG IGN (case sensitive) or PUBG API is down.",inline=False)
        else:
            player_info = json.loads(initial_r.text)
            player_id = player_info['data'][0]['id'].replace('account.', '')
            season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
            curr_header['Authorization'] = keys[no_requests % (len(keys))]
            second_request = requests.get(season_url, headers=curr_header)
            no_requests += 1
            season_info = json.loads(second_request.text)
            c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
            c_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['subTier']
            c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
            h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
            h_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['subTier']
            h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
            games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
            team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
            KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
            season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
            season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
            new_rank = c_rank + " " + c_tier
            ADR = round(season_damage / games_played, 0)
            KDA = round(KDA, 2)
            user_list.update({str(user_id): {'IGN': user_ign,'ID': player_id,'Rank': new_rank}})
            user_list[str(user_id)]['c_rank'] = c_rank
            user_list[str(user_id)]['c_tier'] = c_tier
            user_list[str(user_id)]['c_rank_points'] = c_rank_points
            user_list[str(user_id)]['h_rank'] = h_rank
            user_list[str(user_id)]['h_tier'] = h_tier
            user_list[str(user_id)]['h_rank_points'] = h_rank_points
            user_list[str(user_id)]['games_played'] = games_played
            user_list[str(user_id)]['team_kills'] = team_kills
            user_list[str(user_id)]['season_wins'] = season_wins
            user_list[str(user_id)]['KDA'] = KDA
            user_list[str(user_id)]['ADR'] = ADR
            user_list[str(user_id)]['punisher'] = 0
            user_list[str(user_id)]['terminator'] = 0
            user_list[str(user_id)]['team_killer'] = 0
            user_list[str(user_id)]['general'] = 0
            role = discord.utils.get(ctx.guild.roles, name=new_rank)
            await user.add_roles(role)
            response_msg.add_field(name="Rank:",value=f"Current rank is: {c_rank} {c_tier}: {c_rank_points}\nHighest rank is: {h_rank} {h_tier}: {h_rank_points}",inline=False)
            response_msg.add_field(name="KDA:",value=f"Kills and assists per death: {KDA}",inline=False)
            response_msg.add_field(name="ADR:",value=f"Average damage per game: {ADR}",inline=False)
            response_msg.add_field(name="Done: ",value="Discord linked with PUBG IGN and stats saved to file.",inline=False)
    set_data(user_list)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# Pull stats for current user and update database
@client.command()
async def mystats(ctx):
    global keys
    global header
    global no_requests
    user_list=get_data()
    channel = client.get_channel(stats_channel)
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    response_msg = discord.Embed(colour=discord.Colour.orange(),title="Stats for " + user.name,)
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    if str(user_id) in user_list:
        curr_rank = user_list[str(user_id)]['Rank']
        curr_terminator = user_list[str(user_id)]['terminator']
        curr_punisher = user_list[str(user_id)]['punisher']
        curr_teamkiller = user_list[str(user_id)]['team_killer']
        curr_general = user_list[str(user_id)]['general']
        player_id = user_list[str(user_id)]['ID']
        user_ign = user_list[str(user_id)]['IGN']
        season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
        second_request = requests.get(season_url, headers=curr_header)
        no_requests += 1
        season_info = json.loads(second_request.text)
        c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
        c_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['subTier']
        c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
        h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
        h_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['subTier']
        h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
        games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
        team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
        new_rank = c_rank + " " + c_tier
        ADR = round(season_damage / games_played, 0)
        KDA = round(KDA, 2)
        user_list.update({str(user_id): {'IGN': user_ign,'ID': player_id,'Rank': new_rank}})
        user_list[str(user_id)]['c_rank'] = c_rank
        user_list[str(user_id)]['c_tier'] = c_tier
        user_list[str(user_id)]['c_rank_points'] = c_rank_points
        user_list[str(user_id)]['h_rank'] = h_rank
        user_list[str(user_id)]['h_tier'] = h_tier
        user_list[str(user_id)]['h_rank_points'] = h_rank_points
        user_list[str(user_id)]['games_played'] = games_played
        user_list[str(user_id)]['team_kills'] = team_kills
        user_list[str(user_id)]['season_wins'] = season_wins
        user_list[str(user_id)]['KDA'] = KDA
        user_list[str(user_id)]['ADR'] = ADR
        user_list[str(user_id)]['punisher'] = curr_punisher
        user_list[str(user_id)]['terminator'] = curr_terminator
        user_list[str(user_id)]['team_killer'] = curr_teamkiller
        user_list[str(user_id)]['general'] = curr_general
        if new_rank != curr_rank:
            role = discord.utils.get(ctx.guild.roles, name=curr_rank)
            await user.remove_roles(role)
            role = discord.utils.get(user.guild.roles, name=new_rank)
            await user.add_roles(role)
        response_msg.add_field(name="Rank:", value=f"Current rank is: {c_rank} {c_tier}: {c_rank_points}\nHighest rank is: {h_rank} {h_tier}: {h_rank_points}", inline=False)
        response_msg.add_field(name="KDA:",value=f"Kills and assists per death: {KDA}", inline=False)
        response_msg.add_field(name="ADR:",value=f"Average damage per game: {ADR}", inline=False)
        response_msg.add_field(name="Done: ",value=f"Updated stats and saved to file.", inline=False)
    else:
        response_msg.add_field(name="Rank:",value=f"You currently don't have a rank and your IGN isn't added to the list so use .link command to link",inline=False)
    set_data(user_list)
    response_msg.timestamp = datetime.datetime.utcnow()
    await channel.send(embed=response_msg)

# Main program - full resync all data, ranks, roles and stats
@tasks.loop(hours=4.0)
async def update():
    global keys
    global header
    global no_requests
    user_list=get_data()
    guild = client.get_guild(d_server)
    channel = client.get_channel(botinfo_channel)
    message = await channel.fetch_message(botinfo_msg)
    response_msg = discord.Embed(colour=discord.Colour.orange(),title="Sync all data for The 101 Club")
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    curr_header = header
    curr_header["Authorization"] = keys[no_requests % (len(keys))]
    for user in user_list:
        player_id = user_list[user]['ID']
        user_ign = user_list[user]['IGN']
        curr_rank = user_list[user]['Rank']
        curr_terminator = user_list[user]['terminator']
        curr_punisher = user_list[user]['punisher']
        curr_teamkiller = user_list[user]['team_killer']
        curr_general = user_list[user]['general']
        season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
        second_request = requests.get(season_url, headers=curr_header)
        curr_header['Authorization'] = keys[no_requests % (len(keys))]
        no_requests += 1
        if second_request.status_code == 429:
            print('Too many API requests, sleep 100secs')
            await asyncio.sleep(60)
            second_request = requests.get(season_url, headers=curr_header)
            curr_header['Authorization'] = keys[no_requests % (len(keys))]
            no_requests += 1
        season_info = json.loads(second_request.text)
        c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
        c_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['subTier']
        c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
        h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
        h_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['subTier']
        h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
        games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
        team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
        new_rank = c_rank + " " + c_tier
        ADR = round(season_damage / games_played, 0)
        KDA = round(KDA, 2)
        user_list.update( {str(user): {'IGN': user_ign,'ID': player_id,'Rank': new_rank}})
        user_list[str(user)]['c_rank'] = c_rank
        user_list[str(user)]['c_tier'] = c_tier
        user_list[str(user)]['c_rank_points'] = c_rank_points
        user_list[str(user)]['h_rank'] = h_rank
        user_list[str(user)]['h_tier'] = h_tier
        user_list[str(user)]['h_rank_points'] = h_rank_points
        user_list[str(user)]['games_played'] = games_played
        user_list[str(user)]['team_kills'] = team_kills
        user_list[str(user)]['season_wins'] = season_wins
        user_list[str(user)]['KDA'] = KDA
        user_list[str(user)]['ADR'] = ADR
        user_list[str(user)]['punisher'] = curr_punisher
        user_list[str(user)]['terminator'] = curr_terminator
        user_list[str(user)]['team_killer'] = curr_teamkiller
        user_list[str(user)]['general'] = curr_general
        if new_rank != curr_rank:
            role = discord.utils.get(guild.roles, name=curr_rank)
            member = await guild.fetch_member(user)
            await member.remove_roles(role)
            role = discord.utils.get(guild.roles, name=new_rank)
            await member.add_roles(role)

    max_points = 0
    max_points_user = ''
    current_general = 'None'
    for user in user_list:
        if user_list[user]['general'] == 1:
            current_general = user
    for user in user_list:
        if (user_list[user]['c_rank_points'] > max_points):
            max_points = user_list[user]['c_rank_points']
            max_points_user = user
    user_list[max_points_user]['general'] = 1
    if current_general == 'None':
        role = discord.utils.get(guild.roles, name='The General')
        member = await guild.fetch_member(max_points_user)
        await member.add_roles(role)
        response_msg.add_field(name="The General",value=f"A new The General role (highest rank) has been assigned. Congrats! ```{member.name}```",inline=False)
    elif current_general == max_points_user:
        role = discord.utils.get(guild.roles, name='The General')
        member = await guild.fetch_member(current_general)
        response_msg.add_field(name="The General",value=f"The General is the same as before. ```{member.name}```",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='The General')
        member = await guild.fetch_member(current_general)
        await member.remove_roles(role)
        user_list[current_general]['general'] = 0
        member = await guild.fetch_member(max_points_user)
        await member.add_roles(role)
        response_msg.add_field(name="The General",value=f"Previous General (highest rank) has been replaced. Congrats! ```{member.name}```",inline=False)

    max_kda = 0
    max_kda_user = ''
    current_terminator = 'None'
    for user in user_list:
        if user_list[user]['terminator'] == 1:
            current_terminator = user
    for user in user_list:
        if (user_list[user]['KDA'] > max_kda):
            max_kda = user_list[user]['KDA']
            max_kda_user = user
    user_list[max_kda_user]['terminator'] = 1
    if current_terminator == 'None':
        role = discord.utils.get(guild.roles, name='The Terminator')
        member = await guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        response_msg.add_field(name="The Terminator",value=f"A new The Terminator role (highest KDA) has been assigned. Congrats! ```{member.name}```",inline=False)
    elif current_terminator == max_kda_user:
        role = discord.utils.get(guild.roles, name='The Terminator')
        member = await guild.fetch_member(max_kda_user)
        response_msg.add_field(name="The Terminator",value=f"The Terminator is the same as before. ```{member.name}```",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='The Terminator')
        member = await guild.fetch_member(current_terminator)
        await member.remove_roles(role)
        user_list[current_terminator]['terminator'] = 0
        member = await guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        response_msg.add_field(name="The Terminator",value=f"Previous Terminator (highest KDA) has been replaced. Congrats! ```{member.name}```",inline=False)

    max_adr = 0
    max_adr_user = ''
    current_punisher = 'None'
    for user in user_list:
        if user_list[user]['punisher'] == 1:
            current_punisher = user
    for user in user_list:
        if (user_list[user]['ADR'] > max_adr):
            max_adr = user_list[user]['ADR']
            max_adr_user = user
    user_list[max_adr_user]['punisher'] = 1
    if current_punisher == 'None':
        role = discord.utils.get(guild.roles, name='The Punisher')
        member = await guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        response_msg.add_field(name="The Punisher",value=f"A new The Punisher role (highest ADR) has been assigned. Congrats! ```{member.name}```",inline=False)
    elif current_punisher == max_adr_user:
        role = discord.utils.get(guild.roles, name='The Punisher')
        member = await guild.fetch_member(max_adr_user)
        response_msg.add_field(name="The Punisher",value=f"The Punisher is the same as before. ```{member.name}```",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='The Punisher')
        member = await guild.fetch_member(current_punisher)
        await member.remove_roles(role)
        user_list[current_punisher]['punisher'] = 0
        member = await guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        response_msg.add_field(name="The Punisher",value=f"Previous Punisher (highest ADR) has been replaced. Congrats! ```{member.name}```",inline=False)

    max_team_kills = 0
    max_team_kills_user = ''
    current_team_killer = 'None'
    for user in user_list:
        if user_list[user]['team_killer'] == 1:
            current_team_killer = user
    for user in user_list:
        if user_list[user]['team_kills'] > max_team_kills:
            max_team_kills = user_list[user]['team_kills']
            max_team_kills_user = user
    if max_team_kills_user != '':
        user_list[max_team_kills_user]['team_killer'] = 1
    if max_team_kills_user == '':
        response_msg.add_field(name="Dog water",value="No one has any ranked team kills.",inline=False)
    elif current_team_killer == 'None':
        role = discord.utils.get(guild.roles, name='Dog water')
        member = await guild.fetch_member(max_team_kills_user)
        await member.add_roles(role)
        response_msg.add_field(name="Dog water",value=f"A new dog water role has been assigned for the most teamkills this season. ```{member.name}```",inline=False)
    elif current_team_killer == max_team_kills_user:
        role = discord.utils.get(guild.roles, name='Dog water')
        member = await guild.fetch_member(max_team_kills_user)
        response_msg.add_field(name="Dog water",value=f"The dog water is still the same. ```{member.name}```",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='Dog water')
        member = await guild.fetch_member(current_team_killer)
        await member.remove_roles(role)
        user_list[current_team_killer]['team_killer'] = 0
        member = await guild.fetch_member(max_team_kills_user)
        await member.add_roles(role)
        response_msg.add_field(name="Dog water", value=f"Previous dog water player has been replaced. Congrats! ```{member.name}```",inline=False)
    response_msg.add_field(name="Resync completed: ",value="PUGB API requests completed: ```" + str(no_requests) + "```",inline=False)
    response_msg.add_field(name="Finished:",value=f"Roles and ranks have been synced.",inline=False)
    print('Updated everyones stats')
    set_data(user_list)
    response_msg.timestamp = datetime.datetime.utcnow()
    #await channel.send(embed=response_msg)
    await message.edit(embed=response_msg)


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2], admin_roles[3], admin_roles[4], admin_roles[5])
async def resync(ctx):
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="Resync started: ",value="This could take a long time based on the number of users and the PUBG API, please wait for the comfirmation message before more commands.",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)
    await update()
    await top25ranks()
    await top25adr()
    await top25kda()
    response_msg = discord.Embed(colour=discord.Colour.orange())
    response_msg.set_thumbnail(url="https://i.ibb.co/BNrSMdN/101-logo.png")
    response_msg.add_field(name="Resync completed: ",value="PUGB API requests completed: ```" + str(no_requests) + "```",inline=False)
    response_msg.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=response_msg)


# main
@client.event
async def on_ready():
    update.start()
    top25ranks.start()
    top25adr.start()
    top25kda.start()

# Run the bot
client.run(bot_token)
