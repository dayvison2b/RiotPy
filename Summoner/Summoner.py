from typing import Optional, Union, List, Dict, Any
from RiotAPIService import RiotAPIService  # Import RiotAPIService module
from datetime import datetime


class Summoner:
    def __init__(self, api_key: str, summoner_name: Optional[str] = None, account_id: Optional[str] = None,
                 summoner_id: Optional[str] = None, region: str = "br1") -> None:
        """
        Initialize a Summoner instance.
        :param api_key: API key for Riot API.
        :param summoner_name: Optional summoner name.
        :param account_id: Optional account ID.
        :param summoner_id: Optional summoner ID.
        :param region: Region for API requests.
        """
        self._api_key = api_key
        self._summoner_name = summoner_name
        self._account_id = account_id
        self._summoner_id = summoner_id
        self._region = region
        self._summoner_info = None  # To store summoner info
        self._riot_api = RiotAPIService(api_key, region)  # Initialize RiotAPIService instance

    @property
    def account_id(self) -> str:
        return self._summoner_info["accountId"]

    @property
    def summoner_id(self) -> str:
        return self._summoner_info["id"]

    @property
    def summoner_name(self) -> str:
        return self._summoner_info["name"]

    @property
    def summoner_level(self) -> int:
        return self._summoner_info["summonerLevel"]

    @property
    def summoner_masteries(self) -> dict[str, Any]:
        return self._riot_api.get_masteries(self._summoner_info["id"])

    @property
    def summoner_info(self) -> Dict[str, Any]:
        """Get the complete summoner info."""
        return self._summoner_info()

    def get_match_history(self) -> List[dict]:
        match_ids = self._riot_api.get_match_ids_by_puuid(self._summoner_info["puuid"])
        match_history = []
        for match_id in match_ids:
            match_details = self._riot_api.get_match_details_by_id(match_id)
            match_info = self._extract_match_info(match_details)
            match_history.append(match_info)
        return match_history

    def _extract_match_info(self, match_details):
        participant_id = self._find_participant_id(match_details)
        participant_data = match_details["info"]["participants"][participant_id]
        match_date = datetime.fromtimestamp(match_details["info"]["gameStartTimestamp"] // 1000)
        match_result = "Win" if participant_data["win"] else "Defeat"

        return {
            "match_id": match_details["metadata"]["matchId"],
            "date": match_date.strftime("%Y-%m-%d %H:%M:%S"),
            "result": match_result
        }

    def _find_participant_id(self, match_details):
        for i, participant in enumerate(match_details["info"]["participants"]):
            if participant["summonerId"] == self.summoner_id:
                return i
        raise ValueError("Summoner not found in participants")

    def _get_summoner_info(self):
        """
        Fetch summoner info from Riot API based on available parameters.
        If summoner info is already fetched, return the cached info.
        """
        if not self._summoner_info:
            if self._account_id:
                self._summoner_info = self._riot_api.get_summoner_by_account_id(self._account_id)
            elif self._summoner_id:
                self._summoner_info = self._riot_api.get_summoner_by_summoner_id(self._summoner_id)
            elif self._summoner_name:
                self._summoner_info = self._riot_api.get_summoner_by_name(self._summoner_name)
            else:
                raise ValueError("At least one summoner information must be provided.")
        return self._summoner_info

    def exists(self) -> bool:
        """Check if the summoner exists."""
        summoner_info = self._get_summoner_info()
        return summoner_info is not None
