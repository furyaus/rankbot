# RankedBot
# Version: 0.9
# Date: 30.06.21
# Current Authors: fury#1662, coopzr#3717, Jobelerno#7978
# Github: https://github.com/furyaus/rankbot
# Repl.it: https://replit.com/@furyaus/rankbot
# Original Author: Mazun19 from the PUBG community
# Original Date: 2019

import discord
from discord.ext import commands
from operator import itemgetter
import requests
import json
import time
import os

client = commands.Bot(command_prefix=".")
client.remove_command("help")

# Global variables
curr_season = "division.bro.official.pc-2018-12"
prev_season = "division.bro.official.pc-2018-11"
prev_prev_season = "division.bro.official.pc-2018-10"

bot_token = os.environ['discord_token']
API_key_fury = os.environ['API_key_fury']
API_key_ocker = os.environ['API_key_ocker']
API_key_p4 = os.environ['API_key_p4']

#Keys in order - furyaus, ocker, p4, 
keys = ["Bearer "+API_key_fury,"Bearer "+API_key_ocker,"Bearer "+API_key_p4]


header = {
    "Authorization": "Bearer "+API_key_fury,
    "Accept": "application/vnd.api+json"
}

json_file_path = "edited_server_list.json"
with open(json_file_path, 'r') as j:
    server_list = json.loads(j.read())

server_roles = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"]
admin_roles = ["Mods", "Admin", "Boss"]

no_requests = 0
curr_key = 0

@client.event
async def on_ready():
    print("Bot is ready.")

@client.command(pass_context=True)
async def help(ctx):
    help_msg = discord.Embed(
        colour=discord.Colour.red(),
        title="Help for Rank Bot",
        description="Rank Bot calculates in-game KD and it manages the roles within this discord!")
    help_msg.add_field(name="checkstats:", value=".checkstats <USERNAME> , used to check someone's squad FPP stats, for example '.checkstats furyaus'", inline=False)
    help_msg.add_field(name="enlist:", value=".enlist <USERNAME> , links your discord username with your PUBG in-game name, You only have to do this once!",inline=False)
    help_msg.add_field(name="updaterole:", value=".updaterole , Updates your role if your stats have changed", inline=False)
    help_msg.add_field(name="top20", value=".top20 , Top 20 KD", inline=False)
    help_msg.add_field(name="top20ADR:", value=".top20ADR , Top 20 ADR", inline=False)
    await ctx.send(embed=help_msg)

@client.command(pass_context=True)
async def adminhelp(ctx):
    help_msg = discord.Embed(
        colour=discord.Colour.red(),
        title="Admin Help for Rank Bot",
        description="Rank Bot calculates in-game KD and it manages the roles within this discord!")
    help_msg.add_field(name="total enlisted:", value=".totalenlisted will return the total number of currently stored players", inline=False)
    help_msg.add_field(name="remove user:", value=".removeuser <USERNAME> , will allow someone to re-enlist to fix issues", inline=False)
    help_msg.add_field(name="team killer", value=".getteamkiller, finds the player with largest number of team kills", inline=False)
    help_msg.add_field(name="terminator", value=".getterminator, will update top killer", inline=False)
    help_msg.add_field(name="punisher:", value=".getpunisher, will update highest ADR", inline=False)
    await ctx.send(embed=help_msg)

@client.command()
async def checkstats(ctx, user_ign):
    global keys
    global header
    global no_requests
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Rank for "+user_ign,)
    user = ctx.message.author
    user_id = user.id
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
        c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
        h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
        h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
        games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
        team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
        
        new_role = c_rank
        ADR = round(season_damage/games_played,0)
        KDA = round(KDA,2)
        server_list.update({str(user_id): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
        server_list[str(user_id)]['c_rank'] = c_rank
        server_list[str(user_id)]['c_rank_points'] = c_rank_points
        server_list[str(user_id)]['h_rank'] = h_rank
        server_list[str(user_id)]['h_rank_points'] = h_rank_points
        server_list[str(user_id)]['games_played'] = games_played
        server_list[str(user_id)]['team_kills'] = team_kills
        server_list[str(user_id)]['season_wins'] = season_wins
        server_list[str(user_id)]['KDA'] = KDA
        server_list[str(user_id)]['ADR'] = ADR
        server_list[str(user_id)]['Punisher'] = 0
        server_list[str(user_id)]['Terminator'] = 0
        server_list[str(user_id)]['team_killer'] = 0
        
        response_msg.add_field(name="Rank:",
            value=f"Current rank is: {c_rank}: {c_rank_points}\nHighest rank is: {h_rank}: {h_rank_points}",inline=False)
        response_msg.add_field(name="KDA:",
            value=f"Kills and assists per death: {KDA}",inline=False)
        response_msg.add_field(name="ADR:",
            value=f"Average damage per game: {ADR}",inline=False)

        await ctx.send(embed=response_msg)

@client.command(pass_context=True)
async def enlist(ctx, user_ign):
    global keys
    global header
    global no_requests
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Rank for "+user_ign,
    )
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send("Your IGN has already been added to the list, just use .updaterole to update your role")
    else:
        url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
        initial_r = requests.get(url, headers=curr_header)
        no_requests += 1
        if initial_r.status_code != 200:
            await ctx.send(
                "Wrong username (capitals in username matters) or the PUBG API is down or too many people are trying "
                "to enlist at the same time (maximum of 5 per minute)")
        else:
            player_info = json.loads(initial_r.text)
            player_id = player_info['data'][0]['id'].replace('account.', '')
            season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
            curr_header['Authorization'] = keys[no_requests % (len(keys))]
            second_request = requests.get(season_url, headers=curr_header)
            no_requests += 1
            season_info = json.loads(second_request.text)
            c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
            c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
            h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
            h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
            games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
            team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
            KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
            season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
            season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']

            new_role = c_rank
            ADR = round(season_damage/games_played,0)
            KDA = round(KDA,2)
            server_list.update({str(user_id): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
            server_list[str(user_id)]['c_rank'] = c_rank
            server_list[str(user_id)]['c_rank_points'] = c_rank_points
            server_list[str(user_id)]['h_rank'] = h_rank
            server_list[str(user_id)]['h_rank_points'] = h_rank_points
            server_list[str(user_id)]['games_played'] = games_played
            server_list[str(user_id)]['team_kills'] = team_kills
            server_list[str(user_id)]['season_wins'] = season_wins
            server_list[str(user_id)]['KDA'] = KDA
            server_list[str(user_id)]['ADR'] = ADR
            server_list[str(user_id)]['Punisher'] = 0
            server_list[str(user_id)]['Terminator'] = 0
            server_list[str(user_id)]['team_killer'] = 0

            await ctx.send("You have been enlisted into the server and your current rank is: " + new_role)
            role = discord.utils.get(ctx.guild.roles, name=new_role)
            await user.add_roles(role)

            response_msg.add_field(name="Rank:", value=f"Current rank is: {c_rank}: {c_rank_points}\nHighest rank is: {h_rank}: {h_rank_points}",inline=False)
            response_msg.add_field(name="KDA:", value=f"Kills and assists per death: {KDA}",inline=False)
            response_msg.add_field(name="ADR:", value=f"Average damage per game: {ADR}",inline=False)

            await ctx.send(embed=response_msg)
            with open("edited_server_list.json", "w") as data_file:
                json.dump(server_list, data_file, indent=2)


@client.command()
async def updaterole(ctx):
    global keys
    global header
    global no_requests
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        curr_rank = server_list[str(user_id)]['Rank']
        await ctx.send("Your current rank is: " + server_list[str(user_id)]['Rank'])
        player_id = server_list[str(user_id)]['ID']
        season_url = "https://api.pubg.com/shards/steam/players/" + "account." + player_id + "/seasons/" + curr_season + "/ranked"
        second_request = requests.get(season_url, headers=curr_header)
        no_requests += 1
        season_info = json.loads(second_request.text)
        c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
        c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
        h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
        h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
        games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
        team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']

        new_role = c_rank
        ADR = round(season_damage/games_played,0)
        KDA = round(KDA,2)
        server_list[str(user_id)]['c_rank'] = c_rank
        server_list[str(user_id)]['c_rank_points'] = c_rank_points
        server_list[str(user_id)]['h_rank'] = h_rank
        server_list[str(user_id)]['h_rank_points'] = h_rank_points
        server_list[str(user_id)]['games_played'] = games_played
        server_list[str(user_id)]['team_kills'] = team_kills
        server_list[str(user_id)]['season_wins'] = season_wins
        server_list[str(user_id)]['KDA'] = KDA
        server_list[str(user_id)]['ADR'] = ADR
        server_list[str(user_id)]['Punisher'] = 0
        server_list[str(user_id)]['Terminator'] = 0
        server_list[str(user_id)]['team_killer'] = 0

        if new_role == curr_rank:
            await ctx.send("Your rank is the same as before")
        else:
            try:
                await user.add_roles(discord.utils.get(ctx.guild.roles, name=new_role))
                server_list[str(user_id)]['Rank'] = new_role
                await ctx.send("Your rank has been updated!")
            except Exception as e:
                await ctx.send("There was an error changing your rank " + str(e))
    else:
        await ctx.send(
            "You currently don't have a rank and your IGN isn't added to the list so use .enlist command to enlist")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
async def totalenlisted(ctx):
    await ctx.send(f"There are currently {len(server_list)} people enlisted in this server!")


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def removeuser(ctx, member: discord.Member):
    await ctx.send(f"Removing {str(member)} from the list..")
    del server_list[str(member.id)]
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def updatestats(ctx):
    await ctx.send("Updating everyone's stats")
    no_of_players = 0
    total_additions = 0
    curr_request_list = []
    curr_request_list_users = []
    total_api_requests = 0
    curr_header = header
    for user in server_list:
        player_id = server_list[user]['ID']
        curr_request_list.append(player_id)
        curr_request_list_users.append(user)
        no_of_players += 1
        total_additions += 1
        if no_of_players == 10 or total_additions == len(server_list):
            player_id_list = ','.join(curr_request_list)
            season_url = "https://api.pubg.com/shards/steam/seasons/" + curr_season + "/gameMode/squad-fpp/players?filter[playerIds]=" + "account."+ player_id_list
            second_request = requests.get(season_url, headers=curr_header)
            total_api_requests += 1
            if total_api_requests == 10:
                await ctx.send("10 Requests per min reached waiting for a minute")
                time.sleep(60)
                total_api_requests = 0

            if second_request.status_code == 429:
                await ctx.send("Too MANY REQUESTS")
            season_info = json.loads(second_request.text)
            for i in range(0, len(season_info['data'])):
                games_played = season_info['data'][i]['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
                total_losses = season_info['data'][i]['attributes']['rankedGameModeStats']['squad-fpp']['losses']
                total_kills = season_info['data'][i]['attributes']['rankedGameModeStats']['squad-fpp']['kills']
                season_damage = season_info['data'][i]['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
                team_kills = season_info['data'][i]['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
                player_adr = season_damage / games_played
                player_kd = total_kills / total_losses
                curr_user = curr_request_list_users[i]
                server_list[curr_user]['KD'] = round(player_kd, 4)
                server_list[curr_user]['ADR'] = round(player_adr, 2)
                server_list[curr_user]['team_kills'] = team_kills
            no_of_players = 0
            curr_request_list = []
            curr_request_list_users = []

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

    await ctx.send("Finished Updating the stats")


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getterminator(ctx):
    await ctx.send("Calculating who should get the Terminator role....")
    channel = client.get_channel(859442603984683099)
    max_kda = 0
    max_kda_user = ''
    current_terminator = 'None'
    for user in server_list:
        if server_list[user]['Terminator'] == 1:
            current_terminator = user

    for user in server_list:
        if (server_list[user]['KDA'] > max_kda):
            max_kda = server_list[user]['KDA']
            max_kda_user = user

    server_list[max_kda_user]['Terminator'] = 1

    if current_terminator == 'None':
        role = discord.utils.get(ctx.guild.roles, name='Terminator')
        member = await ctx.guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        await channel.send(f"A new Terminator role (highest KDA) has been assigned to {member.mention}. Congrats!!")
    elif current_terminator == max_kda_user:
        await channel.send("Terminator is the same as before!!")
    else:
        role = discord.utils.get(ctx.guild.roles, name='Terminator')
        member = await ctx.guild.fetch_member(current_terminator)
        await member.remove_roles(role)
        server_list[current_terminator]['Terminator'] = 0
        member = await ctx.guild.fetch_member(max_kda_user)
        await member.add_roles(role)
        await channel.send(f"Previous Terminator (highest KDA) has been replaced by {member.mention}. Congrats!!")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getpunisher(ctx):
    await ctx.send("Calculating who should get the Punisher role....")
    channel = client.get_channel(859442603984683099)
    max_adr = 0
    max_adr_user = ''
    current_punisher = 'None'

    for user in server_list:
        if server_list[user]['Punisher'] == 1:
            current_punisher = user

    for user in server_list:
        if (server_list[user]['ADR'] > max_adr):
            max_adr = server_list[user]['ADR']
            max_adr_user = user

    server_list[max_adr_user]['Punisher'] = 1

    if current_punisher == 'None':
        role = discord.utils.get(ctx.guild.roles, name='Punisher')
        member = await ctx.guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        await channel.send(f"A new Punisher role (highest ADR) has been assigned to {member.mention}. Congrats!!")
    elif current_punisher == max_adr_user:
        await channel.send("Punisher is the same as before!!")
    else:
        role = discord.utils.get(ctx.guild.roles, name='Punisher')
        member = await ctx.guild.fetch_member(current_punisher)
        await member.remove_roles(role)
        server_list[current_punisher]['Punisher'] = 0
        member = await ctx.guild.fetch_member(max_adr_user)
        await member.add_roles(role)
        await channel.send(f"Previous Punisher (highest ADR) has been replaced by {member.mention}. Congrats!!")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getteamkiller(ctx):
    await ctx.send("Calculating who should get the team-killer role....")
    id = client.get_guild(859316578994487306)
    channel = client.get_channel(859442603984683099)
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
        await channel.send("No one has any team kills!!")
    elif current_team_killer == 'None':
        role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
        member = discord.utils.get(id.members, id=int(max_team_kills_user))
        member = await ctx.guild.fetch_member(max_team_kills_user)
        await member.add_roles(role)
        await channel.send(f"A new DUMBASS role has been assigned to {member.mention}, for the most teamkills this season")
    elif current_team_killer == max_team_kills_user:
        await channel.send("DUMBASS is the same as before!!")
    else:
        role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
        member = await ctx.guild.fetch_member(current_team_killer)
        await member.remove_roles(role)
        server_list[current_team_killer]['team_killer'] = 0
        member = await ctx.guild.fetch_member(max_team_kills_user)
        await member.add_roles(role)
        await channel.send(
            f"Previous DUMBASS has been replaced by {member.mention}, with "
            f"{server_list[max_team_kills_user]['team_kills']} teamkills this season")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
async def top20adr(ctx):
    channel = client.get_channel(859442603984683099)
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Top 20 ADR in this server",)
    new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
    top_20_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1
    while i > -(total_length+1):
        ign = new_server_list[i]['IGN']
        player_adr = new_server_list[i]['ADR']
        curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), ign, player_adr)
        top_20_string += curr_line
        j += 1
        if j == 21:
            break
        i -= 1
    response_msg.add_field(name="Top ADR:", value=top_20_string,inline=False)
    await channel.send(embed=response_msg)


@client.command()
async def top20ranks(ctx):
    channel = client.get_channel(859442603984683099)
    new_server_list = sorted(server_list.values(), key=itemgetter('c_rank_points'))
    response_msg = discord.Embed(
      colour=discord.Colour.red(),
      title="Top 20 Rank holders in this server",)
    top_20_string = ''
    i = -1
    total_length = len(new_server_list)
    j = 1 
    while i > -(total_length+1):
        ign = new_server_list[i]['IGN']
        player_rank = round(new_server_list[i]['c_rank_points'],0)
        curr_line = "%i : %s, Rank Points = %.3f\n" % (abs(j), ign, player_rank)
        top_20_string += curr_line
        j += 1
        if j == 21:
            break
        i -= 1
    response_msg.add_field(name="Top rank holders:", value=top_20_string,inline=False)
    await channel.send(embed=response_msg)

client.run(bot_token)