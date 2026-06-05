"""Riot API client skeleton for Rift Watcher."""

import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

from .database_client import DatabaseClient
from ..types import RiotMatchData, RiotPlayerProfile

class RiotAPIClient:
    """Handles requests to the Riot API and validates responses."""

    def __init__(self, region: str, database_client: DatabaseClient | None = None):
        load_dotenv()
        self.api_key = os.getenv('RIOT_API_KEY')
        self.region = region
        self.database_client = database_client

        self.request_headers = {
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://developer.riotgames.com",
            "X-Riot-Token": self.api_key,
        }
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

    def fetch_match_history(self, player_id: str) -> list[RiotMatchData]:
        """Fetch match history from Riot for a given player."""
        # Placeholder: Replace with Riot API integration and response validation.
        return [
            {
                "game_id": f"game_{player_id}_1",
                "champion": "PlaceholderChampion",
                "role": "Mid",
                "kills": 5,
                "deaths": 3,
                "assists": 7,
                "win": True,
                "damage_share": 0.28,
                "cs": 180,
                "duration_minutes": 32,
                "lp_change": 18,
            }
        ]

    def fetch_player_profile(self, summoner_name: str, region: str) -> RiotPlayerProfile:
        """Fetch player profile details from Riot."""
        summoner_data = self.__get_summoner_by_name(summoner_name, region)
        if not summoner_data or summoner_data.get("status", {}).get("status_code") == 404:
            raise ValueError(f"Summoner {summoner_name} not found in region {region}")

        league_entries = self.__get_league_data_by_summoner_id(summoner_data["id"], region)
        ranked_tier = None
        ranked_division = None
        rank = "Unranked"

        if isinstance(league_entries, list) and league_entries:
            solo_entry = next(
                (entry for entry in league_entries if entry.get("queueType") == self.queue_types["SOLO"]),
                None,
            )
            selected_entry = solo_entry or league_entries[0]
            ranked_tier = selected_entry.get("tier")
            ranked_division = selected_entry.get("rank")
            if ranked_tier and ranked_division:
                rank = f"{ranked_tier} {ranked_division}"

        return {
            "player_id": summoner_data.get("id"),
            "display_name": summoner_data.get("name", summoner_name),
            "region": region,
            "rank": rank,
            "ranked_tier": ranked_tier,
            "ranked_division": ranked_division,
        }

    def __get_summoner_profile(self, summoner_name: str, region: str):
        '''
        Get a specific player's profile data (summoner level, rank, etc).
        '''
        summoner_data = self.__get_summoner_by_name(summoner_name, region)
        if not summoner_data:
            raise ValueError(f"Summoner {summoner_name} not found in region {region}")
        
        else:
            account_data = self.__get_league_data_by_summoner_id(summoner_data['id'], region)
            parsed_account_data = self.__parse_account_data(account_data)
            parsed_account_data['profileIcon'] = summoner_data['profileIconId']
            
            # Winrate calculations. Note that the else conditions are if the player is unranked
            if parsed_account_data and 'solo_data' in parsed_account_data:
                solo_wins = parsed_account_data['solo_data']['wins']
                solo_losses= parsed_account_data['solo_data']['losses']
                solo_winrate = calculate_winrate(solo_wins, solo_losses)
                parsed_account_data['solo_winrate'] = solo_winrate
            else:
                parsed_account_data['solo_data'] = {'rank': [None, None], 'wins': None, 'losses': None, 'lp': None}
                parsed_account_data['solo_winrate'] = None

            if parsed_account_data and 'flex_data' in parsed_account_data:
                flex_wins = parsed_account_data['flex_data']['wins']
                flex_losses = parsed_account_data['flex_data']['losses']
                flex_winrate = calculate_winrate(flex_wins, flex_losses)
                parsed_account_data['flex_winrate'] = flex_winrate
            else:
                parsed_account_data['flex_data'] = {'rank': [None, None], 'wins': None, 'losses': None, 'lp': None}
                parsed_account_data['flex_winrate'] = None
            
            user_data = {'summoner_account_data': parsed_account_data}
            return {'status': 1, 'summoner_data': user_data}

    def __get_summoner_by_name(self, summoner_name: str, region: str):
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

    def __summoner_profile_exists(self, summoner_name: str, region: str):
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

    def __get_league_data_by_summoner_id(self, summoner_id: str, region: str):
        '''
        Get league of legends game info via summoner id. This will return info such as ranks for each queue, tiers, etc. via RiotAPI
        '''
        url = f"https://{self.regions[region]}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}"
        try:
            account_info = requests.get(url, headers=self.request_headers, timeout=10)
            account_info.raise_for_status()
        except requests.HTTPError as e:
            print(f"HTTP error fetching league data for {summoner_id}: {e}")
            return []
        except requests.RequestException as e:
            print(f"Error fetching league data for {summoner_id}: {e}")
            return []

        return account_info.json()
        
