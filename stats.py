import json

class statsCalc:

    class playerStats:
        def __init__(self, c_rank, c_tier, c_rank_points, h_rank,
        h_tier, h_rank_points, games_played, KDA, season_wins, season_damage,
        new_rank, ADR, team_kills):
            self.c_rank = c_rank
            self.c_tier = c_tier
            self.c_rank_points = c_rank_points
            self.h_rank = h_rank
            self.h_tier = h_tier
            self.h_rank_points = h_rank_points
            self.games_played = games_played
            self.KDA = KDA
            self.season_wins = season_wins
            self.season_damage = season_damage
            self.new_rank = new_rank
            self.ADR = ADR
            self.team_kills = team_kills
            
    def __init__(self, playerid, playerJson):
        self.player = playerid
        self.pStats = self.gatherStats(playerJson)

    def gatherStats(self, jsonPayload):
        season_info = jsonPayload
        try:
            c_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['tier']
            c_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentTier']['subTier']
            c_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['currentRankPoint']
            h_rank = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['tier']
            h_tier = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestTier']['subTier']
            h_rank_points = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['bestRankPoint']
            games_played = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['roundsPlayed']
            KDA = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda']
            season_wins = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['wins']
            season_damage = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['damageDealt']
            team_kills = season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['teamKills']
            new_rank = c_rank + " " + c_tier
            ADR = round(season_damage / games_played, 0)
            KDA = round(season_info['data']['attributes']['rankedGameModeStats']['squad-fpp']['kda'], 2)
        except:
            c_rank = 'Unranked'
            c_tier = ''
            c_rank_points = 0
            h_rank = 'Unranked'
            h_tier = ''
            h_rank_points = 0
            games_played = 0
            KDA = 0
            season_wins = 0
            season_damage = 0
            team_kills = 0
            new_rank = c_rank
            ADR = 0
            KDA = 0

        return statsCalc.playerStats(c_rank, c_tier, c_rank_points, h_rank, h_tier, h_rank_points, games_played, KDA, season_wins, season_damage, new_rank, ADR,team_kills)