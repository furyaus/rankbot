
# RankedBot.py
# Version: 0.1
# Date: 29.06.21
# Github: https://github.com/furyaus/rankbot
# Repl.it: https://replit.com/@furyaus/rankbot

import discord
import os
import requests
import json

from discord.ext import commands, tasks
from operator import itemgetter
from discord.utils import get
import time

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

#Global variables
curr_season = "division.bro.official.pc-2018-07"
prev_season = "division.bro.official.pc-2018-06"
prev_prev_season = "division.bro.official.pc-2018-03"

bot_token = os.environ['discord_token']
API_key = os.environ['API_key']

keys = API_key
header = bot_token

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

@client.event
async def on_message(message):
  if message.content.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)


json_file_path = "edited_server_list.json"

with open(json_file_path, 'r') as j:
     server_list = json.loads(j.read())


server_roles = ["Bronze", "Silver", "Gold", "Platinum", "Diamond", "Master"]

no_requests = 0
curr_key = 0

@client.event
async def on_ready():
    updateEverything.start()
    print('Bot is ready.')

@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    help_msg = discord.Embed(
        colour=discord.Colour.red(),
        title="Help for Rank Bot",
        description="Rank Bot calculates in-game KD and it manages the roles within this discord!"
    )
    help_msg.add_field(name="checkstats:", value=".checkstats <USERNAME> , used to check someone's squad FPP stats, for example \".checkstats Deboxx\"", inline=False)
    help_msg.add_field(name="checkmystats:", value=".checkmystats, used to check your own squad FPP stats, for example \".checkmystats\"", inline=False)
    help_msg.add_field(name="enlist:", value=".enlist <USERNAME> , links your discord username with your PUBG in-game name, for example \".enlist furyaus\". You only have to do this once!", inline=False)
    help_msg.add_field(name="currentrank", value=".currentrank , Gets your current rank", inline=False)
    help_msg.add_field(name="updaterole:", value=".updaterole , Updates your role if your stats have changed", inline=False)
    help_msg.add_field(name="top20:", value=".top20 , Top 20 KD", inline=False)
    help_msg.add_field(name="top20ADR:", value=".top20ADR , Top 20 ADR", inline=False)
    await ctx.send(embed=help_msg)

@client.command()   
async def checkstats(ctx, Username):
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    await ctx.send(f'Checking {Username}\'s Squad-FPP stats:')
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + Username
    initial_r = requests.get(url, headers=curr_header)
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    no_requests = no_requests + 1
    if initial_r.status_code != 200:
        await ctx.send('Wrong username (captials in username matters) or too many requests made to the PUBG API (only 5 accounts per minute)')
    else:  
        player_info = json.loads(initial_r.text)
        #First get the ID:
        player_ID = player_info['data'][0]['id'].replace('account.','')

        #Retreive the season data and calculate KD
        season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + curr_season
        second_request = requests.get(season_url, headers=curr_header)
        curr_header["Authorization"] = keys[no_requests%(len(keys))]
        no_requests = no_requests + 1
        season_info = json.loads(second_request.text)
        games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
        total_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['kills']
        season_wins = season_info['data']['attributes']['gameModeStats']['squad-fpp']['wins']
        season_losses = season_info['data']['attributes']['gameModeStats']['squad-fpp']['losses']
        season_damage = season_info['data']['attributes']['gameModeStats']['squad-fpp']['damageDealt']
        recent_matches = season_info['data']['relationships']['matchesSquadFPP']['data']

        if len(recent_matches) == 0:
            await ctx.send('You haven\'t played a Squad FPP game in the last 14 days so you will be demoted to Bronze, either ask admin to enlist a different account or play some games to get your proper rank!!')
        else:
            if season_losses == 0:
                    tru_KD = total_kills
            else:
                tru_KD = total_kills/season_losses
                ADR = round(season_damage/games_played,3)
                #GG_KD = total_kills/(games_played - season_wins)
                await ctx.send(f'{Username}\'s Stats:\nIn-Game KD is: {round(tru_KD,2)}')
                await ctx.send(f'ADR = {ADR}')
                if games_played < 50:
                    await ctx.send('You have played less than 100 games this season, so you only get Bronze role')
                    await ctx.send(f'Play {50-games_played} more games this season to get your proper role!!')
                else:
                    if ADR < 225:
                        await ctx.send(f'{Username}\'s doesn\'t belong in this server!!')
                    elif ADR < 300:
                        await ctx.send(f'{Username}\'s Role = Bronze')
                    elif ADR < 350:  
                        await ctx.send(f'{Username}\'s Role = Silver')
                    elif ADR < 400:
                        await ctx.send(f'{Username}\'s Role = Gold')
                    elif ADR < 450:
                        await ctx.send(f'{Username}\'s Role = Platinum')
                    elif ADR < 500:
                        await ctx.send(f'{Username}\'s Role = Diamond')
                    else:
                        await ctx.send(f'{Username}\'s Role = Master')

@client.command()   
async def checkmystats(ctx):
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send(f'Checking {user}\'s Squad-FPP stats:')
        player_ID = server_list[str(user_id)]['ID']
        #Retreive the season data and calculate KD
        season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + curr_season
        second_request = requests.get(season_url, headers=curr_header)
        no_requests = no_requests + 1
        season_info = json.loads(second_request.text)
        games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
        total_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['kills']
        season_wins = season_info['data']['attributes']['gameModeStats']['squad-fpp']['wins']
        season_losses = season_info['data']['attributes']['gameModeStats']['squad-fpp']['losses']
        season_damage = season_info['data']['attributes']['gameModeStats']['squad-fpp']['damageDealt']
        recent_matches = season_info['data']['relationships']['matchesSquadFPP']['data']
        if len(recent_matches) == 0:
            await ctx.send('You haven\'t played a Squad FPP game in the last 14 days so you will be demoted to Bronze, either ask admin to enlist a different account or play some games to get your proper rank!!')  
        else:
            if season_losses == 0:
                    tru_KD = total_kills
            else:
                tru_KD = total_kills/season_losses
                GG_KD = total_kills/(games_played - season_wins)
                ADR = round(season_damage/games_played,3)
                await ctx.send(f"{str(user)[:-5]}\'s Stats:\nIn-Game KD is: {round(tru_KD,4)}\nOP-GG KD is: {round(GG_KD,4)}")
                await ctx.send(f'ADR = {ADR}')
                server_list[str(user_id)]['KD'] = round(tru_KD,4)
                server_list[str(user_id)]['ADR'] = ADR
                if games_played < 50:
                    await ctx.send('You have played less than 100 games this season, so you only get Bronze role')
                    await ctx.send(f'Play {100-games_played} more games this season to get your proper role!!')
                else:
                    if ADR < 250:
                        await ctx.send(f'{str(user)[:-5]}\'s doesn\'t belong in this server!!')
                    elif ADR < 300:
                        await ctx.send(f'{str(user)[:-5]}\'s Role = Bronze')
                    elif ADR < 350:  
                        await ctx.send(f'{str(user)[:-5]}\'s Role = Silver')
                    elif ADR < 400:
                        await ctx.send(f'{str(user)[:-5]}\'s Role = Gold')
                    elif ADR < 450:
                        await ctx.send(f'{str(user)[:-5]}\'s Role = Platinum')
                    elif ADR < 500:
                        await ctx.send(f'{str(user)[:-5]}\'s Role = Diamond')
                    else:
                        await ctx.send(f'{str(user)[:-5]}\'s Role = Master')
            
        with open("edited_server_list.json", "w") as data_file:
            json.dump(server_list, data_file, indent=2)
    else:
        await ctx.send(f"You haven't enlisted yourself to the server list yet!")

@client.command(pass_context=True)
async def currentrank(ctx):
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send('Your current rank is: ' + server_list[str(user_id)]['Rank'])
    else:
        await ctx.send('You currently don\'t have a rank')
        
@client.command(pass_context=True)
async def enlist(ctx,user_IGN):
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        await ctx.send('Your IGN has already been added to the list, just use .updaterole to update your role')
    else: 
        await ctx.send('...Linking your IGN to your discord...')
        url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_IGN
        #Find the player pubg ID:
        initial_r = requests.get(url, headers=curr_header)
        no_requests = no_requests + 1
        if initial_r.status_code != 200:  
            await ctx.send('Wrong username (captials in username matters) or the PUBG API is down or too many people are trying to enlist at the same time (maximum of 5 per minute)')
        else:  
            player_info = json.loads(initial_r.text)
            #First get the ID:
            player_ID = player_info['data'][0]['id'].replace('account.','')
            season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + curr_season
            curr_header["Authorization"] = keys[no_requests%(len(keys))]
            second_request = requests.get(season_url, headers=curr_header)
            no_requests = no_requests + 1
            season_info = json.loads(second_request.text)
            total_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['kills']
            games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
            season_losses = season_info['data']['attributes']['gameModeStats']['squad-fpp']['losses']
            season_damage = season_info['data']['attributes']['gameModeStats']['squad-fpp']['damageDealt']
            team_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['teamKills']
            ADR = round(season_damage/games_played,3)
            if season_losses == 0:
                tru_KD = total_kills
            else:
                tru_KD = total_kills/season_losses

            #You need to have a 2+KD to join the server
            if ADR < 250:
                    await ctx.send(f'Your ADR is: {ADR}')
                    reason = 'Sorry your in-game ADR is less than 250, and you need a 250+ ADR to enter this server'
                    await ctx.send(f'Sorry but you\'ll have to do better to be in here!, {user} will be kicked in 5s')
                    time.sleep(5)
                    await user.send('Sorry your in-game ADR is less than 250, and you need a 250+ KD to enter this server')
                    await user.kick(reason=reason)
            else:
                if games_played < 100:
                    await ctx.send('You have played less than 100 games this season, so you only get Bronze role')
                    await ctx.send(f'Play {100-games_played} more games this season to get your proper role!!')
                    new_role = 'Bronze'
                    role = discord.utils.get(ctx.guild.roles, name=new_role)
                    await user.add_roles(role)
                    #Create the new entry in the dictionary           
                    server_list.update({str(user_id) : {'IGN' : user_IGN, 'ID' : player_ID, 'Rank' : new_role}})
                    server_list[str(user_id)]['KD'] = round(tru_KD,4)
                    server_list[str(user_id)]['ADR'] = round(season_damage/games_played,2)
                    server_list[str(user_id)]['team_kills'] = team_kills
                    server_list[str(user_id)]['Aries'] = 0
                    server_list[str(user_id)]['Zeus'] = 0
                    server_list[str(user_id)]['team_killer'] = 0
                    await ctx.send(f'Your in-Game KD is: {round(tru_KD,2)}')
                    await ctx.send(f'Your ADR = {round(season_damage/games_played,2)}')
                    #write the updated server list
                    with open("edited_server_list.json", "w") as data_file:
                        json.dump(server_list, data_file, indent=2)
                else:
                    if tru_KD < 2.0:
                        new_role = 'Bronze'
                    elif tru_KD < 2.5:
                        new_role = 'Silver'    
                    elif tru_KD < 3.0:
                        new_role = 'Gold'
                    elif tru_KD < 3.5:
                        new_role = 'Platinum'
                    elif tru_KD < 4.0:
                        new_role = 'Diamond'
                    else:
                        new_role = 'Master'

                    #Create the new entry in the dictionary           
                    server_list.update({str(user_id) : {'IGN' : user_IGN, 'ID' : player_ID, 'Rank' : new_role}})
                    server_list[str(user_id)]['KD'] = round(tru_KD,4)
                    server_list[str(user_id)]['ADR'] = round(season_damage/games_played,2)
                    server_list[str(user_id)]['team_kills'] = team_kills
                    server_list[str(user_id)]['Aries'] = 0
                    server_list[str(user_id)]['Zeus'] = 0
                    server_list[str(user_id)]['team_killer'] = 0
                    await ctx.send(f'Your in-Game KD is: {round(tru_KD,2)}')
                    await ctx.send(f'Your ADR = {round(season_damage/games_played,2)}')
                    await ctx.send('You have been enlisted into the server and your current rank is: ' + new_role)
                    role = discord.utils.get(ctx.guild.roles, name=new_role)
                    await user.add_roles(role)
                    #Also assign Bronze role to newcomers
                    if new_role != 'Bronze':
                        role = discord.utils.get(ctx.guild.roles, name='Bronze')
                        await user.add_roles(role)
                    #write the updated server list
                    with open("edited_server_list.json", "w") as data_file:
                        json.dump(server_list, data_file, indent=2)

@client.command(pass_context=True)
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2]) 
async def changeIGN(ctx,member: discord.Member,user_IGN):
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    user_id = str(member.id)
    await ctx.send(f'...Changing {str(member)}''s IGN on the list...')
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + user_IGN
    #Find the player pubg ID:
    initial_r = requests.get(url, headers=curr_header)
    no_requests = no_requests + 1
    if initial_r.status_code != 200:  
        await ctx.send('Wrong username (captials in username matters) or the PUBG API is down or too many people are trying to enlist at the same time (maximum of 5 per minute)')
    else:
        #Remove user's exisitng roles
        curr_rank = server_list[str(member.id)]['Rank']
        try:
            if curr_rank != 'Bronze' :
                role = discord.utils.get(ctx.guild.roles, name=curr_rank)
                await member.remove_roles(role)

            if server_list[str(member.id)]['Aries'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='Aries')
                await member.remove_roles(role)     
            
            if server_list[str(member.id)]['Zeus'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='ZEUS')
                await member.remove_roles(role)

            if server_list[str(member.id)]['team_killer'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
                await member.remove_roles(role)  
        except Exception as e:
            print(str(e))

        player_info = json.loads(initial_r.text)
        del server_list[str(member.id)]
        #First get the ID:
        player_ID = player_info['data'][0]['id'].replace('account.','')
        season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + curr_season
        curr_header["Authorization"] = keys[no_requests%(len(keys))]
        second_request = requests.get(season_url, headers=curr_header)
        no_requests = no_requests + 1
        season_info = json.loads(second_request.text)
        total_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['kills']
        games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
        season_losses = season_info['data']['attributes']['gameModeStats']['squad-fpp']['losses']
        season_damage = season_info['data']['attributes']['gameModeStats']['squad-fpp']['damageDealt']
        team_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['teamKills']
        
        if season_losses == 0:
            tru_KD = total_kills
        else:
            tru_KD = total_kills/season_losses
            if games_played < 100:
                await ctx.send('You have played less than 100 games this season, so you only get Bronze role')
                await ctx.send(f'Play {100-games_played} more games this season to get your proper role!!')
                new_role = 'Bronze'
            else:
                if tru_KD < 1.9:
                    await ctx.send(f'Your in-Game KD is: {round(tru_KD,2)}')
                    await ctx.send(f'This account''s KD is less than 1.9, you cannot link this IGN to ur discord')
                elif tru_KD < 2.0:
                    new_role = 'Bronze'
                elif tru_KD < 2.5:
                    new_role = 'Silver'    
                elif tru_KD < 3.0:
                    new_role = 'Gold'
                elif tru_KD < 3.5:
                    new_role = 'Platinum'
                elif tru_KD < 4.0:
                    new_role = 'Diamond'
                else:
                    new_role = 'Master'
            
            #Only add people with a tru KD of greater than 1.9
            if tru_KD > 1.9:
                #Create the new entry in the dictionary           
                server_list.update({str(user_id) : {'IGN' : user_IGN, 'ID' : player_ID, 'Rank' : new_role}})
                server_list[str(user_id)]['KD'] = round(tru_KD,4)
                server_list[str(user_id)]['ADR'] = round(season_damage/games_played,2)
                server_list[str(user_id)]['team_kills'] = team_kills
                server_list[str(user_id)]['Aries'] = 0
                server_list[str(user_id)]['Zeus'] = 0
                server_list[str(user_id)]['team_killer'] = 0
                await ctx.send(f'Your in-Game KD is: {round(tru_KD,2)}')
                await ctx.send(f'Your ADR = {round(season_damage/games_played,2)}')
                await ctx.send('You have been enlisted into the server and your current rank is: ' + new_role)
                role = discord.utils.get(ctx.guild.roles, name=new_role)
                await member.add_roles(role)
                #write the updated server list
        
        with open("edited_server_list.json", "w") as data_file:
            json.dump(server_list, data_file, indent=2)
            
@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])   
async def updateEveryone(ctx):
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    #Check and update everyone's roles and make announcements on promotions and demotions! 
    id = client.get_guild(180535625034891264)
    #Rank bot annoucements channel:
    channel = client.get_channel(652624968642723850)
    channel2 = client.get_channel(652462920734605317)
    print('Updating everyones stats and roles')
    #await channel.send("Making daily updates to everyone's roles.....")
    #Making a request based on 10 players at a time
    no_of_players = 0
    total_additions = 0
    curr_request_list = []
    curr_request_list_users = []
    less_than_2_list = []
    #total_api_requests  = 0
    promoted_users = []
    demoted_users = []
    inactive_users = []
    kicked_users = []
    for user in server_list:
        player_ID = server_list[user]['ID']
        curr_request_list.append(player_ID)
        curr_request_list_users.append(user)
        no_of_players = no_of_players + 1
        total_additions = total_additions + 1
        if no_of_players == 10 or total_additions == len(server_list):
            player_ID_list = ','.join(curr_request_list)
            season_url = "https://api.pubg.com/shards/steam/seasons/" + curr_season + "/gameMode/squad-fpp/players?filter[playerIds]=" + player_ID_list
            second_request = requests.get(season_url, headers=curr_header)
            no_requests = no_requests + 1
            curr_header["Authorization"] = keys[no_requests%(len(keys))]
            # total_api_requests = total_api_requests + 1
            # if total_api_requests == 10:
            #     print('10 Requests per min reached waiting for a minute')
            #     time.sleep(60)
            #     total_api_requests = 0
            if second_request.status_code == 429:
                print('Too MANY REQUESTS')
                time.sleep(60)
            season_info = json.loads(second_request.text)
            for i in range(0,len(season_info['data'])):
                games_played = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
                total_losses = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['losses']
                total_kills = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['kills']
                season_damage = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['damageDealt']
                team_kills = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['teamKills']
                recent_matches = season_info['data'][i]['relationships']['matchesSquadFPP']['data']
                
                if total_losses == 0:
                    player_KD = total_kills
                    player_ADR = season_damage
                else:
                    player_KD = total_kills/total_losses
                    player_ADR = season_damage/games_played
                
                #add/update their KD and ADR
                curr_user = curr_request_list_users[i]
                server_list[curr_user]['KD'] = round(player_KD,4)
                server_list[curr_user]['ADR'] = round(player_ADR,2)
                server_list[curr_user]['team_kills'] = team_kills
                curr_role = server_list[curr_user]['Rank']
                
                #Check if the user hasn't played a game in the last 14 days and also if they have a higher rank than Bronze
                if (len(recent_matches) == 0) and (curr_role != 'Bronze'):
                    inactive_users.append(curr_user)
                    #await ctx.send('You haven\'t played a Squad FPP game in the last 14 days so you will be demoted to Bronze, either ask admin to enlist a different account or play some games to get your proper rank!!')  
                    member = discord.utils.get(id.members, id=int(curr_user))
                    role = discord.utils.get(ctx.guild.roles, name=curr_role)
                    
                    server_list[curr_user]['KD'] = 0
                    server_list[curr_user]['ADR'] = 0    

                    server_list[curr_user]['Rank'] = 'Bronze'
                    await member.remove_roles(role)
                    #Update the rank in the server list
                    if server_list[str(member.id)]['Aries'] == 1:
                        server_list[curr_user]['Aries'] = 0
                        await member.remove_roles(role)     
                    
                    if server_list[str(member.id)]['Zeus'] == 1:
                        server_list[curr_user]['Zeus'] = 0
                        role = discord.utils.get(ctx.guild.roles, name='ZEUS')
                        await member.remove_roles(role)

                    with open("edited_server_list.json", "w") as data_file:
                        json.dump(server_list, data_file, indent=2)
                        
                elif (len(recent_matches) == 0):
                    member = discord.utils.get(id.members, id=int(curr_user))
                    server_list[curr_user]['KD'] = 0
                    server_list[curr_user]['ADR'] = 0    
                    server_list[curr_user]['Rank'] = 'Bronze'
                else:    
                    if games_played >= 100:
                        #Only change the role of those with more than 100 games
                        if player_KD < 1.9:
                            #Player needs to be kicked
                            try:
                                reason = 'Sorry your in-game KD is less than 1.9, and you need a 2+ KD to re-enter'
                                print(server_list[curr_user]['IGN'])
                                member = discord.utils.get(id.members, id=int(curr_user))
                                await member.send('Sorry your in-game KD is less than 1.9, and you need a 2+ KD to re-enter')
                                await member.kick(reason=reason)
                                kicked_users.append(curr_user)
                            except Exception as e:
                                print('issue:' + str(e))
                        elif player_KD < 2.0:
                            less_than_2_list.append(server_list[curr_user]['IGN'])
                            new_role = 'Bronze'
                        elif player_KD < 2.5:
                            new_role = 'Silver'    
                        elif player_KD < 3.0:
                            new_role = 'Gold'
                        elif player_KD < 3.5:
                            new_role = 'Platinum'
                        elif player_KD < 4.0:
                            new_role = 'Diamond'
                        else:
                            new_role = 'Master'
                        
                        if player_KD > 1.9:
                            #Only promote/demote if their role has changed
                            if new_role != curr_role:
                                try:
                                    member = discord.utils.get(id.members, id=int(curr_user))
                                    await member.add_roles(discord.utils.get(ctx.guild.roles, name=new_role))
                                    server_list[curr_user]['Rank'] = new_role
                                    #Update the rank in the server list
                                    with open("edited_server_list.json", "w") as data_file:
                                        json.dump(server_list, data_file, indent=2)
                                    #Remove old rank
                                    if curr_role != 'Bronze':
                                        await member.remove_roles(discord.utils.get(ctx.guild.roles, name=curr_role))
                                    if server_roles.index(new_role) > server_roles.index(curr_role):
                                        #Promoted user:
                                        promoted_users.append(curr_user)
                                    else:
                                        demoted_users.append(curr_user)
                                    with open("edited_server_list.json", "w") as data_file:
                                        json.dump(server_list, data_file, indent=2)
                                except Exception as e:
                                    await ctx.send('There was an error changing your rank ' + str(e))
                                    await ctx.send('There was an error changing : ' + str(curr_user)) #if error

            #Reset variables
            no_of_players = 0
            curr_request_list = []
            curr_request_list_users = []
    
    #Announce the promotions and demotions:
    if len(promoted_users) > 0:
        await channel.send("The following users have been promoted:")
        for user in promoted_users:
            member = discord.utils.get(id.members, id=int(user))
            await channel.send(f"""{member.mention}""")
    
    # if len(demoted_users) > 0:
    #     await channel.send("The following users have been demoted:")
    #     for user in demoted_users:
    #         member = discord.utils.get(id.members, id=int(user))
    #         await channel.send(f"""{member.mention}""")

    if len(kicked_users) > 0:
        await channel2.send("The following users have been kicked:")
        for user in kicked_users:
            member = discord.utils.get(id.members, id=int(user))
            del server_list[user]
            await channel2.send(f"kicked user: {member}")
        with open("edited_server_list.json", "w") as data_file:
            json.dump(server_list, data_file, indent=2)
    if len(inactive_users) > 0:
        await channel.send('Following users haven''t played a Squad FPP game in the last 14 days so you will be demoted to Bronze, either ask admin to enlist a different account or play some games to get your proper rank!!')
        for user in inactive_users:
            member = discord.utils.get(id.members, id=int(user))
            await channel.send(f"""{member.mention}""")
    
    # if (len(promoted_users) == 0):
    #     await channel.send("No promotions today...")

    await ctx.send("Users with more than 100 games and KD less than 2:")
    await ctx.send(less_than_2_list)

    print('Finished Updating Everything')

@client.command()   
async def updaterole(ctx):
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    id = client.get_guild(180535625034891264)
    #Rank bot annoucements channel:
    channel = client.get_channel(652624968642723850)
    user = ctx.message.author
    user_id = user.id
    if str(user_id) in server_list:
        curr_rank = server_list[str(user_id)]['Rank']
        await ctx.send('Your current rank is: ' + server_list[str(user_id)]['Rank'])
        player_ID = server_list[str(user_id)]['ID']
        season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + curr_season
        second_request = requests.get(season_url, headers=curr_header)
        no_requests = no_requests + 1
        season_info = json.loads(second_request.text)
        games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
        total_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['kills']
        season_wins = season_info['data']['attributes']['gameModeStats']['squad-fpp']['wins']
        season_losses = season_info['data']['attributes']['gameModeStats']['squad-fpp']['losses']
        season_damage = season_info['data']['attributes']['gameModeStats']['squad-fpp']['damageDealt']
        recent_matches = season_info['data']['relationships']['matchesSquadFPP']['data']
        
        if season_losses == 0:
            tru_KD = total_kills
        else:
            tru_KD = total_kills/season_losses

        GG_KD = total_kills/(games_played - season_wins)
        await ctx.send(f'{str(user)}\'s Stats:\nIn-Game KD: {round(tru_KD,4)}\nOP.GG KD: {round(GG_KD,3)}')
        await ctx.send(f'Your ADR = {round(season_damage/games_played,2)}')
        server_list[str(user_id)]['KD'] = round(tru_KD,4)
        server_list[str(user_id)]['ADR'] = round(season_damage/games_played,2)
        if games_played < 100:
            await ctx.send('You have played less than 100 games this season, so you only get Bronze role')
            await ctx.send(f'Play {100-games_played} more games this season to get your proper role!!')
        else:
            if tru_KD < 1.9:
                reason = 'Sorry your in-game KD is less than 1.9, and you need a 2+ KD to re-enter'
                await ctx.send(f'Sorry but you\'ll have to do better to be in here!, {user} will be kicked in 5s')
                time.sleep(5)
                await user.send('Sorry your in-game KD is less than 1.9, and you need a 2+ KD to re-enter')
                await user.kick(reason=reason)
            elif tru_KD < 2.0:
                new_role = 'Bronze'
            elif tru_KD < 2.5:
                new_role = 'Silver'    
            elif tru_KD < 3.0:
                new_role = 'Gold'
            elif tru_KD < 3.5:
                new_role = 'Platinum'
            elif tru_KD < 4.0:
                new_role = 'Diamond'
            else:
                new_role = 'Master'

            #People with less than 1.9 KD would have been kicked
            if tru_KD >= 1.9:
                if new_role == curr_rank:
                    await ctx.send('Your rank is the same as before')
                else:
                    try:
                        #Change rank
                        await user.add_roles(discord.utils.get(ctx.guild.roles, name=new_role))
                        server_list[str(user_id)]['Rank'] = new_role
                        #Update the rank in the server list
                        
                        #Remove old rank
                        if curr_rank != 'Bronze':
                            await user.remove_roles(discord.utils.get(ctx.guild.roles, name=curr_rank))
                        if server_roles.index(new_role) > server_roles.index(curr_rank):
                            await ctx.send("You have been promoted to " + new_role + " , good job!!")
                            #member = discord.utils.get(id.members, name=user[:-5])
                            #await channel.send(f"""{member.mention} has been promoted to {new_role}, good job!!""")
                        else:
                            await ctx.send("You have been demoted to " + new_role + " get better at the game you scrub!!")
                    except Exception as e:
                        await ctx.send('There was an error changing your rank ' + str(e)) #if error

    else:
        await ctx.send('You currently don\'t have a rank and your IGN isn\'t added to the list so use .enlist command to enlist')

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()   
async def totalEnlisted(ctx):
    await ctx.send(f'There are currently {len(server_list)} people enlisted in this server!')

@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])
async def removeuser(ctx,member: discord.Member):
    await ctx.send(f"Removing {str(member)} from the list..")
    del server_list[str(member.id)]

@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])   
async def get_team_killer(ctx):
    await ctx.send('Calculating who should get the team-killer role....')
    id = client.get_guild(180535625034891264)
    #Rank bot annoucements channel:
    channel = client.get_channel(652624968642723850)
    maxteamkills = 0
    maxteamkills_user = ''
    current_Team_killer = 'None'
    #Find the current DUMBASS
    for user in server_list:
        if server_list[user]['team_killer'] == 1:
            current_Team_killer = user
    
    for user in server_list:
        if server_list[user]['team_kills'] > maxteamkills:
            maxteamkills = server_list[user]['team_kills']
            maxteamkills_user = user

    server_list[maxteamkills_user]['team_killer'] = 1

    if current_Team_killer == 'None':
        #No Existing Team Killer
        role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
        member = discord.utils.get(id.members, id=int(maxteamkills_user))
        await member.add_roles(role)
        await channel.send(f"""A new DUMBASS role has been assigned to {member.mention}, for the most teamkills this season""")
    elif current_Team_killer == maxteamkills_user:
        #Zeus hasn't changed
        await channel.send("DUMBASS is the same as before!!")
    else:
        #Brand New DUMBASS
        role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
        member = discord.utils.get(id.members, id=int(current_Team_killer))
        await member.remove_roles(role)
        server_list[current_Team_killer]['team_killer'] = 0
        member = discord.utils.get(id.members, id=int(maxteamkills_user))
        await member.add_roles(role)
        await channel.send(f"""Previous DUMBASS has been replaced by {member.mention}, with {server_list[maxteamkills_user]['team_kills']} teamkills this seasonn""")

    # new_server_list = sorted(server_list.values(), key=itemgetter('team_kills'))
    # await channel.send('This season team-kills Top 5:')
    # top_5_string = ''
    # i = -1
    # while i > -6:
    #     IGN = new_server_list[i]['IGN']
    #     player_teamkills = new_server_list[i]['team_kills']
    #     curr_line = "%i : %s, Team-kills = %d\n" % (abs(i), IGN, player_teamkills)
    #     top_5_string = top_5_string + curr_line
    #     #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
    #     i = i - 1
    
    # await channel.send(top_5_string)

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)
    


@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])   
async def updateStats(ctx):
    #Update server list JSON with everyone's stats
    await ctx.send('Updating everyones stats')
    #Making a request based on 10 players at a time
    no_of_players = 0
    total_additions = 0
    curr_request_list = []
    curr_request_list_users = []
    total_api_requests  = 0
    for user in server_list:
        player_ID = server_list[user]['ID']
        curr_request_list.append(player_ID)
        curr_request_list_users.append(user)
        no_of_players = no_of_players + 1
        total_additions = total_additions + 1
        if no_of_players == 10 or total_additions == len(server_list):
            player_ID_list = ','.join(curr_request_list)
            season_url = "https://api.pubg.com/shards/steam/seasons/" + curr_season + "/gameMode/squad-fpp/players?filter[playerIds]=" + player_ID_list
            second_request = requests.get(season_url, headers=curr_header)
            total_api_requests = total_api_requests + 1
            if total_api_requests == 10:
                await ctx.send('10 Requests per min reached waiting for a minute')
                time.sleep(60)
                total_api_requests = 0

            if second_request.status_code == 429:
                await ctx.send('Too MANY REQUESTS')
            season_info = json.loads(second_request.text)
            for i in range(0,len(season_info['data'])):
                games_played = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
                total_losses = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['losses']
                total_kills = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['kills']
                season_damage = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['damageDealt']
                team_kills = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['teamKills']
                player_ADR = season_damage/games_played
                player_KD = total_kills/total_losses
                #add/update their KD
                curr_user = curr_request_list_users[i]
                server_list[curr_user]['KD'] = round(player_KD,4)
                server_list[curr_user]['ADR'] = round(player_ADR,2)
                server_list[curr_user]['team_kills'] = team_kills
            #Reset variables
            no_of_players = 0
            curr_request_list = []
            curr_request_list_users = []
    
    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)
    
    await ctx.send('Finished Updating the stats')

@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])
async def get_zeus(ctx):
    await ctx.send('Calculating who should get the Zeus role....')
    id = client.get_guild(180535625034891264)
    #Rank bot annoucements channel:
    channel = client.get_channel(652624968642723850)
    maxKD = 0
    maxKD_user = ''
    current_zeus = 'None'
    #Find the current Zeus
    for user in server_list:
        if server_list[user]['Zeus'] == 1:
            current_zeus = user
    
    for user in server_list:
        if (server_list[user]['KD'] > maxKD) and (server_list[user]['Rank'] != "Bronze"):
            maxKD = server_list[user]['KD']
            maxKD_user = user

    server_list[maxKD_user]['Zeus'] = 1

    if current_zeus == 'None':
        #No Existing Zeus
        role = discord.utils.get(ctx.guild.roles, name='ZEUS')
        member = discord.utils.get(id.members, id=int(maxKD_user))
        await member.add_roles(role)
        await channel.send(f"""A new ZEUS role has been assigned to {member.mention}. Congrats!!""")
    elif current_zeus == maxKD_user:
        #Zeus hasn't changed
        await channel.send("ZEUS is the same as before!!")
    else:
        #Brand New Zeus
        role = discord.utils.get(ctx.guild.roles, name='ZEUS')
        member = discord.utils.get(id.members, id=int(current_zeus))
        await member.remove_roles(role)
        server_list[current_zeus]['Zeus'] = 0
        member = discord.utils.get(id.members, id=int(maxKD_user))
        await member.add_roles(role)
        await channel.send(f"""Previous ZEUS has been replaced by {member.mention}. Congrats!!""")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])
async def get_aries(ctx):
    await ctx.send('Calculating who should get the Aries role....')
    id = client.get_guild(180535625034891264)
    #Rank bot annoucements channel:
    channel = client.get_channel(652624968642723850)
    maxADR = 0
    maxADR_user = ''
    current_aries = 'None'

    #Find the current Aries
    for user in server_list:
        if server_list[user]['Aries'] == 1:
            current_aries = user
    
    for user in server_list:
        if (server_list[user]['ADR'] > maxADR) and (server_list[user]['Rank'] != "Bronze"):
            maxADR = server_list[user]['ADR']
            maxADR_user = user

    server_list[maxADR_user]['Aries'] = 1

    if current_aries == 'None':
        #No Existing Aries
        role = discord.utils.get(ctx.guild.roles, name='Aries')
        member = discord.utils.get(id.members, id=int(maxADR_user))
        await member.add_roles(role)
        await channel.send(f"""A new Aries role (Highest ADR) has been assigned to {member.mention}. Congrats!!""")
    elif current_aries == maxADR_user:
        #Aries hasn't changed
        print("Aries is the same as before!!")
        #await channel.send("Aries is the same as before!!")
    else:
        #Brand New Aries
        role = discord.utils.get(ctx.guild.roles, name='Aries')
        member = discord.utils.get(id.members, id=int(current_aries))
        await member.remove_roles(role)
        server_list[current_aries]['Aries'] = 0
        member = discord.utils.get(id.members, id=int(maxADR_user))
        await member.add_roles(role)
        await channel.send(f"""Previous Aries has been replaced by {member.mention}. Congrats!!""")
        new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
        await channel.send('Top 5 ADR in this server (with more than 100 games this season):')
        top_5_string = ''
        total_length = len(new_server_list)
        i = -1
        j = 1
        while i > -(total_length - 1):
            IGN = new_server_list[i]['IGN']
            player_ADR = new_server_list[i]['ADR']
            if new_server_list[i]['Rank'] != "Bronze":
                curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), IGN, player_ADR)
                top_5_string = top_5_string + curr_line
                j = j + 1
            
            if j == 6:
                break
            #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
            i = i - 1
        
        await channel.send(top_5_string)

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)  

@client.command()
async def top5ADR(ctx):
    new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
    await ctx.send('Top 5 ADR in this server (with more than 100 games this season):')
    top_5_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1
    while i > -(total_length - 1):
        IGN = new_server_list[i]['IGN']
        player_ADR = new_server_list[i]['ADR']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), IGN, player_ADR)
            top_5_string = top_5_string + curr_line
            j = j + 1
        
        if j == 6:
            break
        #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i = i - 1
    
    await ctx.send(top_5_string)

@client.command()
async def top20ADR(ctx):
    new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
    await ctx.send('Top 20 ADR in this server (with more than 100 games this season):')
    top_20_string = ''
    total_length = len(new_server_list)
    i = -1
    j = 1
    while i > -(total_length - 1):
        IGN = new_server_list[i]['IGN']
        player_ADR = new_server_list[i]['ADR']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), IGN, player_ADR)
            top_20_string = top_20_string + curr_line
            j = j + 1
        
        if j == 21:
            break
        #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i = i - 1
    
    await ctx.send(top_20_string)

@client.command()
async def top20(ctx):
    #await ctx.send('Calculating top 20 (give me a min).....')
    new_server_list = sorted(server_list.values(), key=itemgetter('KD'))
    await ctx.send('Top 20 Sweaties in this server (with more than 100 games this season):')
    top_20_string = ''
    i = -1
    total_length = len(new_server_list)
    j = 1
    while i > -(total_length - 1):
        IGN = new_server_list[i]['IGN']
        player_KD = new_server_list[i]['KD']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, KD = %.3f\n" % (abs(j), IGN, player_KD)
            top_20_string = top_20_string + curr_line
            j = j + 1
        
        if j == 21:
            break
        #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i = i - 1
    
    await ctx.send(top_20_string)

@client.command()
async def top20_announce(ctx):
    channel = client.get_channel(652624968642723850)
    new_server_list = sorted(server_list.values(), key=itemgetter('KD'))
    await channel.send('Top 20 Sweaties in this server (with more than 100 games this season):')
    top_20_string = ''
    i = -1
    total_length = len(new_server_list)
    j = 1
    while i > -(total_length - 1):
        IGN = new_server_list[i]['IGN']
        player_KD = new_server_list[i]['KD']
        if new_server_list[i]['Rank'] != "Bronze":
            curr_line = "%i : %s, KD = %.3f\n" % (abs(j), IGN, player_KD)
            top_20_string = top_20_string + curr_line
            j = j + 1
        
        if j == 21:
            break
        #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
        i = i - 1
    
    await channel.send(top_20_string)

@client.command()
@commands.has_any_role(admin_roles[0],admin_roles[1],admin_roles[2])
async def reset_everyone(ctx):
    id = client.get_guild(180535625034891264)
    try:
        for user in server_list:
            if server_list[user]['Aries'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='Aries')
                member = discord.utils.get(id.members, id=int(user))
                await member.remove_roles(role)
            
            if server_list[user]['Zeus'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='ZEUS')
                member = discord.utils.get(id.members, id=int(user))
                await member.remove_roles(role)
            
            if server_list[user]['team_killer'] == 1:
                role = discord.utils.get(ctx.guild.roles, name='DUMBASS')
                member = discord.utils.get(id.members, id=int(user))
                await member.remove_roles(role)

            if server_list[user]['Rank'] != "Bronze":
                curr_rank = server_list[user]['Rank']
                server_list[user]['Rank'] = "Bronze"
                role = discord.utils.get(ctx.guild.roles, name=curr_rank)
                member = discord.utils.get(id.members, id=int(user))
                await member.remove_roles(role)
        
        with open("edited_server_list.json", "w") as data_file:
            json.dump(server_list, data_file, indent=2)

    except Exception as e:
        print(user)
        print(e)


@client.command()   
async def r_they_hacking(ctx,Username):
    await ctx.send(f'Checking if {Username} is a hacker!:')
    url = "https://api.pubg.com/shards/steam/players?filter[playerNames]=" + Username
    initial_r = requests.get(url, headers=curr_header)
    if initial_r.status_code != 200:
        await ctx.send('Wrong username (captials in username matters) or the PUBG API is down')
    else:  
        player_info = json.loads(initial_r.text)
        #First get the ID:
        player_ID = player_info['data'][0]['id'].replace('account.','')

        #Retreive the season data and calculate KD
        season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + curr_season
        second_request = requests.get(season_url, headers=curr_header)
        season_info = json.loads(second_request.text)
        games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
        await ctx.send(f'Games played this season: {games_played}')
        total_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['kills']
        season_wins = season_info['data']['attributes']['gameModeStats']['squad-fpp']['wins']
        season_losses = season_info['data']['attributes']['gameModeStats']['squad-fpp']['losses']
        season_damage = season_info['data']['attributes']['gameModeStats']['squad-fpp']['damageDealt']
        headshot_kills = season_info['data']['attributes']['gameModeStats']['squad-fpp']['headshotKills']
        cur_season_kd = total_kills/season_losses
        await ctx.send(f'This season\'s KD: {round(cur_season_kd,2)}')
        await ctx.send(f'Headshot ratio: {round((headshot_kills/total_kills)*100,2)} %')
        season_url = "https://api.pubg.com/shards/steam/players/" + player_ID + "/seasons/" + prev_season
        second_request = requests.get(season_url, headers=curr_header)
        season_info = json.loads(second_request.text)
        games_played = season_info['data']['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
        await ctx.send(f'Games played previous season: {games_played}')
        if (games_played == 0):
            await ctx.send(f'Wow this player didn\'t play any games last season')

# @client.event
# async def on_command_error(ctx,error):
#     if isinstance(error,commands.MissingAnyRole):
#         await ctx.send("Only Admins can use this command!!!")

@client.event
async def on_member_remove(member):
	channel2 = client.get_channel(652462920734605317)
	members_id = member.id
	if (str(member.id) in server_list) :
		await channel2.send(f"Removing {str(member)} from the list because they left the server")
		del server_list[str(member.id)]
		with open("edited_server_list.json", "w") as data_file:
			json.dump(server_list, data_file, indent=2)

@tasks.loop(hours=10.0)
async def updateEverything():
    global keys 
    global header 
    global no_requests
    curr_header = header
    curr_header["Authorization"] = keys[no_requests%(len(keys))]
    #Check and update everyone's roles and make announcements on promotions and demotions! 
    id = client.get_guild(180535625034891264)
    #Rank bot annoucements channel:
    channel = client.get_channel(652624968642723850)
    channel2 = client.get_channel(652462920734605317)
    print('Updating everyones stats and roles')
    #Making a request based on 10 players at a time
    no_of_players = 0
    total_additions = 0
    curr_request_list = []
    curr_request_list_users = []
    less_than_2_list = []
    #total_api_requests  = 0
    promoted_users = []
    demoted_users = []
    inactive_users = []
    kicked_users = []
    for user in server_list:
        player_ID = server_list[user]['ID']
        curr_request_list.append(player_ID)
        curr_request_list_users.append(user)
        no_of_players = no_of_players + 1
        total_additions = total_additions + 1
        if no_of_players == 10 or total_additions == len(server_list):
            player_ID_list = ','.join(curr_request_list)
            season_url = "https://api.pubg.com/shards/steam/seasons/" + curr_season + "/gameMode/squad-fpp/players?filter[playerIds]=" + player_ID_list
            second_request = requests.get(season_url, headers=curr_header)
            no_requests = no_requests + 1
            curr_header["Authorization"] = keys[no_requests%(len(keys))]
            if second_request.status_code == 429:
                print('Too MANY REQUESTS')
                time.sleep(60)
            season_info = json.loads(second_request.text)
            for i in range(0,len(season_info['data'])):
                games_played = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['roundsPlayed']
                total_losses = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['losses']
                total_kills = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['kills']
                season_damage = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['damageDealt']
                team_kills = season_info['data'][i]['attributes']['gameModeStats']['squad-fpp']['teamKills']
                recent_matches = season_info['data'][i]['relationships']['matchesSquadFPP']['data']
                
                if total_losses == 0:
                    player_KD = total_kills
                    player_ADR = season_damage
                else:
                    player_KD = total_kills/total_losses
                    player_ADR = season_damage/games_played
                
                #add/update their KD and ADR
                curr_user = curr_request_list_users[i]
                server_list[curr_user]['KD'] = round(player_KD,4)
                server_list[curr_user]['ADR'] = round(player_ADR,2)
                server_list[curr_user]['team_kills'] = team_kills
                curr_role = server_list[curr_user]['Rank']
                
                #Check if the user hasn't played a game in the last 14 days and also if they have a higher rank than Bronze
                if (len(recent_matches) == 0) and (curr_role != 'Bronze'):
                    inactive_users.append(curr_user)
                    #await ctx.send('You haven\'t played a Squad FPP game in the last 14 days so you will be demoted to Bronze, either ask admin to enlist a different account or play some games to get your proper rank!!')  
                    member = discord.utils.get(id.members, id=int(curr_user))
                    role = discord.utils.get(id.roles, name=curr_role)
                    
                    server_list[curr_user]['KD'] = 0
                    server_list[curr_user]['ADR'] = 0    

                    server_list[curr_user]['Rank'] = 'Bronze'
                    await member.remove_roles(role)
                    #Update the rank in the server list
                    if server_list[str(member.id)]['Aries'] == 1:
                        server_list[curr_user]['Aries'] = 0
                        await member.remove_roles(role)     
                    
                    if server_list[str(member.id)]['Zeus'] == 1:
                        server_list[curr_user]['Zeus'] = 0
                        role = discord.utils.get(id.roles, name='ZEUS')
                        await member.remove_roles(role)

                    with open("edited_server_list.json", "w") as data_file:
                        json.dump(server_list, data_file, indent=2)
                        
                elif (len(recent_matches) == 0):
                    member = discord.utils.get(id.members, id=int(curr_user))
                    server_list[curr_user]['KD'] = 0
                    server_list[curr_user]['ADR'] = 0    
                    server_list[curr_user]['Rank'] = 'Bronze'
                else:    
                    if games_played >= 100:
                        #Only change the role of those with more than 100 games
                        if player_KD < 1.9:
                            #Player needs to be kicked
                            try:
                                kicked_users.append(curr_user)
                            except Exception as e:
                                print('issue:' + str(e))
                        elif player_KD < 2.0:
                            less_than_2_list.append(server_list[curr_user]['IGN'])
                            new_role = 'Bronze'
                        elif player_KD < 2.5:
                            new_role = 'Silver'    
                        elif player_KD < 3.0:
                            new_role = 'Gold'
                        elif player_KD < 3.5:
                            new_role = 'Platinum'
                        elif player_KD < 4.0:
                            new_role = 'Diamond'
                        else:
                            new_role = 'Master'
                        
                        if player_KD > 1.9:
                            #Only promote/demote if their role has changed
                            if new_role != curr_role:
                                try:
                                    member = discord.utils.get(id.members, id=int(curr_user))
                                    await member.add_roles(discord.utils.get(id.roles, name=new_role))
                                    server_list[curr_user]['Rank'] = new_role
                                    #Update the rank in the server list
                                    with open("edited_server_list.json", "w") as data_file:
                                        json.dump(server_list, data_file, indent=2)
                                    #Remove old rank
                                    if curr_role != 'Bronze':
                                        await member.remove_roles(discord.utils.get(id.roles, name=curr_role))
                                    if server_roles.index(new_role) > server_roles.index(curr_role):
                                        #Promoted user:
                                        promoted_users.append(curr_user)
                                    else:
                                        demoted_users.append(curr_user)
                                    with open("edited_server_list.json", "w") as data_file:
                                        json.dump(server_list, data_file, indent=2)
                                except Exception as e:
                                    print("There was an error changing your rank " + str(e))
                                   

            #Reset variables
            no_of_players = 0
            curr_request_list = []
            curr_request_list_users = []
    
    #Announce the promotions and demotions:
    if len(promoted_users) > 0:
        await channel.send("The following users have been promoted:")
        for user in promoted_users:
            member = discord.utils.get(id.members, id=int(user))
            await channel.send(f"""{member.mention}""")
    
    # if len(demoted_users) > 0:
    #     await channel.send("The following users have been demoted:")
    #     for user in demoted_users:
    #         member = discord.utils.get(id.members, id=int(user))
    #         await channel.send(f"""{member.mention}""")

    if len(kicked_users) > 0:
        await channel2.send("The following users have been kicked:")
        reason = 'Sorry your in-game KD is less than 1.9, and you need a 2+ KD to re-enter'
        for user in kicked_users:
            member = discord.utils.get(id.members, id=int(user))
            await channel2.send(f"kicked user: {member}")
            await member.send('Sorry your in-game KD is less than 1.9, and you need a 2+ KD to re-enter')
            await member.kick(reason=reason)
            del server_list[user]
            with open("edited_server_list.json", "w") as data_file:
                json.dump(server_list, data_file, indent=2)
    
    if len(inactive_users) > 0:
        await channel.send('Following users haven''t played a Squad FPP game in the last 14 days so you will be demoted to Bronze, either ask admin to enlist a different account or play some games to get your proper rank!!')
        for user in inactive_users:
            member = discord.utils.get(id.members, id=int(user))
            await channel.send(f"""{member.mention}""")

    #Update Zeus role
    maxKD = 0
    maxKD_user = ''
    current_zeus = 'None'
    #Find the current Zeus
    for user in server_list:
        if server_list[user]['Zeus'] == 1:
            current_zeus = user
    
    for user in server_list:
        if (server_list[user]['KD'] > maxKD) and (server_list[user]['Rank'] != "Bronze"):
            maxKD = server_list[user]['KD']
            maxKD_user = user

    server_list[maxKD_user]['Zeus'] = 1

    if current_zeus == 'None':
        #No Existing Zeus
        role = discord.utils.get(id.roles, name='ZEUS')
        member = discord.utils.get(id.members, id=int(maxKD_user))
        await member.add_roles(role)
        await channel.send(f"""A new ZEUS role has been assigned to {member.mention}. Congrats!!""")
    elif current_zeus == maxKD_user:
        #Zeus hasn't changed
        print("ZEUS is the same as before!!")
    else:
        #Brand New Zeus
        role = discord.utils.get(id.roles, name='ZEUS')
        member = discord.utils.get(id.members, id=int(current_zeus))
        await member.remove_roles(role)
        server_list[current_zeus]['Zeus'] = 0
        member = discord.utils.get(id.members, id=int(maxKD_user))
        await member.add_roles(role)
        await channel.send(f"""Previous ZEUS has been replaced by {member.mention}. Congrats!!""")

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)

    maxADR = 0
    maxADR_user = ''
    current_aries = 'None'

    #Update Aries role
    for user in server_list:
        if server_list[user]['Aries'] == 1:
            current_aries = user
    
    for user in server_list:
        if (server_list[user]['ADR'] > maxADR) and (server_list[user]['Rank'] != "Bronze"):
            maxADR = server_list[user]['ADR']
            maxADR_user = user

    server_list[maxADR_user]['Aries'] = 1

    if current_aries == 'None':
        #No Existing Aries
        role = discord.utils.get(id.roles, name='Aries')
        member = discord.utils.get(id.members, id=int(maxADR_user))
        await member.add_roles(role)
        await channel.send(f"""A new Aries role (Highest ADR) has been assigned to {member.mention}. Congrats!!""")
    elif current_aries == maxADR_user:
        #Aries hasn't changed
        print("Aries is the same as before!!")
        #await channel.send("Aries is the same as before!!")
    else:
        #Brand New Aries
        role = discord.utils.get(id.roles, name='Aries')
        member = discord.utils.get(id.members, id=int(current_aries))
        await member.remove_roles(role)
        server_list[current_aries]['Aries'] = 0
        member = discord.utils.get(id.members, id=int(maxADR_user))
        await member.add_roles(role)
        await channel.send(f"""Previous Aries has been replaced by {member.mention}. Congrats!!""")
        new_server_list = sorted(server_list.values(), key=itemgetter('ADR'))
        await channel.send('Top 5 ADR in this server (with more than 100 games this season):')
        top_5_string = ''
        total_length = len(new_server_list)
        i = -1
        j = 1
        while i > -(total_length - 1):
            IGN = new_server_list[i]['IGN']
            player_ADR = new_server_list[i]['ADR']
            if new_server_list[i]['Rank'] != "Bronze":
                curr_line = "%i : %s, ADR = %.3f\n" % (abs(j), IGN, player_ADR)
                top_5_string = top_5_string + curr_line
                j = j + 1
            
            if j == 6:
                break
            #await ctx.send(f'{abs(i)}: {IGN} , KD = {player_KD}')
            i = i - 1

        await channel.send(top_5_string)

    with open("edited_server_list.json", "w") as data_file:
        json.dump(server_list, data_file, indent=2)


client.run(bot_token)