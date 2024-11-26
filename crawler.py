from typing import Self
from sqlmodel import SQLModel, create_engine, Session
from managers import LeaderboardDataManager, MatchDataManager, AssetsDataManager
import httpx
from utils import flatten_dict, RateLimitTransport
from tqdm import tqdm
import httpx
import random
from models import Player, MatchPlayers
from sqlalchemy import func, select,distinct, text
from httpcore import PoolTimeout
from itertools import cycle
from dotenv import load_dotenv
import os

class ValorantApiCrawler:
    def __init__(self) -> Self:
        load_dotenv()
        self.API_URL = os.getenv("API_URL")
        self.AUTH_KEYS = os.getenv("API_KEYS").split(",")
        self.engine = create_engine(os.getenv("DATABASE_URL"))
        
        SQLModel.metadata.create_all(self.engine)
        self.key_cycle = cycle(self.AUTH_KEYS)
        self.client = httpx.Client(base_url=self.API_URL, transport=RateLimitTransport())

    def api_call(self, endpoint, params=None):
        try:
            response = self.client.get(endpoint, params=params, timeout=60, headers={"Authorization": next(self.key_cycle)})
            return response.json()
        except PoolTimeout as e:
            print("Pool Timeout, retrying...")
            self.__init__()
            return self.api_call(endpoint, params)
        
    def sync_assets(self):
        assets_data = self.api_call("valorant/v1/content")
        AssetsDataManager(engine=self.engine, data=assets_data).save()
        
    def crawl_leaderboard(self, region, platform):
        print(f"Crawling leaderboard for {region} {platform}")
        players = []
        for page in tqdm(range(1,10)):
            data = self.api_call(f"/valorant/v3/leaderboard/{region}/{platform}",
                                 params={"page": page, "size": 1000})
            leaderboard_manager = LeaderboardDataManager(engine=self.engine, data=data, region=region, platform=platform)
            leaderboard_manager.save()
            uuids = leaderboard_manager.get_player_uuids()
            players.extend(uuids)
        return players
    
    def crawl_matches_from_player(self, region, platform, player_uuid, num_pages=1, page_size=10):
        # Max page size for api is 10, can fetch up to 80 for activate players, else will result an error
        # for page in (pbar1 := tqdm(range(1, num_pages+1),leave=False)):
        for page in range(1, num_pages+1):
            # pbar1.set_description(f"Processing {page} of player {player_uuid}")
            try:
                data = self.api_call(f"/valorant/v4/by-puuid/matches/{region}/{platform}/{player_uuid}",
                                    params={"size": page_size, "start": (page-1)*page_size})
                for match in data['data']:
                    match_manager = MatchDataManager(engine=self.engine, data=match)
                    match_manager.save()
            except Exception as e:
                print(f"An error has ocurred when crawling matches with player: {e}")
                continue


    def crawl_matches_from_leaderboard(self, region, platform, limit=50):
        players = self.crawl_leaderboard(region, platform)

        # Get the total number of matches present in the database
        with Session(self.engine) as session:
            query = (
                session.exec(
                        select(Player.puuid)
                            .outerjoin(MatchPlayers, Player.puuid == MatchPlayers.player_puuid)
                            .group_by(Player.puuid)
                            .having(func.count(MatchPlayers.match_id) >= 10)
                    )
            )
            players_to_exclude = [row[0] for row in query.all()]

        players = list(set(players) - set(players_to_exclude))
        players = random.choices(players, k=min(limit, len(players)))
        
        for player_uuid in (pbar := tqdm(players)):
            pbar.set_description(f"Processing matches of player {player_uuid}")
            try:
                self.crawl_matches_from_player(region, platform, player_uuid)
            
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error: {e}")
                continue

    def crawl_matches_from_players_less_than_n_matches(self, num_matches=10, limit=50, recursive=False):
        with Session(self.engine) as session:
            query = (
                session.exec(
                    text(
                        f"""
                        SELECT player.puuid, 
                            player.primary_platform, 
                            player.primary_region, 
                            COUNT(DISTINCT(match_players.match_id)) AS match_count
                        FROM player
                        LEFT JOIN match_players ON player.puuid = match_players.player_puuid
                        WHERE player.primary_platform IS NOT NULL AND player.primary_region IS NOT NULL
                        GROUP BY player.puuid
                        HAVING COUNT(match_id) < {num_matches}
                        ORDER BY match_count ASC
                        LIMIT {limit}
                        """
                    )        
                )
            )
            for puuid, platform, region, _ in (pbar := tqdm(query.all())):
                pbar.set_description(f"Processing player {puuid} with {num_matches} current matches")
                self.crawl_matches_from_player(region, platform, puuid, num_pages=1, page_size=10)
        
        if recursive:
            self.crawl_matches_from_players_less_than_n_matches(num_matches=num_matches, limit=limit, recursive=recursive)

if __name__ == "__main__":
    crawler = ValorantApiCrawler()
    crawler.sync_assets()
    for region in ["na", "eu", "ap", "kr", "latam"]:
        crawler.crawl_matches_from_leaderboard(region, "pc")
    crawler.crawl_matches_from_players_less_than_n_matches(num_matches=10, limit=50, recursive=True)