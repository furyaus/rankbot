# RankedBot.py
# Version: 0.1
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
import time
import os

client = commands.Bot(command_prefix=".")
client.remove_command("help")

# Global variables
curr_season = "division.bro.official.pc-2018-12"
prev_season = "division.bro.official.pc-2018-11"
prev_prev_season = "division.bro.official.pc-2018-10"

bot_token = os.environ['discord_token']
API_key = os.environ['API_key']

#Keys in order - furyaus, ocker, p4, 
keys = ["Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzNTgyZDhlMC1iM2I1LTAxMzktOGY0YS0yZDliOGVkMDhlMTQiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjI0MTY2NDU0LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJhbmtlZGJvdCJ9.1wpVbT-75yeziFq41tjeLWxFbJFI9sK2wcPGSaBOfus", \
"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI3M2QyNTQxMC05MmQ3LTAxMzgtMzkzOC0xYmJkOWE0ZjQyNzEiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTkyNDA1Mjc1LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6ImpsaG9uZXl3b29kLWhvIn0.JwhuAkULPSlRpMof-UZtk_jqbvOjBCPui4dxLOeo7vY",\
"Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJjMTBjY2VhMC1iYzkzLTAxMzktOGZhYy0yZDliOGVkMDhlMTQiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjI1MTQxNjQ1LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6IjEwMXJhbmtlZGJvdGFwIn0.LzURl_ut4004j1ijcOvPq7hixtTGG_KD01ct1S5t_qA"]


header = {
    "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIzNTgyZDhlMC1iM2I1LTAxMzktOGY0YS0yZDliOGVkMDhlMTQiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNjI0MTY2NDU0LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InJhbmtlZGJvdCJ9.1wpVbT-75yeziFq41tjeLWxFbJFI9sK2wcPGSaBOfus",
    "Accept": "application/vnd.api+json"
}

json_file_path = "edited_server_list.json"
with open(json_file_path, 'r') as j:
    server_list = json.loads(j.read())

server_roles = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"]
admin_roles = ["Lil Admins", "Admin", "Useful Admin"]

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
        description="Rank Bot calculates in-game KD and it manages the roles within this discord!"
    )
    help_msg.add_field(name="checkstats:",
                       value=".checkstats <USERNAME> , used to check someone's squad FPP stats, for example "
                             "'.checkstats furyaus'",
                       inline=False)
    help_msg.add_field(name="enlist:",
                       value=".enlist <USERNAME> , links your discord username with your PUBG in-game name, "
                             "for example '.enlist furyaus'. You only have to do this once!",
                       inline=False)
    help_msg.add_field(name="currentrank", value=".currentrank , Gets your current rank", inline=False)
    help_msg.add_field(name="updaterole:", value=".updaterole , Updates your role if your stats have changed",
                       inline=False)
    help_msg.add_field(name="top20", value=".top20 , Top 20 KD", inline=False)
    help_msg.add_field(name="top20ADR:", value=".top20ADR , Top 20 ADR", inline=False)
    await ctx.send(embed=help_msg)

@client.command()
async def checkstats(ctx, user_ign):
    global keys
    global header
    global no_requests
    user = ctx.message.author
    user_id = user.id
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    await ctx.send(f"Fetching {user_ign}'s current Ranked Squad-FPP Stats:")
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
    initial_r = requests.get(url, headers=curr_header)
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    no_requests += 1
    if initial_r.status_code != 200:
        await ctx.send(
            "Wrong username (capitals in username matters) or too many requests made to the PUBG API (only 5 accounts "
            "per minute)")
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
        KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
        season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
        season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
        ADR = round(season_damage/games_played,3)
        new_role = c_rank
        server_list.update({str(user_id): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
        server_list[str(user_id)]['c_rank'] = c_rank
        server_list[str(user_id)]['c_rank_points'] = c_rank_points
        server_list[str(user_id)]['h_rank'] = h_rank
        server_list[str(user_id)]['h_rank_points'] = h_rank_points
        server_list[str(user_id)]['total_kills'] = h_rank
        server_list[str(user_id)]['season_wins'] = season_wins
        server_list[str(user_id)]['KDA'] = KDA
        server_list[str(user_id)]['ADR'] = ADR
        server_list[str(user_id)]['Punisher'] = 0
        server_list[str(user_id)]['Terminator'] = 0
        server_list[str(user_id)]['team_killer'] = 0

        await ctx.send(f"{user_ign}'s ranked stats:\nCurrent rank is: {c_rank}: {c_rank_points}\nHighest rank is: {h_rank}: {h_rank_points}")
        if c_rank_points < 1000:
            await ctx.send(f"{user_ign}'s Role = Bronze")
        elif c_rank == "Silver":
            await ctx.send(f"{user_ign}'s Role = Silver")
        elif c_rank == "Gold":
            await ctx.send(f"{user_ign}'s Role = Gold")
        elif c_rank == "Platinum":
            await ctx.send(f"{user_ign}'s Role = Platinum")
        elif c_rank == "Diamond":
            await ctx.send(f"{user_ign}'s Role = Diamond")
        else:
            await ctx.send(f"{user_ign}'s Role = Master")

        role = discord.utils.get(ctx.guild.roles, name=new_role)
        await user.add_roles(role)
        with open("edited_server_list.json", "w") as data_file:
           json.dump(server_list, data_file, indent=2)

@client.command(pass_context=True)
async def currentrank(ctx):
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send("Your current rank is: " + server_list[str(user_id)]['Rank'])
    else:
        await ctx.send("You currently don't have a rank")

@client.command(pass_context=True)
async def enlist(ctx, user_ign):
    global keys
    global header
    global no_requests
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send("Your IGN has already been added to the list, just use .updaterole to update your role")
    else:
        await ctx.send("...Linking your IGN to your discord...")
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
            KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
            season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
            season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
            ADR = round(season_damage/games_played,3)

            new_role = c_rank

            server_list.update({str(user_id): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
            server_list[str(user_id)]['c_rank'] = c_rank
            server_list[str(user_id)]['c_rank_points'] = c_rank_points
            server_list[str(user_id)]['h_rank'] = h_rank
            server_list[str(user_id)]['h_rank_points'] = h_rank_points
            server_list[str(user_id)]['total_kills'] = h_rank
            server_list[str(user_id)]['season_wins'] = season_wins
            server_list[str(user_id)]['KDA'] = KDA
            server_list[str(user_id)]['ADR'] = ADR
            server_list[str(user_id)]['Punisher'] = 0
            server_list[str(user_id)]['Terminator'] = 0
            server_list[str(user_id)]['team_killer'] = 0
            await ctx.send("You have been enlisted into the server and your current rank is: " + new_role)
            role = discord.utils.get(ctx.guild.roles, name=new_role)
            await user.add_roles(role)
            with open("edited_server_list.json", "w") as data_file:
                json.dump(server_list, data_file, indent=2)


@client.command(pass_context=True)
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def changeign(ctx, member: discord.Member, user_ign):
    global keys
    global header
    global no_requests
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    user_id = str(member.id)
    await ctx.send(f"...Changing {str(member)}'s IGN on the list...")
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_ign
    initial_r = requests.get(url, headers=curr_header)
    no_requests += 1
    if initial_r.status_code != 200:
        await ctx.send(
            "Wrong username (capitals in username matters) or the PUBG API is down or too many people are trying to "
            "enlist at the same time (maximum of 5 per minute)")
    else:
        curr_rank = server_list[str(member.id)]['Rank']
        try:
            if curr_rank != 'Bronze':
                role = discord.utils.get(ctx.guild.roles, name=curr_rank)
                await member.remove_roles(role)

            if server_list[str(member.id)]['Punisher'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='Punisher')
                await member.remove_roles(role)

            if server_list[str(member.id)]['Terminator'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='Terminator')
                await member.remove_roles(role)

            if server_list[str(member.id)]['team_killer'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
                await member.remove_roles(role)
        except Exception as e:
            print(str(e))

        player_info = json.loads(initial_r.text)
        del server_list[str(member.id)]
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

        new_role = c_rank

        server_list.update({str(user_id): {'IGN': user_ign, 'ID': player_id, 'Rank': new_role}})
        server_list[str(user_id)]['c_rank'] = c_rank
        server_list[str(user_id)]['c_rank_points'] = c_rank_points
        server_list[str(user_id)]['h_rank'] = h_rank
        server_list[str(user_id)]['h_rank_points'] = h_rank_points
        server_list[str(user_id)]['Punisher'] = 0
        server_list[str(user_id)]['Terminator'] = 0
        server_list[str(user_id)]['team_killer'] = 0
        await ctx.send("You have updated your IGN and your current rank is: " + new_role)

        with open("edited_server_list.json", "w") as data_file:
            json.dump(server_list, data_file, indent=2)

@client.command()
async def updaterole(ctx):
    global keys
    global header
    global no_requests
    curr_header = header
    curr_header['Authorization'] = keys[no_requests % (len(keys))]
    id = client.get_guild(859316578994487306)  # Shadows
    # Rank bot announcements channel:
    channel = client.get_channel(859442603984683099)
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
        new_role = c_rank

        server_list[str(user_id)]['c_rank'] = c_rank
        server_list[str(user_id)]['c_rank_points'] = c_rank_points
        server_list[str(user_id)]['h_rank'] = h_rank
        server_list[str(user_id)]['h_rank_points'] = h_rank_points
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
                await ctx.send("There was an error changing your rank " + str(e))  # if error
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


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getteamkiller(ctx):
    await ctx.send("Calculating who should get the team-killer role....")
    id = client.get_guild(859316578994487306)  # Shadows
    # Rank bot announcements channel:
    channel = client.get_channel(859442603984683099)
    max_team_kills = 0
    max_team_kills_user = ''
    current_team_killer = 'None'
    # Find the current DUMBASS
    for user in server_list:
        if server_list[user]['team_killer'] == 1:
            current_team_killer = user

    for user in server_list:
        if server_list[user]['team_kills'] > max_team_kills:
            max_team_kills = server_list[user]['team_kills']
            max_team_kills_user = user

    server_list[max_team_kills_user]['team_killer'] = 1

    if current_team_killer == 'None':
        # No Existing Team Killer
        role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
        member = discord.utils.get(id.members, id=int(max_team_kills_user))
        await member.add_roles(role)
        await channel.send(
            f"A new DUMBASS role has been assigned to {member.mention}, for the most teamkills this season")
    elif current_team_killer == max_team_kills_user:
        # Terminator hasn't changed
        await channel.send("DUMBASS is the same as before!!")
    else:
        # Brand New DUMBASS
        role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
        member = discord.utils.get(id.members, id=int(current_team_killer))
        await member.remove_roles(role)
        server_list[current_team_killer]['team_killer'] = 0
        member = discord.utils.get(id.members, id=int(max_team_kills_user))
        await member.add_roles(role)
        await channel.send(
            f"Previous DUMBASS has been replaced by {member.mention}, with "
            f"{server_list[max_team_kills_user]['team_kills']} teamkills this season")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def updatestats(ctx):
    # Update server list JSON with everyone's stats
    await ctx.send("Updating everyone's stats")
    # Making a request based on 10 players at a time
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
                # add/update their KD
                curr_user = curr_request_list_users[i]
                server_list[curr_user]['KD'] = round(player_kd, 4)
                server_list[curr_user]['ADR'] = round(player_adr, 2)
                server_list[curr_user]['team_kills'] = team_kills
            # Reset variables
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
    id = client.get_guild(859316578994487306)  # Shadows
    # Rank bot announcements channel:
    channel = client.get_channel(859442603984683099)
    max_kd = 0
    max_kd_user = ''
    current_terminator = 'None'
    # Find the current Terminator
    for user in server_list:
        if server_list[user]['Terminator'] == 1:
            current_terminator = user

    for user in server_list:
        if (server_list[user]['KD'] > max_kd) and (server_list[user]['Rank'] != "Bronze"):
            max_kd = server_list[user]['KD']
            max_kd_user = user

    server_list[max_kd_user]['Terminator'] = 1

    if current_terminator == 'None':
        # No Existing Terminator
        role = discord.utils.get(ctx.guild.roles, name='Terminator')
        member = discord.utils.get(id.members, id=int(max_kd_user))
        await member.add_roles(role)
        await channel.send(f"A new Terminator role has been assigned to {member.mention}. Congrats!!")
    elif current_terminator == max_kd_user:
        # Terminator hasn't changed
        await channel.send("Terminator is the same as before!!")
    else:
        # Brand New Terminator
        role = discord.utils.get(ctx.guild.roles, name='Terminator')
        member = discord.utils.get(id.members, id=int(current_terminator))
        await member.remove_roles(role)
        server_list[current_terminator]['Terminator'] = 0
        member = discord.utils.get(id.members, id=int(max_kd_user))
        await member.add_roles(role)
        await channel.send(f"Previous Terminator has been replaced by {member.mention}. Congrats!!")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
@commands.has_any_role(admin_roles[0], admin_roles[1], admin_roles[2])
async def getpunisher(ctx):
    await ctx.send("Calculating who should get the Punisher role....")
    id = client.get_guild(859316578994487306)  # Shadows
    # Rank bot announcements channel:
    channel = client.get_channel(859442603984683099)
    max_adr = 0
    max_adr_user = ''
    current_punisher = 'None'

    # Find the current Punisher
    for user in server_list:
        if server_list[user]['Punisher'] == 1:
            current_punisher = user

    for user in server_list:
        if (server_list[user]['ADR'] > max_adr) and (server_list[user]['Rank'] != "Bronze"):
            max_adr = server_list[user]['ADR']
            max_adr_user = user

    server_list[max_adr_user]['Punisher'] = 1

    if current_punisher == 'None':
        # No Existing Punisher
        role = discord.utils.get(ctx.guild.roles, name='Punisher')
        member = discord.utils.get(id.members, id=int(max_adr_user))
        await member.add_roles(role)
        await channel.send(f"A new Punisher role (Highest ADR) has been assigned to {member.mention}. Congrats!!")
    elif current_punisher == max_adr_user:
        # Punisher hasn't changed
        print("Punisher is the same as before!!")
        # await channel.send("Punisher is the same as before!!")
    else:
        # Brand New Punisher
        role = discord.utils.get(ctx.guild.roles, name='Punisher')
        member = discord.utils.get(id.members, id=int(current_punisher))
        await member.remove_roles(role)
        server_list[current_punisher]['Punisher'] = 0
        member = discord.utils.get(id.members, id=int(max_adr_user))
        await member.add_roles(role)
        await channel.send(f"Previous Punisher has been replaced by {member.mention}. Congrats!!")
        new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
        await channel.send("Top 5 ADR in this server (with more than 100 games this season):")
        top_5_string = ''
        total_length = len(new_server_list)
        i = -1
        j = 1  # Shadows
        while i > -(total_length - 1):
            ign = new_server_list[i]['IGN']
            player_adr = new_server_list[i]['ADR']
            if new_server_list[i]['Rank'] != "Bronze":
                curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), ign, player_adr)
                top_5_string += curr_line
                j += 1

            if j == 6:
                break
            # await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
            i -= 1

        await channel.send(top_5_string)

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


@client.command()
async def top5adr(ctx):
    new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
    await ctx.send("Top 5 ADR in this server (with more than 100 games this season):")
    top_5_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1  # Shadows
    while i > -(total_length - 1):
        ign = new_server_list[i]['IGN']
        player_adr = new_server_list[i]['ADR']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), ign, player_adr)
            top_5_string += curr_line
            j += 1

        if j == 6:
            break
        # await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i -= 1

    await ctx.send(top_5_string)


@client.command()
async def top20adr(ctx):
    new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
    await ctx.send("Top 20 ADR in this server (with more than 100 games this season):")
    top_20_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1  # Shadows
    while i > -(total_length - 1):
        ign = new_server_list[i]['IGN']
        player_adr = new_server_list[i]['ADR']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), ign, player_adr)
            top_20_string += curr_line
            j += 1

        if j == 21:
            break
        # await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i -= 1

    await ctx.send(top_20_string)


@client.command()
async def top20(ctx):
    # await ctx.send('Calculating top 20 (give me a min).....')
    new_server_list = sorted(server_list.values(), key=itemgetter('KD'))
    await ctx.send("Top 20 Sweats in this server (with more than 100 games this season):")
    top_20_string = ''
    i = -1
    total_length = len(new_server_list)
    j = 1  # Shadows
    while i > -(total_length - 1):
        ign = new_server_list[i]['IGN']
        player_kd = new_server_list[i]['KD']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, KD = %.3f\n" % (abs(j), ign, player_kd)
            top_20_string += curr_line
            j += 1

        if j == 21:
            break
        # await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i -= 1

    await ctx.send(top_20_string)

@client.command()
async def top20announce(ctx):
    channel = client.get_channel(859442603984683099)
    new_server_list = sorted(server_list.values(), key=itemgetter('KD'))
    await channel.send("Top 20 Sweats in this server (with more than 100 games this season):")
    top_20_string = ''
    i = -1
    total_length = len(new_server_list)
    j = 1  # Shadows
    while i > -(total_length - 1):
        ign = new_server_list[i]['IGN']
        player_kd = new_server_list[i]['KD']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, KD = %.3f\n" % (abs(j), ign, player_kd)
            top_20_string += curr_line
            j += 1

        if j == 21:
            break
        # await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i -= 1

    await channel.send(top_20_string)

client.run(bot_token)
