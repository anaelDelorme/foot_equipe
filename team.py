from collections import defaultdict
from player import Player

class Team:
    def __init__(self, team_id: int, nb_subteams: int):
        self.team_id = team_id
        self.subteams = [[] for _ in range(nb_subteams)]

    def add_player_to_subteam(self, player: Player, subteam_id: int):
        self.subteams[subteam_id].append(player)

    def get_average_level(self) -> float:
        all_players = [p for subteam in self.subteams for p in subteam]
        if not all_players:
            return 0
        return sum(p.niveau for p in all_players) / len(all_players)

    def get_subteam_average_level(self, subteam_id: int) -> float:
        if not self.subteams[subteam_id]:
            return 0
        return sum(p.niveau for p in self.subteams[subteam_id]) / len(
            self.subteams[subteam_id]
        )
