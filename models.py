from sqlmodel import Field, SQLModel
from datetime import datetime

class Equipment(SQLModel, table=True):
    """
    Equipment refers to weapons and abilities of the Agents (armor not included).
    """
    __tablename__ = "equipment"
    id : str = Field(primary_key=True)
    name : str | None
    asset_name : str | None
    localized_names : str | None
    version : str | None
    # Note: type is only present in match history, not in assets api 
    type : str | None # values: weapon, ability, fall bomb

class Armor(SQLModel, table=True):  
    """
    Speaks for itself. Light and heavy shields
    """
    __tablename__ = "armor"
    id : str = Field(primary_key=True)
    name : str

class Map(SQLModel,table=True):
    """
    All maps in the game: standard maps, team deathmatch maps, and tutorial maps.
    """
    __tablename__ = "map"
    id : str = Field(primary_key=True)
    name : str
    asset_name : str
    localized_names : str
    version : str

class Queue(SQLModel,table=True):
    """
    Diff queue types: Unrated, competitive, team deathmatch, deathmatch, etc.
    """
    __tablename__ = "queue"
    id : str = Field(primary_key=True)
    name : str
    mode_type : str

class Act(SQLModel, table=True):
    """
    Acts are the seasons in Valorant up to Episode 9 Act 3.
    """
    __tablename__ = "act"
    id : str = Field(primary_key=True)
    parent_id : str | None
    type : str
    name : str
    localized_names : str
    is_active : bool


class Player(SQLModel,table=True):
    """
    Player information. This is the main table for player information.
    """
    __tablename__ = "player"
    puuid : str = Field(primary_key=True)
    name : str
    tag : str
    primary_region : str | None
    primary_platform : str | None

class Agent(SQLModel,table=True):
    """
    All 26 Valorant agents plus 'Base' agents.
    """
    __tablename__ = "agent"
    id : str = Field(primary_key=True)
    name : str
    asset_name : str
    localized_names : str
    version : str

class Tier(SQLModel,table=True):
    """
    Unrated rank (0) to Radiant (27) and all other queues.
    When referenced in other tables, this is the tier_id.
    """
    __tablename__ = "tier"
    id : int = Field(primary_key=True)
    name : str

class Match(SQLModel,table=True):
    """
    Grain is one row per match. This is the main table for match information.
    """
    __tablename__ = "match"
    __henrik_schema__ = "v4_match"

    id : str = Field(primary_key=True)
    map_id : str = Field(foreign_key="map.id")
    game_version : str
    game_length_in_ms : int
    started_at : datetime
    is_completed : bool
    queue_id : str = Field(foreign_key="queue.id")
    season_id : str = Field(foreign_key="act.id")
    platform : str
    premier : str | None
    region : str
    cluster : str

class Leaderboard(SQLModel, table=True):
    """
    Player leaderboard information.
    """
    __tablename__ = "leaderboard"

    id : int | None = Field(default=None, primary_key=True)
    platform : str 
    region : str
    card : str
    title : str
    is_banned : bool
    is_anonymized : bool
    puuid : str | None = Field(foreign_key="player.puuid")
    leaderboard_rank : int
    tier : int # Equivalent to tier_id max 27 min 0 (unrated to radiant)
    rr : int
    wins : int
    updated_at : datetime

class MatchPlayers(SQLModel, table=True):
    """
    Grain is one row per player per match.
    """
    __tablename__ = "match_players"
    match_id : str = Field(foreign_key="match.id", primary_key=True)
    player_puuid : str | None = Field(foreign_key="player.puuid", primary_key=True)
    team_id : str | None
    platform : str
    party_id : str | None
    agent_id : str = Field(foreign_key="agent.id")

    stats_score : int
    stats_kills : int
    stats_deaths : int
    stats_assists : int
    stats_headshots : int
    stats_bodyshots : int
    stats_legshots : int
    stats_damage_dealt : int
    stats_damage_received : int
    ability_casts_grenade : int|None = Field(default=0)
    ability_casts_ability1 : int|None = Field(default=0)
    ability_casts_ability2 : int|None = Field(default=0)
    ability_casts_ultimate : int|None = Field(default=0)

    tier_id : int = Field(foreign_key="tier.id")

    account_level : int
    session_playtime_in_ms : int
    behavior_afk_rounds : float
    behavior_friendly_fire_incoming : float
    behavior_friendly_fire_outgoing : float
    behavior_rounds_in_spawn : float

    economy_spent_overall : int
    economy_spent_average : float|None = Field(default=0)
    economy_loadout_value_overall : int
    economy_loadout_value_average : float|None = Field(default=0)

class MatchTeams(SQLModel, table=True):
    """
    Grain is one row per team per match.
    """
    __tablename__ = "match_teams"

    team_id : str = Field(primary_key=True)
    match_id : str = Field(foreign_key="match.id", primary_key=True)
    won : bool
    rounds_won : int
    rounds_lost : int

class MatchRounds(SQLModel, table=True):
    """
    Grain is one row per round per match.
    """
    __tablename__ = "match_rounds"

    match_id : str = Field(foreign_key="match.id", primary_key=True)
    round_num : int = Field(primary_key=True) # id in the match round
    result : str
    ceremony : str
    winning_team : str

class MatchRoundPlant(SQLModel, table=True):
    """
    Grain is one row per round per match IF spike is planted in that round.
    """
    __tablename__ = "match_round_plant"

    match_id : str = Field(foreign_key="match.id", primary_key=True)
    round_num : int = Field(primary_key=True)
    round_time_in_ms : int
    site : str
    location_x : int
    location_y : int

    # Player puuid may be None, if no plant, or the player is anonymous.  IF player is anonymous and there is a plant, use agent_id instead
    player_puuid : str | None = Field(foreign_key="player.puuid")
    player_team : str
    agent_id : str | None = Field(foreign_key="agent.id")

class MatchRoundDefuse(SQLModel, table=True):
    """
    Grain is one row per round per match IF spike is defused in that round.
    """
    __tablename__ = "match_round_defuse"

    match_id : str = Field(foreign_key="match.id", primary_key=True)
    round_num : int = Field(primary_key=True)
    round_time_in_ms : int
    location_x : int
    location_y : int

    # Player puuid may be None, if no defuse, or the player is anonymous.  IF player is anonymous and there is a defuse, use agent_id instead
    player_puuid : str | None = Field(foreign_key="player.puuid")
    player_team : str
    agent_id : str | None = Field(foreign_key="agent.id")

class MatchRoundPlayerLocations(SQLModel, table=True):
    """
    Grain is one row per player per round per match.
    Indicates the location of all players when the spike is planted or defused.
    """
    __tablename__ = "match_round_player_locations"

    match_id : str = Field(foreign_key="match.id", primary_key=True)
    round_num : int = Field(primary_key=True)

    # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
    player_puuid : str | None= Field(foreign_key="player.puuid",primary_key=True)
    player_team : str
    agent_id : str = Field(foreign_key="agent.id")

    view_radians : float
    location_x : float
    location_y : float
    event_type : str # POSSIBE VALUES: plant, defuse

class MatchRoundPlayerStats(SQLModel, table=True):
    """
    Grain is one row per player per round per match.
    Per-round player statistics.
    """
    __tablename__ = "match_round_player_stats"

    match_id : str = Field(foreign_key="match.id", primary_key=True)
    round_num : int = Field(primary_key=True)

    # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
    player_puuid : str | None= Field(foreign_key="player.puuid", primary_key=True)
    player_team : str
    agent_id : str = Field(foreign_key="agent.id")

    ability_casts_grenade : int|None = Field(default=0)
    ability_casts_ability1 : int|None = Field(default=0)
    ability_casts_ability2 : int|None = Field(default=0)
    ability_casts_ultimate : int|None = Field(default=0)

    stats_bodyshots : int|None = Field(default=0)
    stats_headshots : int|None = Field(default=0)
    stats_legshots : int|None = Field(default=0)
    stats_damage : int|None = Field(default=0)
    stats_kills : int|None = Field(default=0)
    stats_assists : int|None = Field(default=0)
    stats_score : int|None = Field(default=0)

    economy_loadout_value : int
    economy_remaining : int
    economy_weapon_id : str | None = Field(foreign_key="equipment.id")
    economy_armor_id : str | None= Field(foreign_key="armor.id")

    was_afk : bool
    received_penalty : bool
    stayed_in_spawn : bool

class MatchRoundPlayerStatsDamageEvents(SQLModel, table=True):
    """
    Grain is one row per damage per victim per round per match.
    Answers the question: Who did how much damage to whom in a round?
    """
    __tablename__ = "match_round_player_stats_damage_events"

    match_id : str = Field(foreign_key="match.id", primary_key=True)
    round_num : int = Field(primary_key=True)

    # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
    player_puuid : str = Field(foreign_key="player.puuid", primary_key=True)
    player_team : str
    player_agent_id : str = Field(foreign_key="agent.id")

    receiver_puuid : str = Field(foreign_key="player.puuid", primary_key=True)
    receiver_team : str
    receiver_agent_id : str = Field(foreign_key="agent.id")
    
    bodyshots : int
    headshots : int
    legshots : int
    damage : int

class MatchRoundKills(SQLModel, table=True):
    """
    Grain is one row per kill per round per match.
    Answers the question: Who killed whom in a round?
    """
    __tablename__ = "match_round_kills"

    id: int | None = Field(default=None, primary_key=True)

    match_id : str = Field(foreign_key="match.id",)
    round_num : int = Field() # internal name: round

    time_in_round_in_ms : int
    time_in_match_in_ms : int

    # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
    killer_puuid : str = Field(foreign_key="player.puuid", )
    killer_team : str
    killer_agent_id : str = Field(foreign_key="agent.id")

    victim_puuid : str = Field(foreign_key="player.puuid", )
    victim_team : str
    victim_agent_id : str = Field(foreign_key="agent.id")

    location_x : float
    location_y : float

    weapon_id : str | None = Field(foreign_key="equipment.id")

    secondary_fire_mode : bool

class MatchRoundKillsPlayerLocations(SQLModel, table=True):
    """
    Grain is one row per player per killer per victim per round per match.
    Answers the question: Where was the player when a kill happened?
    """
    __tablename__ = "match_round_kills_player_locations"

    id: int | None = Field(default=None, primary_key=True)

    match_id : str = Field(foreign_key="match.id", )
    round_num : int = Field() # internal name: round

    # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
    killer_puuid : str = Field(foreign_key="player.puuid",)
    killer_team : str
    killer_agent_id : str = Field(foreign_key="agent.id")

    victim_puuid : str = Field(foreign_key="player.puuid",)
    victim_team : str
    victim_agent_id : str = Field(foreign_key="agent.id")

    player_puuid : str = Field(foreign_key="player.puuid",)
    player_team : str
    player_agent_id : str = Field(foreign_key="agent.id")

    view_radians : float
    location_x : float
    location_y : float

class MatchRoundAssists(SQLModel, table=True):
    """
    Grain is one row per assist per round per match.
    Answers the question: Who assisted whom in a round?
    """
    __tablename__ = "match_round_assists"
    
    id: int | None = Field(default=None, primary_key=True)
    
    match_id : str = Field(foreign_key="match.id", )
    round_num : int = Field()# internal name: round

    # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
    assistant_puuid : str | None = Field(foreign_key="player.puuid", )
    assistant_team : str
    assistant_agent_id : str = Field(foreign_key="agent.id")

    killer_puuid : str | None = Field(foreign_key="player.puuid", )
    killer_team : str
    killer_agent_id : str  = Field(foreign_key="agent.id")

    victim_puuid : str | None = Field(foreign_key="player.puuid", )
    victim_team : str
    victim_agent_id : str = Field(foreign_key="agent.id")


# class MatchRoundKills(SQLModel, table=True):
#     """
#     Grain is one row per kill per round per match.
#     Answers the question: Who killed whom in a round?
#     """
#     __tablename__ = "match_round_kills"

    
#     match_id : str = Field(foreign_key="match.id",primary_key=True)
#     round_num : int = Field(primary_key=True) # internal name: round

#     time_in_round_in_ms : int
#     time_in_match_in_ms : int

#     # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
#     killer_puuid : str = Field(foreign_key="player.puuid", primary_key=True)
#     killer_team : str
#     killer_agent_id : str = Field(foreign_key="agent.id")

#     victim_puuid : str = Field(foreign_key="player.puuid", primary_key=True)
#     victim_team : str
#     victim_agent_id : str = Field(foreign_key="agent.id")

#     location_x : float
#     location_y : float

#     weapon_id : str | None = Field(foreign_key="equipment.id")

#     secondary_fire_mode : bool

# class MatchRoundKillsPlayerLocations(SQLModel, table=True):
#     """
#     Grain is one row per player per killer per victim per round per match.
#     Answers the question: Where was the player when a kill happened?
#     """
#     __tablename__ = "match_round_kills_player_locations"

#     match_id : str = Field(foreign_key="match.id", primary_key=True)
#     round_num : int = Field(primary_key=True) # internal name: round

#     # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
#     killer_puuid : str = Field(foreign_key="player.puuid",primary_key=True)
#     killer_team : str
#     killer_agent_id : str = Field(foreign_key="agent.id")

#     victim_puuid : str = Field(foreign_key="player.puuid",primary_key=True)
#     victim_team : str
#     victim_agent_id : str = Field(foreign_key="agent.id")

#     player_puuid : str = Field(foreign_key="player.puuid",primary_key=True)
#     player_team : str
#     player_agent_id : str = Field(foreign_key="agent.id")

#     view_radians : float
#     location_x : float
#     location_y : float

# class MatchRoundAssists(SQLModel, table=True):
#     """
#     Grain is one row per assist per round per match.
#     Answers the question: Who assisted whom in a round?
#     """
#     __tablename__ = "match_round_assists"
    
#     match_id : str = Field(foreign_key="match.id", primary_key=True)
#     round_num : int = Field(primary_key=True)# internal name: round

#     # Player puuid may be None, if the player is anonymous.  IF player is anonymous, use agent_id instead
#     assistant_puuid : str | None = Field(foreign_key="player.puuid", primary_key=True)
#     assistant_team : str
#     assistant_agent_id : str = Field(foreign_key="agent.id")

#     killer_puuid : str | None = Field(foreign_key="player.puuid", primary_key=True)
#     killer_team : str
#     killer_agent_id : str  = Field(foreign_key="agent.id")

#     victim_puuid : str | None = Field(foreign_key="player.puuid", primary_key=True)
#     victim_team : str
#     victim_agent_id : str = Field(foreign_key="agent.id")
