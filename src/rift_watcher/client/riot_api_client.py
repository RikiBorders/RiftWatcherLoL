"""Riot API client skeleton for Rift Watcher."""

import os
from typing import Dict, List
from urllib import response
from urllib.parse import quote

import requests
from dotenv import load_dotenv

from .database_client import DatabaseClient
from ..type.types import RiotMatchData, RiotPlayerProfile

class RiotAPIClient:
    """Handles requests to the Riot API and validates responses."""

    def __init__(self, region: str):
        load_dotenv()
        self.api_key = os.getenv('RIOT_API_KEY')
        self.region = region
        self.database_client = DatabaseClient()

        self.request_headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": self.api_key,
        }
        self.headers = self.request_headers

        # Region mapping for Riot API endpoints
        self.regions = {
            "NA" : "na1",
            "BR" : "br1",
            "EUN" : "eun1",
            "EUW" : "euw1",
            "JP" : "jp1",
            "KR" : "kr",
            "LA1" : "la1",
            "LA2" : "la2",
            "OC" : "oc1",
            "TR" : "tr1",
            "RU" : "ru"
        }
        self.account_regions = {
            "NA": "americas",
            "BR": "americas",
            "LA1": "americas",
            "LA2": "americas",
            "OC": "americas",
            "EUN": "europe",
            "EUW": "europe",
            "TR": "europe",
            "RU": "europe",
            "JP": "asia",
            "KR": "asia",
        }

        # Riot ranked queues
        self.queue_types = {
            "SOLO" : "RANKED_SOLO_5x5",
            "FLEX" : "RANKED_FLEX_SR"
        }

        # Riot ranked divisions
        self.division = {
            "ONE" : "I",
            "TWO" : "II",
            "THREE" : "III",
            "FOUR" : "IV"
        }

    def fetch_player_profile(
        self,
        game_name: str,
        tag_line: str,
        region: str,
    ):
        account_data = self._get_account_by_riot_id(
            game_name=game_name,
            tag_line=tag_line,
            region=region,
        )

        summoner_data = self._get_summoner_by_puuid(
            puuid=account_data["puuid"],
            region=region,
        )

        league_entries = self._get_league_data_by_summoner_id(
            summoner_data["puuid"],
            region,
        )

        solo_queue = next(
            (
                entry
                for entry in league_entries
                if entry["queueType"] == "RANKED_SOLO_5x5"
            ),
            None,
        )

        flex_queue = next(
            (
                entry
                for entry in league_entries
                if entry["queueType"] == "RANKED_FLEX_SR"
            ),
            None,
        )

        return {
            "display_name": (
                f"{account_data['gameName']}"
                f"#{account_data['tagLine']}"
            ),
            "profile_icon_id": summoner_data.get(
                "profileIconId"
            ),
            "summoner_level": summoner_data.get(
                "summonerLevel"
            ),
            "puuid": account_data["puuid"],
            "solo_queue": solo_queue,
            "flex_queue": flex_queue,
        }
    
    def _get_account_by_riot_id(
        self,
        game_name: str,
        tag_line: str,
        region: str,
    ) -> Dict:
        """
        Riot Account-V1 lookup.

        Returns:
        {
            "puuid": "...",
            "gameName": "Faker",
            "tagLine": "KR1"
        }
        """
        account_region = self.account_regions[region]

        url = (
            f"https://{account_region}.api.riotgames.com"
            f"/riot/account/v1/accounts/by-riot-id"
            f"/{quote(game_name)}"
            f"/{quote(tag_line)}"
        )

        response = requests.get(
            url,
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()
    
    def _get_summoner_by_puuid(
        self,
        puuid: str,
        region: str
    ) -> Dict:
        """
        Resolve a Riot account PUUID into a League Summoner object.
        Returns Riot's SummonerDTO:
        {
            "id": "...",            # encrypted summoner id
            "accountId": "...",
            "puuid": "...",
            "profileIconId": 1234,
            "summonerLevel": 500
        }
        """
        platform = self.regions[region]

        url = (
            f"https://{platform}.api.riotgames.com"
            f"/lol/summoner/v4/summoners/by-puuid/{puuid}"
        )

        response = requests.get(
            url,
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()
        print("Fetched Summoner by puuid:" + str(response.json()))
        return response.json()

    def _get_summoner_by_name(self, summoner_name: str, region: str):
        '''
        Get summoner account info via summoner name & region via the RiotAPI
        '''
        try:
            encoded_name = quote(summoner_name)
            url = f"https://{self.regions[region]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_name}"
            summoner_info = requests.get(url, headers=self.request_headers, timeout=10)
            summoner_info.raise_for_status()
        except requests.HTTPError as e:
            if summoner_info.status_code == 404:
                return {}
            print(f"HTTP error fetching summoner data for {summoner_name}: {e}")
            return {}
        except requests.RequestException as e:
            print(f"Error fetching summoner data for {summoner_name}: {e}")
            return {}

        return summoner_info.json()

    def get_league_match_ids_by_puuid(self, puuid: str, region: str, number_of_matches: int = 20) -> list[str]:
        url = (
            f"https://{self.regions[region]}.api.riotgames.com"
            f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        )

        params = {
            "count": number_of_matches
        }

        response = requests.get(url, params=params, headers=self.request_headers, timeout=10)
        response.raise_for_status()
        print(f"Fetched match IDs for PUUID {puuid}: {response.json()}")
        return response.json()
    
    def get_match_data_batch(self, match_ids: list[str], region: str) -> list[RiotMatchData]:
        response = []
        for match_id in match_ids:
            response.append(self._get_match(match_id, region))

        return response

    def _get_match(self, match_id: str, region: str) -> Dict:
        """
        Get detailed match data.
        """

        url = (
            f"https://{self.regions[region]}.api.riotgames.com"
            f"/lol/match/v5/matches/{match_id}"
        )

        response = requests.get(url, headers=self.request_headers, timeout=10)
        response.raise_for_status()

        return response.json()

    def get_match_ids(
        self,
        puuid: str,
        count: int = 5,
        region: str = "NA"
    ) -> List[str]:
        """
        Get recent match IDs for a player.
        """
        url = (
            f"https://{self.regions[region]}.api.riotgames.com"
            f"/lol/match/v5/matches/by-puuid/{puuid}/ids"
        )

        params = {
            "count": count
        }

        response = requests.get(
            url,
            headers=self.request_headers,
            params=params,
            timeout=10
        )
        response.raise_for_status()

        print(f"Fetched match IDs for PUUID {puuid}: {response.json()}")
        return response.json()
    
    def _summoner_profile_exists(self, summoner_name: str, region: str):
        '''
        private method to check if a summoner exists
        '''
        try:
            encoded_name = quote(summoner_name)
            url = f"https://{self.regions[region]}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{encoded_name}"
            summoner_data = requests.get(url, headers=self.request_headers, timeout=10).json()
        except requests.RequestException as e:
            print(f"Error fetching summoner data for {summoner_name}: {e}")
            return {}
        
        return summoner_data

    def _get_league_data_by_summoner_id(self, puuid: str, region: str):
        '''
        Get league of legends game info via summoner id. This will return info such as ranks for each queue, tiers, etc. via RiotAPI
        '''
        url = f"https://{self.regions[region]}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
        try:
            account_info = requests.get(url, headers=self.request_headers, timeout=10)
            account_info.raise_for_status()
        except requests.HTTPError as e:
            print(f"HTTP error fetching league data for {puuid}: {e}")
            return []
        except requests.RequestException as e:
            print(f"Error fetching league data for {puuid}: {e}")
            return []

        print("Received League Data from Riot API: " + str(account_info.json()))
        return account_info.json()
        
