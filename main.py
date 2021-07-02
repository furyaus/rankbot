# RankedBot
# Version: 0.9
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
import os
import re

clientintents = discord.Intents.all()
client = commands.Bot(command_prefix=".",intents=clientintents)
client.remove_command("help")

# Global variables
curr_season = "division.bro.official.pc-2018-12"
prev_season = "division.bro.official.pc-2018-11"
prev_prev_season = "division.bro.official.pc-2018-10"

bot_token = os.environ['discord_token']
API_key_fury = os.environ['API_key_fury']
API_key_ocker = os.environ['API_key_ocker']
API_key_p4 = os.environ['API_key_p4']
d_server  = int(os.environ['discord_server'])
d_channel = int(os.environ['discord_channel'])

top50ranks_channel  = int(os.environ['top50ranks_channel'])
top50ranks_msg = int(os.environ['top50ranks_msg'])
top50kda_channel = int(os.environ['top50kda_channel'])
top50kda_msg = int(os.environ['top50kda_msg'])
top50adr_channel = int(os.environ['top50adr_channel'])
top50adr_msg = int(os.environ['top50adr_msg'])

#Keys in order - furyaus, ocker, p4
keys = ["Bearer "+API_key_fury,"Bearer "+API_key_ocker,"Bearer "+API_key_p4]
header = {"Authorization": "Bearer "+API_key_fury,"Accept": "application/vnd.api+json"}

json_file_path = "edited_server_list.json"
with open(json_file_path, 'r') as j:
    server_list = json.loads(j.read())

server_roles = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"]
admin_roles = ["Mods", "Admin", "Boss"]

no_requests = 0
curr_key = 0

@client.event
async def on_ready():
    top50ranks.start()
    top50adr.start()
    top50kda.start()
    updateEverything.start()
    print("Bot is ready.")

@client.command(pass_context=True)
async def help(ctx):
    help_msg = discord.Embed(
        colour=discord.Colour.red(),
        title="Help for Rank Bot",
        description="Rank Bot manages the roles, ranks and other stats for gamers within this discord.")
    help_msg.add_field(name="link:", value=".link PUBG ign, links your discord useridwith your PUBG in-game name, for example '.link furyaus'",inline=False)
    help_msg.add_field(name="checkstats:", value=".checkstats PUBG ign, used to check someone's squad FPP stats, for example '.checkstats furyaus'", inline=False)
    help_msg.add_field(name="mystats:", value=".mystats , Updates your ranks if your stats have changed", inline=False)
    await ctx.send(embed=help_msg)

@client.command(pass_context=True)
async def adminhelp(ctx):
    help_msg = discord.Embed(
        colour=discord.Colour.red(),
        title="Admin Help for Rank Bot",
        description="Admin users can remove users and call for global updates.")
    help_msg.add_field(name="total linked:", value=".total linked users will return the total number of currently stored players", inline=False)
    help_msg.add_field(name="remove user:", value=".removeuser @username (discord user), will allow someone to re-link to fix issues", inline=False)
    help_msg.add_field(name="Update all stats:", value=".updatestatsall will force a full resync with PUBG - only do once per hour", inline=False)
    help_msg.add_field(name="team killer", value=".getteamkiller, finds the player with largest number of team kills", inline=False)
    help_msg.add_field(name="terminator", value=".getterminator, will update top killer", inline=False)
    help_msg.add_field(name="punisher:", value=".getpunisher, will update highest ADR", inline=False)
    help_msg.add_field(name="general:", value=".getgeneral, will update the highest rank in server", inline=False)
    await ctx.send(embed=help_msg)

@client.command()
async def checkstats(ctx, user_ign):
    global keys
    global header
    global no_requests
    channel = client.get_channel(d_channel)
    user_ign = user_ign.replace("<","")
    user_ign = user_ign.replace(">","")
    user_ign = user_ign.replace("@","")
    user_ign = user_ign.replace("!","")
    for user in server_list:
      if (user == user_ign):
          user_ign = server_list[user]['IGN']

    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Rank for "+user_ign,)
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
    initial_r = requests.get(url, headers=curr_header)
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    no_requests += 1
    if initial_r.status_code != 200:
        await ctx.send(
            "Wrong username (capitals in username matters) or too many requests made to the PUBG API (only 5 accounts per minute)")
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
        ADR = round(season_damage/games_played,0)
        KDA = round(KDA,2)

        response_msg.add_field(name="Rank:",
            value=f"Current rank is: {c_rank} {c_tier}: {c_rank_points}\nHighest rank is: {h_rank} {h_tier}: {h_rank_points}",inline=False)
        response_msg.add_field(name="KDA:",
            value=f"Kills and assists per death: {KDA}",inline=False)
        response_msg.add_field(name="ADR:",
            value=f"Average damage per game: {ADR}",inline=False)

        await channel.send(embed=response_msg)

@client.command(pass_context=True)
async def link(ctx, user_ign):
    global keys
    global header
    global no_requests
    channel = client.get_channel(d_channel)
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Rank for "+user_ign,
    )
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send("Your IGN has already been added to the list, just use .mystats to update your rank")
    else:
        url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
        initial_r = requests.get(url, headers=curr_header)
        no_requests += 1
        if initial_r.status_code != 200:
            await ctx.send(
                "Wrong username (capitals in username matters) or the PUBG API is down or too many people are trying "
                "to link at the same time (maximum of 5 per minute)")
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

            new_role = c_rank +" "+ c_tier
            ADR = round(season_damage/games_played,0)
            KDA = round(KDA,2)
            server_list.update({str(user_id): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
            server_list[str(user_id)]['c_rank'] = c_rank
            server_list[str(user_id)]['c_tier'] = c_tier
            server_list[str(user_id)]['c_rank_points'] = c_rank_points
            server_list[str(user_id)]['h_rank'] = h_rank
            server_list[str(user_id)]['h_tier'] = h_tier
            server_list[str(user_id)]['h_rank_points'] = h_rank_points
            server_list[str(user_id)]['games_played'] = games_played
            server_list[str(user_id)]['team_kills'] = team_kills
            server_list[str(user_id)]['season_wins'] = season_wins
            server_list[str(user_id)]['KDA'] = KDA
            server_list[str(user_id)]['ADR'] = ADR
            server_list[str(user_id)]['punisher'] = 0
            server_list[str(user_id)]['terminator'] = 0
            server_list[str(user_id)]['team_killer'] = 0
            server_list[str(user_id)]['general'] = 0

            role = discord.utils.get(ctx.guild.roles, name=new_role)
            await user.add_roles(role)

            response_msg.add_field(name="Rank:", value=f"Current rank is: {c_rank} {c_tier}: {c_rank_points}\nHighest rank is: {h_rank} {h_tier}: {h_rank_points}",inline=False)
            response_msg.add_field(name="KDA:", value=f"Kills and assists per death: {KDA}",inline=False)
            response_msg.add_field(name="ADR:", value=f"Average damage per game: {ADR}",inline=False)

            await channel.send(embed=response_msg)
            with open("edited_server_list.json", "w") as data_file:
                json.dump(server_list, data_file, indent=2)

@client.command()
async def mystats(ctx):
    global keys
    global header
    global no_requests
    channel = client.get_channel(d_channel)
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Rank for "+str(user),
    )
    if str(user_id) in server_list:
        curr_rank = server_list[str(user_id)]['Rank']
        curr_terminator = server_list[str(user_id)]['terminator']
        curr_punisher = server_list[str(user_id)]['punisher']
        curr_teamkiller = server_list[str(user_id)]['team_killer']
        curr_general = server_list[str(user_id)]['general']
        response_msg.add_field(name="Current Rank:", value="Your current rank is: " + server_list[str(user_id)]['Rank'],inline=False)
        player_id = server_list[str(user_id)]['ID']
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

        new_role = c_rank +" "+ c_tier
        ADR = round(season_damage/games_played,0)
        KDA = round(KDA,2)
        server_list[str(user_id)]['c_rank'] = c_rank
        server_list[str(user_id)]['c_tier'] = c_tier
        server_list[str(user_id)]['c_rank_points'] = c_rank_points
        server_list[str(user_id)]['h_rank'] = h_rank
        server_list[str(user_id)]['h_tier'] = h_tier
        server_list[str(user_id)]['h_rank_points'] = h_rank_points
        server_list[str(user_id)]['games_played'] = games_played
        server_list[str(user_id)]['team_kills'] = team_kills
        server_list[str(user_id)]['season_wins'] = season_wins
        server_list[str(user_id)]['KDA'] = KDA
        server_list[str(user_id)]['ADR'] = ADR
        server_list[str(user_id)]['punisher'] = curr_punisher
        server_list[str(user_id)]['terminator'] = curr_terminator
        server_list[str(user_id)]['team_killer'] = curr_teamkiller
        server_list[str(user_id)]['general'] = curr_general

        if new_role == curr_rank:
            response_msg.add_field(name="Previous Rank:", value=f"Your rank is the same as before. {c_rank} {c_tier}",inline=False)
        else:
            try:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name=new_role))
                server_list[str(user_id)]['Rank'] = new_role
                response_msg.add_field(name="Rank:", value=f"Your rank has been updated! {c_rank} {c_tier}",inline=False)
            except Exception as e:
                response_msg.add_field(name="Rank:", value=f"There was an error changing your rank :"+ str(e),inline=False)
    else:
      response_msg.add_field(name="Rank:", value=f"You currently don't have a rank and your IGN isn't added to the list so use .link command to link",inline=False)

    await channel.send(embed=response_msg)

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
async def totalenlisted(ctx):
    await ctx.send(f"There are currently {len(server_list)} people linked in this server!")

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def removeuser(ctx, member: discord.Member):
    await ctx.send(f"Removing {str(member)} from the list..")
    del server_list[str(member.id)]
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def updatestatsall(ctx):
    top50ranks.start()
    top50adr.start()
    top50kda.start()
    await updateEverything()

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getterminator(ctx):
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="terminator (highest KDA)",)
    channel = client.get_channel(d_channel)
    max_kda = 0
    max_kda_user = ''
    current_terminator = 'None'
    for user in server_list:
        if server_list[user]['terminator'] == 1:
            current_terminator = user

    for user in server_list:
        if (server_list[user]['KDA'] > max_kda):
            max_kda = server_list[user]['KDA']
            max_kda_user = user

    server_list[max_kda_user]['terminator'] = 1

    if current_terminator == 'None':
        role = discord.utils.get(ctx.guild.roles, name='terminator')
        member = await ctx.guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        response_msg.add_field(name="terminator:", value=f"A new terminator role (highest KDA) has been assigned to {member.mention}. Congrats!",inline=False)
    elif current_terminator == max_kda_user:
        response_msg.add_field(name="terminator:", value=f"terminator is the same as before.",inline=False)
    else:
        role = discord.utils.get(ctx.guild.roles, name='terminator')
        member = await ctx.guild.fetch_member(current_terminator)
        await member.remove_roles(role)
        server_list[current_terminator]['terminator'] = 0
        member = await ctx.guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        response_msg.add_field(name="terminator:", value=f"Previous terminator (highest KDA) has been replaced by {member.mention}. Congrats!",inline=False)

    await channel.send(embed=response_msg)
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getpunisher(ctx):
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="punisher (highest ADR)",)
    channel = client.get_channel(d_channel)
    max_adr = 0
    max_adr_user = ''
    current_punisher = 'None'

    for user in server_list:
        if server_list[user]['punisher'] == 1:
            current_punisher = user

    for user in server_list:
        if (server_list[user]['ADR'] > max_adr):
            max_adr = server_list[user]['ADR']
            max_adr_user = user

    server_list[max_adr_user]['punisher'] = 1

    if current_punisher == 'None':
        role = discord.utils.get(ctx.guild.roles, name='punisher')
        member = await ctx.guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        response_msg.add_field(name="punisher:", value=f"A new punisher role (highest ADR) has been assigned to {member.mention}. Congrats!",inline=False)
    elif current_punisher == max_adr_user:
        response_msg.add_field(name="punisher:", value=f"punisher is the same as before.",inline=False)
    else:
        role = discord.utils.get(ctx.guild.roles, name='punisher')
        member = await ctx.guild.fetch_member(current_punisher)
        await member.remove_roles(role)
        server_list[current_punisher]['punisher'] = 0
        member = await ctx.guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        response_msg.add_field(name="punisher:", value=f"Previous punisher (highest ADR) has been replaced by {member.mention}. Congrats!",inline=False)

    await channel.send(embed=response_msg)
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getgeneral(ctx):
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="general (highest rank in server)",)
    channel = client.get_channel(d_channel)
    max_points = 0
    max_points_user = ''
    current_general = 'None'

    for user in server_list:
        if server_list[user]['general'] == 1:
            current_general = user

    for user in server_list:
        if (server_list[user]['c_rank_points'] > max_points):
            max_points = server_list[user]['c_rank_points']
            max_points_user = user

    server_list[max_points_user]['general'] = 1

    if current_general == 'None':
        role = discord.utils.get(ctx.guild.roles, name='general')
        member = await ctx.guild.fetch_member(max_points_user)
        await member.add_roles(role)
        response_msg.add_field(name="general:", value=f"A new general role (highest rank in server) has been assigned to {member.mention}. Congrats!",inline=False)
    elif current_general == max_points_user:
        response_msg.add_field(name="general:", value=f"general is the same as before.",inline=False)
    else:
        role = discord.utils.get(ctx.guild.roles, name='general')
        member = await ctx.guild.fetch_member(current_general)
        await member.remove_roles(role)
        server_list[current_general]['general'] = 0
        member = await ctx.guild.fetch_member(max_points_user)
        await member.add_roles(role)
        response_msg.add_field(name="general:", value=f"Previous general (highest rank in server) has been replaced by {member.mention}. Congrats!",inline=False)

    await channel.send(embed=response_msg)
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getteamkiller(ctx):
    channel = client.get_channel(d_channel)
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Literal dog water",)
    max_team_kills = 0
    max_team_kills_user = ''
    current_team_killer = 'None'

    for user in server_list:
        if server_list[user]['team_killer'] == 1:
            current_team_killer = user

    for user in server_list:
        if server_list[user]['team_kills'] > max_team_kills:
            max_team_kills = server_list[user]['team_kills']
            max_team_kills_user = user

    if max_team_kills_user != '':
        server_list[max_team_kills_user]['team_killer'] = 1

    if max_team_kills_user == '':
        response_msg.add_field(name="Team killer:", value="No one has any ranked team kills!",inline=False)
    elif current_team_killer == 'None':
        role = discord.utils.get(ctx.guild.roles, name='Dog water')
        member = await ctx.guild.fetch_member(max_team_kills_user)
        await member.add_roles(role)
        response_msg.add_field(name="Team killer:", value=f"A new dog water role has been assigned to {member.mention}, for the most teamkills this season.",inline=False)
    elif current_team_killer == max_team_kills_user:
        response_msg.add_field(name="Team killer:", value=f"{member.mention} still has the highest ranked team kills.",inline=False)
    else:
        role = discord.utils.get(ctx.guild.roles, name='Dog water')
        member = await ctx.guild.fetch_member(current_team_killer)
        await member.remove_roles(role)
        server_list[current_team_killer]['team_killer'] = 0
        member = await ctx.guild.fetch_member(max_team_kills_user)
        await member.add_roles(role)
        response_msg.add_field(name="Team killer:", value=f"Previous dog water player has been replaced by {member.mention}, with "
            f"{server_list[max_team_kills_user]['team_kills']} teamkills this season",inline=False)

    await channel.send(embed=response_msg)
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@tasks.loop(hours=.05)
async def top50adr():
    channel = client.get_channel(top50adr_channel)
    message = await channel.fetch_message(top50adr_msg)
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Top 50 ADR in the 101 Club",)
    new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
    top_50_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1
    while i > -(total_length+1):
        ign = new_server_list[i]['IGN']
        player_adr = new_server_list[i]['ADR']
        curr_line = "%i : %s, ADR = %.0f\n" % (abs(j), ign, player_adr)
        top_50_string += curr_line
        j += 1
        if j == 51:
            break
        i -= 1
    response_msg.add_field(name="Top ADR:", value=top_50_string,inline=False)
    #await channel.send(embed=response_msg)
    await message.edit(embed=response_msg)
    print("top50adr updated")

@tasks.loop(hours=.05)
async def top50kda():
    channel = client.get_channel(top50kda_channel)
    message = await channel.fetch_message(top50kda_msg)
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Top 50 KDA in the 101 Club",)
    new_server_list = sorted(server_list.values(), key=itemgetter('KDA'))
    top_50_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1
    while i > -(total_length+1):
        ign = new_server_list[i]['IGN']
        player_adr = new_server_list[i]['KDA']
        curr_line = "%i : %s, KDA = %.2f\n" % (abs(j), ign, player_adr)
        top_50_string += curr_line
        j += 1
        if j == 51:
            break
        i -= 1
    response_msg.add_field(name="Top KDA:", value=top_50_string,inline=False)
    #await channel.send(embed=response_msg)
    await message.edit(embed=response_msg)
    print("top50kda updated")

@tasks.loop(hours=.05)
async def top50ranks():
    channel = client.get_channel(top50ranks_channel)
    message = await channel.fetch_message(top50ranks_msg)
    new_server_list = sorted(server_list.values(), key=itemgetter('c_rank_points'))
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Top 50 Rank holders in the 101 Club",)
    top_50_string = ''
    i = -1
    total_length = len(new_server_list)
    j = 1 
    while i > -(total_length+1):
        ign = new_server_list[i]['IGN']
        player_rank = new_server_list[i]['c_rank_points']
        curr_line = "%i : %s, Rank Points = %.0f\n" % (abs(j), ign, player_rank)
        top_50_string += curr_line
        j += 1
        if j == 51:
            break
        i -= 1
    response_msg.add_field(name="Top rank holders:", value=top_50_string,inline=False)
    #await channel.send(embed=response_msg)
    await message.edit(embed=response_msg)
    print("top50ranks updated")

@tasks.loop(hours=4.0)
async def updateEverything():
    global keys 
    global header 
    global no_requests
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Auto rank and role sync - every 4hours")
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    guild = client.get_guild(d_server)
    channel = client.get_channel(d_channel)
    print('Updating everyones stats and roles')
    promoted_users = []
    demoted_users = []
    for user in server_list:
        player_id = server_list[user]['ID']
        user_ign = server_list[user]['IGN']
        curr_role = server_list[user]['Rank']
        curr_terminator = server_list[user]['terminator']
        curr_punisher = server_list[user]['punisher'] 
        curr_teamkiller = server_list[user]['team_killer'] 
        curr_general = server_list[user]['general']
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
        team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
        
        new_role = c_rank +" "+ c_tier
        ADR = round(season_damage/games_played,0)
        KDA = round(KDA,2)
        server_list.update({str(user): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
        server_list[str(user)]['c_rank'] = c_rank
        server_list[str(user)]['c_tier'] = c_tier
        server_list[str(user)]['c_rank_points'] = c_rank_points
        server_list[str(user)]['h_rank'] = h_rank
        server_list[str(user)]['h_tier'] = h_tier
        server_list[str(user)]['h_rank_points'] = h_rank_points
        server_list[str(user)]['games_played'] = games_played
        server_list[str(user)]['team_kills'] = team_kills
        server_list[str(user)]['season_wins'] = season_wins
        server_list[str(user)]['KDA'] = KDA
        server_list[str(user)]['ADR'] = ADR
        server_list[str(user)]['punisher'] = curr_punisher
        server_list[str(user)]['terminator'] = curr_terminator
        server_list[str(user)]['team_killer'] = curr_teamkiller
        server_list[str(user)]['general'] = curr_general

        if new_role != curr_role:
            try:
                member = discord.utils.get(guild.members, id=user)
                await member.add_roles(discord.utils.get(guild.roles, name=new_role))
                server_list[user]['Rank'] = new_role
                if curr_role != 'Bronze':
                    await member.remove_roles(discord.utils.get(guild.roles, name=curr_role))
                if server_roles.index(new_role) > server_roles.index(curr_role):
                    promoted_users.append(user)
                else:
                    demoted_users.append(user)
            except Exception as e:
                print("There was an error changing your rank " + str(e))

    if len(promoted_users) > 0:
        await channel.send("The following users have been promoted:")
        for user in promoted_users:
            member = discord.utils.get(guild.members, id=int(user))
            response_msg.add_field(name="Updated Ranks: ",
              value=f"""{member.mention}""",inline=False)

    max_kda = 0
    max_kda_user = ''
    current_terminator = 'None'

    for user in server_list:
        if server_list[user]['terminator'] == 1:
            current_terminator = user

    for user in server_list:
        if (server_list[user]['KDA'] > max_kda):
            max_kda = server_list[user]['KDA']
            max_kda_user = user

    server_list[max_kda_user]['terminator'] = 1

    if current_terminator == 'None':
        role = discord.utils.get(guild.roles, name='Terminator')
        member = await guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        response_msg.add_field(name="terminator:",
            value=f"A new terminator role (highest KDA) has been assigned to {member.mention}. Congrats!",inline=False)
    elif current_terminator == max_kda_user:
        response_msg.add_field(name="terminator:",
            value=f"terminator is the same as before.",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='Terminator')
        member = await guild.fetch_member(current_terminator)
        await member.remove_roles(role)
        server_list[current_terminator]['terminator'] = 0
        member = await guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        response_msg.add_field(name="terminator:",
            value=f"Previous terminator (highest KDA) has been replaced by {member.mention}. Congrats!",inline=False)

    max_adr = 0
    max_adr_user = ''
    current_punisher = 'None'

    for user in server_list:
        if server_list[user]['punisher'] == 1:
            current_punisher = user

    for user in server_list:
        if (server_list[user]['ADR'] > max_adr):
            max_adr = server_list[user]['ADR']
            max_adr_user = user

    server_list[max_adr_user]['punisher'] = 1

    if current_punisher == 'None':
        role = discord.utils.get(guild.roles, name='Punisher')
        member = await guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        response_msg.add_field(name="punisher:",
            value=f"A new punisher role (highest ADR) has been assigned to {member.mention}. Congrats!",inline=False)
    elif current_punisher == max_adr_user:
        response_msg.add_field(name="punisher:",
            value=f"punisher is the same as before.",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='Punisher')
        member = await guild.fetch_member(current_punisher)
        await member.remove_roles(role)
        server_list[current_punisher]['punisher'] = 0
        member = await guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        response_msg.add_field(name="punisher:",
            value=f"Previous punisher (highest ADR) has been replaced by {member.mention}. Congrats!",inline=False)

    max_points = 0
    max_points_user = ''
    current_general = 'None'

    for user in server_list:
        if server_list[user]['general'] == 1:
            current_general = user

    for user in server_list:
        if (server_list[user]['c_rank_points'] > max_points):
            max_points = server_list[user]['c_rank_points']
            max_points_user = user

    server_list[max_points_user]['general'] = 1

    if current_general == 'None':
        role = discord.utils.get(guild.roles, name='General')
        member = await guild.fetch_member(max_points_user)
        await member.add_roles(role)
        response_msg.add_field(name="general:", value=f"A new general role (highest rank in server) has been assigned to {member.mention}. Congrats!",inline=False)
    elif current_general == max_points_user:
        response_msg.add_field(name="general:", value=f"general is the same as before.",inline=False)
    else:
        role = discord.utils.get(guild.roles, name='General')
        member = await guild.fetch_member(current_general)
        await member.remove_roles(role)
        server_list[current_general]['general'] = 0
        member = await guild.fetch_member(max_points_user)
        await member.add_roles(role)
        response_msg.add_field(name="general:", value=f"Previous general (highest rank in server) has been replaced by {member.mention}. Congrats!",inline=False)

    response_msg.add_field(name="Finished:",
        value=f"Roles and ranks have been synced.",inline=False)
    await channel.send(embed=response_msg)


    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

client.run(bot_token)