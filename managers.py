from models import (Agent, 
                    Map, 
                    Equipment, 
                    Leaderboard, 
                    Player, 
                    Match, 
                    MatchPlayers, 
                    Act, 
                    Tier,
                    MatchTeams, 
                    MatchRounds,
                    MatchRoundPlant,
                    MatchRoundDefuse,
                    MatchRoundPlayerLocations,
                    MatchRoundPlayerStats,
                    MatchRoundPlayerStatsDamageEvents,
                    MatchRoundKills,
                    MatchRoundKillsPlayerLocations,
                    MatchRoundAssists,
                    Queue,
                    Armor
)
from utils import flatten_dict
from sqlmodel import Session
import time
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import exists

class MatchDataManager:
    "API reference: v4_match"
    def __init__(self, engine, data):
        self.engine = engine
        
        self.match_metadata :dict = data['metadata']
        self.platform :str = data['metadata']['platform']
        self.region :str = data['metadata']['region']

        self.match_id :str = data['metadata']['match_id']

        self.match_players :dict = data['players']
        self.player_agent_mappings = {match_player["puuid"]: match_player["agent"]["id"] for match_player in data['players']}
        
        self.match_observers :dict = data['observers']
        self.match_coaches :dict = data['coaches']
        self.match_teams :dict = data['teams']
        self.match_rounds :dict = data['rounds']
        self.match_kills :dict = data['kills']

    def _get_player_agent(self, player_puuid):
        return self.player_agent_mappings.get(player_puuid, "Unknown")

    def _save_metadata(self,session):
        queue_obj = Queue(
            **flatten_dict(self.match_metadata['queue'])
        )
        session.merge(queue_obj)
        
        obj = Match(
            id = self.match_id,
            **flatten_dict(self.match_metadata)
        )
        session.merge(obj)
        session.commit()
    
    def _save_match_players(self,session):
        for match_player in self.match_players:
            player_obj = Player(
                puuid = match_player["puuid"],
                name = match_player["name"],
                tag = match_player["tag"],
                primary_region=self.region,
                primary_platform=self.platform
            )
            session.merge(player_obj)
            session.commit()

            match_player_flat = flatten_dict(match_player)
            match_player_flat['player_puuid'] = match_player_flat.pop('puuid')
            match_player_obj = MatchPlayers(
                match_id = self.match_id,
                **match_player_flat,
            )
            session.merge(match_player_obj)
            session.commit()
               
    def _save_match_teams(self,session):
        for team in self.match_teams:
            team_obj = MatchTeams(
                match_id = self.match_id,
                **flatten_dict(team)
            )
            session.merge(team_obj)

    def _save_match_rounds(self,session):
        # for round in self.match_rounds:
        
        def _indiv(round):
            objs = []
            # rename id to round_id
            round_flat = flatten_dict(round)
            round_flat['round_num'] = round_flat.pop('id')
            round_obj = MatchRounds(
                match_id = self.match_id,
                **round_flat
            )
            objs.append(round_obj)
            # session.merge(round_obj)
            if round['plant']:
                objs_ = self._save_match_round_plant(session, round['plant'], round['id'])
                objs.extend(objs_)
            if round['defuse']:
                objs_ = self._save_match_round_defuse(session, round['plant'], round['id'])
                objs.extend(objs_)
            objs_ = self._save_match_round_player_stats(session, round['stats'], round['id'])
            objs.extend(objs_)
            return objs

        
        with ThreadPoolExecutor() as executor:
            executor.map(_indiv, self.match_rounds)
            results = list(executor.map(_indiv, self.match_rounds))
            objs = []
            
            for result in results:
                objs.extend(result)
            #print("LEN OF RESULTS", len(objs))
            for obj in objs:
                session.merge(obj)
        session.commit()
    
    def _save_match_round_plant(self, session, round_plant, round_num):
        objs = []
        player_puuid = round_plant['player']['puuid']

        round_plant_flat = flatten_dict(round_plant)
        plant_obj = MatchRoundPlant(
            match_id=self.match_id,
            round_num=round_num,
            agent_id = self._get_player_agent(player_puuid),
            **round_plant_flat
        )
        objs.append(plant_obj)
        # session.merge(plant_obj)
        for player_location in round_plant['player_locations']:
            obj = self._save_match_round_player_locations(session, player_location, round_num, "PLANT")
            objs.append(obj)
        return objs

    def _save_match_round_defuse(self, session, round_defuse, round_num):
        objs = []
        player_puuid = round_defuse['player']['puuid']

        round_defuse_flat = flatten_dict(round_defuse)
        defuse_obj = MatchRoundDefuse(
            match_id=self.match_id,
            round_num=round_num,
            agent_id = self._get_player_agent(player_puuid),
            **round_defuse_flat
        )
        objs.append(defuse_obj)
        # session.merge(defuse_obj)
        for player_location in round_defuse['player_locations']:
            obj = self._save_match_round_player_locations(session, player_location, round_num, "DEFUSE")
            objs.append(obj)
        return objs

    def _save_match_round_player_locations(self, session, player_location, round_num,event):
        player_loc_obj = MatchRoundPlayerLocations(
            match_id=self.match_id,
            round_num=round_num,
            agent_id=self._get_player_agent(player_location['player']['puuid']),
            **flatten_dict(player_location),
            event_type=event,
        )
        return player_loc_obj
        # session.merge(player_loc_obj)
    
    def _save_match_round_player_stats(self, session, player_stats, round_num):
        objs = []
        for player_stat in player_stats:
            if player_stat['economy']['weapon'] is not None:
                equipment_obj = Equipment(
                    id = player_stat['economy']['weapon']['id'],
                    name = player_stat['economy']['weapon']['name'],
                    type = player_stat['economy']['weapon']['type'],
                )
                # session.merge(equipment_obj)
                objs.append(equipment_obj)


            if player_stat['economy']['armor'] is not None:
                armor_obj = Armor(
                    id = player_stat['economy']['armor']['id'],
                    name = player_stat['economy']['armor']['name'],
                )
                objs.append(armor_obj)

                # session.merge(armor_obj)
            player_stat_obj = MatchRoundPlayerStats(
                match_id=self.match_id,
                round_num=round_num,
                agent_id=self._get_player_agent(player_stat['player']['puuid']),
                **flatten_dict(player_stat)
            )
            objs.append(player_stat_obj)
            # session.merge(player_stat_obj)
            # session.commit()

            _metadata = {
                "round_num": round_num,
                "player_puuid": player_stat['player']['puuid'],
                "player_team": player_stat['player']['team'],
                "player_agent_id": self._get_player_agent(player_stat['player']['puuid']),
            }
            objs_ = self._save_match_player_stats_damage_events(session, player_stat['damage_events'], _metadata)
            objs.extend(objs_)
            return objs
    
    def _save_match_player_stats_damage_events(self, session, damage_events, _metadata : dict):
        objs = []
        for damage_event in damage_events:
            damage_event_flat = flatten_dict(damage_event)
            damage_event_flat['receiver_puuid'] = damage_event_flat.pop('player_puuid')
            damage_event_flat['receiver_team'] = damage_event_flat.pop('player_team')
            damage_event_flat['receiver_agent_id'] = self._get_player_agent(damage_event_flat['receiver_puuid'])
            
            damage_event_obj = MatchRoundPlayerStatsDamageEvents(
                match_id=self.match_id,
                **damage_event_flat,
                **_metadata,
            )
            objs.append(damage_event_obj)
        return objs
            # session.merge(damage_event_obj)
        # session.commit()

    def _save_match_kills(self, session):

        def _indiv(kill):
            objs = []
            if kill['weapon']['id'] is not None:
                weapon_obj = Equipment(
                    id = kill['weapon']['id'],
                    name = kill['weapon']['name'],
                    type = kill['weapon']['type'],
                )
                objs.append(weapon_obj)
                # session.merge(weapon_obj)

            killer_obj = Player(
                puuid = kill['killer']['puuid'],
                name = kill['killer']['name'],
                tag = kill['killer']['tag'],
                primary_platform=self.platform,
                primary_region=self.region
            )
            victim_obj = Player(
                puuid = kill['victim']['puuid'],
                name = kill['victim']['name'],
                tag = kill['victim']['tag'],
                primary_platform=self.platform,
                primary_region=self.region
            )
            objs.append(killer_obj)
            objs.append(victim_obj)
            # session.merge(killer_obj)
            # session.merge(victim_obj)
            # session.commit()
            kill_flat = flatten_dict(kill)
            kill_flat['round_num'] = kill_flat.pop('round')
            kill_obj = MatchRoundKills(
                match_id=self.match_id,
                killer_agent_id=self._get_player_agent(kill['killer']['puuid']),
                victim_agent_id=self._get_player_agent(kill['victim']['puuid']),
                **kill_flat
            )
            _metadata = {
                "round_num": kill_flat['round_num'],
                "killer_puuid": kill['killer']['puuid'],
                "killer_team": kill['killer']['team'],
                "killer_agent_id": self._get_player_agent(kill['killer']['puuid']),
                "victim_puuid": kill['victim']['puuid'],
                "victim_team": kill['victim']['team'],
                "victim_agent_id": self._get_player_agent(kill['victim']['puuid']),

            }
            objs.extend(self._save_match_assists(session, kill['assistants'], _metadata))
            objs.extend(self._save_match_round_kills_player_locations(session, kill['player_locations'], _metadata))
            objs.append(kill_obj)
            return objs

        with ThreadPoolExecutor() as executor:
            executor.map(_indiv, self.match_kills)
            results = list(executor.map(_indiv, self.match_kills))
            objs = []
            for result in results:
                objs.extend(result)
            #print("LEN OF RESULTS MATCH KILLS", len(objs))
            for obj in objs:
                session.merge(obj)
        
        # for kill in self.match_kills:
            
        session.commit()

    def _save_match_round_kills_player_locations(self, session, player_locations, _metadata):
        objs = []
        for player_location in player_locations:
            player_loc_obj = MatchRoundKillsPlayerLocations(
                match_id=self.match_id,
                player_agent_id=self._get_player_agent(player_location['player']['puuid']),
                **flatten_dict(player_location),
                **_metadata,
            )
            # session.merge(player_loc_obj)
            objs.append(player_loc_obj)
        return objs
        # session.commit()

    def _save_match_assists(self, session, assists, _metadata):
        objs = []
        for assist in assists:
            assists_flat = flatten_dict(assist)
            assists_flat['assistant_puuid'] = assists_flat.pop('puuid')
            assists_flat['assistant_team'] = assists_flat.pop('team')
            assists_flat['assistant_agent_id'] = self._get_player_agent(assists_flat['assistant_puuid'])
            assist_obj = MatchRoundAssists(
                match_id=self.match_id,
                **assists_flat,
                **_metadata
            )
            objs.append(assist_obj)
        return objs
            # session.merge(assist_obj)
        # session.commit()

    def save(self):
        
        # print("Saving match data", self.match_id)
        time_ = time.time()
        with Session(self.engine) as session:
            match_exists = session.exec(exists().where(Match.id == self.match_id).select()).scalar()
            if match_exists:
                # print(f"Match {self.match_id} already exists in the database.")
                return
            # print(f"Session took {time.time() - time_:.2f} seconds to connect.")
            self._save_metadata(session)
            #print(f"Saving metadata took {time.time() - time_:.2f} seconds")
            self._save_match_players(session)
            #print(f"Saving players took {time.time() - time_:.2f} seconds")
            self._save_match_teams(session)
            #print(f"Saving teams took {time.time() - time_:.2f} seconds")
            self._save_match_rounds(session)
            #print(f"Saving rounds took {time.time() - time_:.2f} seconds")
            self._save_match_kills(session)
            #print(f"Saving kills took {time.time() - time_:.2f} seconds")
            session.commit()

class LeaderboardDataManager:
    def __init__(self, engine, data, region, platform):
        self.engine = engine
        self.region = region
        self.platform = platform
        self.players = data['data']['players']

    def save(self):
        with Session(self.engine) as session:
            for leaderboard in self.players:
                # #print(f"Saving leaderboard at {self.region} {self.platform}, {leaderboard['tier']}, {leaderboard['leaderboard_rank']}" )
                if leaderboard["puuid"] is not None:
                    player_obj = Player(
                        puuid = leaderboard["puuid"],
                        name = leaderboard["name"],
                        tag = leaderboard["tag"],
                        primary_region=self.region,
                        primary_platform=self.platform
                    )
                    session.merge(player_obj)
                leaderboard_obj = Leaderboard(
                    platform = self.platform,
                    region = self.region,
                    **flatten_dict(leaderboard),
                )
                session.merge(leaderboard_obj)
            session.commit()
        return self.players
    
    def get_player_uuids(self):
        return [player['puuid'] for player in self.players if player['puuid'] is not None]
    
class AssetsDataManager:
    def __init__(self, engine, data) -> None:
        self.data = data
        self.engine = engine
        self.version = data['version']
        self.assets_data = data

    def save(self):
        with Session(self.engine) as session:
            for character in self.assets_data['characters']:
                agent = Agent(
                    id = character["id"],
                    name = character["name"],
                    asset_name = character["assetName"],
                    localized_names = str(character["localizedNames"]),
                    version = self.version
                )
                session.merge(agent)
            unknown_agent = Agent(
                id = "Unknown",
                name = "Unknown",
                asset_name = "Unknown",
                localized_names=[],
                version = self.version
            )
            session.merge(unknown_agent)
            for map in self.assets_data["maps"]:
                map = Map(
                    id = map["id"],
                    name = map["name"],
                    asset_name = map["assetName"],
                    localized_names = str(map["localizedNames"]),
                    version = self.version
                )
                session.merge(map)

            for equipment in self.assets_data["equips"]:
                equipment = Equipment(
                    id = equipment["id"],
                    name = equipment["name"],
                    asset_name = equipment["assetName"],
                    localized_names = str(equipment["localizedNames"]),
                    version = self.version
                )
                session.merge(equipment)

            for act in self.assets_data["acts"]:
                act = Act(
                    id = act["id"],
                    parent_id=act["parentId"] if act['parentId'] != "00000000-0000-0000-0000-000000000000" else None,
                    type = act["type"],
                    name = act["name"],
                    localized_names=str(act["localizedNames"]),
                    is_active=act["isActive"],
                )
                session.merge(act)

            tiers = [
                (27, "Radiant"),
                (26, "Immmortal 3"),
                (25, "Immmortal 2"),
                (24, "Immmortal 1"),
                (23, "Radiant 3"),
                (22, "Radiant 2"),
                (21, "Radiant 1"),
                (20, "Diamond 3"),
                (19, "Diamond 2"),
                (18, "Diamond 1"),
                (17, "Platinum 3"),
                (16, "Platinum 2"),
                (15, "Platinum 1"),
                (14, "Gold 3"),
                (13, "Gold 2"),
                (12, "Gold 1"),
                (11, "Silver 3"),
                (10, "Silver 2"),
                (9, "Silver 1"),
                (8, "Bronze 3"),
                (7, "Bronze 2"),
                (6, "Bronze 1"),
                (5, "Iron 3"),
                (4, "Iron 2"),
                (3, "Iron 1"),
                (2, "Unranked"),
                (1, "Unknown"),
                (0, "Unrated"),
            ]
            for tier in tiers:
                tier_obj = Tier(
                    id = tier[0],
                    name = tier[1]
                )
                session.merge(tier_obj)
            session.commit()