# from pydantic import BaseModel
# from typing import List, Optional

# class BaseDto(BaseModel):
#     class Config:
#         orm_mode = True

# class CoachDto(BaseDto):
#     puuid : str
#     teamId : str

# class TeamDto(BaseDto):
#     teamId : str
#     won : bool
#     roundsPlayed : int
#     roundsWon : int
#     numPoints : int

# class LocationDto(BaseDto):
#     x : int
#     y : int

# class PlayerLocationsDto(BaseDto):
#     puuid : str
#     viewRadians : float
#     location : List[LocationDto]
# class FinishingDamageDto(BaseDto):
#     damageType : str
#     damageItem : str
#     isSecondaryFireMode : bool

# class KillDto(BaseDto):
#     timeSinceGameStartMillis : int
#     timeSinceRoundStartMillis : int
#     killer : str
#     victim : str
#     victimLocation : Optional[LocationDto]
#     assister : Optional[list[str]]
#     playerLocations : List[PlayerLocationsDto]
#     finishingDamage : FinishingDamageDto

# class DamageDto(BaseDto):
#     receiver : str
#     damage : int
#     legshots : int
#     bodyshots : int
#     headshots : int

# class EconomyDto(BaseDto):
#     loadoutValue : int
#     weapon : str
#     armor : str
#     remaining : int
#     spent : int

# class AbilityCastsDto(BaseDto):
#     grenadeCasts : int
#     ability1Casts : int
#     ability2Casts : int
#     ultimateCasts : int

# class PlayerRoundStatsDto(BaseDto):
#     puuid : str
#     kills : List[KillDto]
#     damage : List[DamageDto]
#     score : int
#     economy : EconomyDto
#     ability : AbilityCastsDto

# class RoundResultDto(BaseDto):
#     roundNum : int
#     roundResult : str
#     roundCeremony : str
#     winningTeam : str
#     bombPlanter : Optional[str]
#     bombDefuser : Optional[str]
#     plantRoundTime : Optional[int]
#     plantPlayerLocations : List[PlayerLocationsDto]
#     plantLocation : Optional[LocationDto]
#     plantSite : Optional[str]
#     defuseRoundTime : Optional[int]
#     defusePlayerLocations : List[PlayerLocationsDto]
#     defuseLocation : Optional[LocationDto]
#     playerStats : List[PlayerRoundStatsDto]


# class AbilityCastsDto(BaseDto):
#     grenadeCasts : int
#     ability1Casts : int
#     ability2Casts : int
#     ultimateCasts : int

# class PlayerStatsDto(BaseDto):
#     score : int
#     roundsPlayed : int
#     kills : int
#     deaths : int
#     assists : int
#     playtimeMillis : int
#     abilityCasts :  AbilityCastsDto


# class PlayerDto(BaseDto):
#     puuid : str
#     gameName : str
#     tagLine : str
#     teamId : str
#     partyId : str
#     characterId : str
#     stats : PlayerStatsDto


