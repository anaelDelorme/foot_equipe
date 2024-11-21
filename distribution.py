import random
from typing import List
from collections import defaultdict
import numpy as np
from math import ceil, floor
from player import Player
from team import Team


def distribute_players_by_position(
    players_by_position: dict, num_teams: int
) -> List[Player]:
    """
    Distribue les joueurs de chaque position équitablement entre les équipes
    avant de les mélanger dans chaque groupe.
    """
    distributed_players = []
    team_assignments = [[] for _ in range(num_teams)]

    # Traiter chaque position
    for position, players in players_by_position.items():
        num_players = len(players)
        min_per_team = floor(num_players / num_teams)
        extra_players = num_players % num_teams

        # Mélanger les joueurs de cette position
        random.shuffle(players)
        player_index = 0

        # Distribuer le minimum de joueurs à chaque équipe
        for team_idx in range(num_teams):
            players_to_add = min_per_team
            # Ajouter un joueur supplémentaire si nécessaire
            if extra_players > 0:
                players_to_add += 1
                extra_players -= 1

            team_assignments[team_idx].extend(
                players[player_index : player_index + players_to_add]
            )
            player_index += players_to_add

    # Mélanger l'ordre des joueurs dans chaque équipe
    for team_players in team_assignments:
        random.shuffle(team_players)
        distributed_players.extend(team_players)

    return distributed_players


def calculate_optimal_distribution(
    total_players: int, num_teams: int, num_subteams: int
) -> List[List[int]]:
    avg_players_per_team = total_players / num_teams
    team_sizes = []
    remaining_players = total_players
    for i in range(num_teams):
        if i == num_teams - 1:
            team_sizes.append(remaining_players)
        else:
            size = round(avg_players_per_team)
            team_sizes.append(size)
            remaining_players -= size

    subteam_distribution = []
    for team_size in team_sizes:
        avg_players_per_subteam = team_size / num_subteams
        subteam_sizes = []
        remaining_team_players = team_size

        for j in range(num_subteams):
            if j == num_subteams - 1:
                subteam_sizes.append(remaining_team_players)
            else:
                size = round(avg_players_per_subteam)
                subteam_sizes.append(size)
                remaining_team_players -= size

        subteam_distribution.append(subteam_sizes)

    return subteam_distribution


def calculate_level_penalty(levels: List[float], target: float = None) -> float:
    """
    Calcule une pénalité basée sur l'écart des niveaux par rapport à la moyenne.
    Plus les écarts sont grands, plus la pénalité augmente de manière exponentielle.
    """
    if not levels:
        return 0

    if target is None:
        target = sum(levels) / len(levels)

    # Calculer les écarts par rapport à la cible
    deviations = [abs(level - target) for level in levels]
    max_deviation = max(deviations)

    # Pénalité de base basée sur l'écart-type
    penalty = np.std(levels) * 50

    # Pénalité supplémentaire pour les grands écarts
    if (
        max_deviation > 0.5
    ):  # Seuil à partir duquel on considère l'écart comme important
        penalty += (max_deviation * 2) ** 2 * 100

    return penalty


def distribute_players(
    players: List[Player], num_teams: int, num_subteams: int, max_iterations: int = 1000
) -> List[Team]:
    total_players = len(players)
    distribution_plan = calculate_optimal_distribution(
        total_players, num_teams, num_subteams
    )

    def create_distribution(
        players_list: List[Player], dist_plan: List[List[int]]
    ) -> List[Team]:
        teams = [Team(i, num_subteams) for i in range(num_teams)]
        players_index = 0

        for team_id, subteam_sizes in enumerate(dist_plan):
            for subteam_id, size in enumerate(subteam_sizes):
                for _ in range(size):
                    if players_index < len(players_list):
                        teams[team_id].add_player_to_subteam(
                            players_list[players_index], subteam_id
                        )
                        players_index += 1

        return teams

    def evaluate_distribution(teams: List[Team]) -> float:
        score = 0

        # Évaluer l'équilibre des niveaux entre équipes
        team_levels = [team.get_average_level() for team in teams]
        team_level_sums = [team.get_total_level() for team in teams]

        # Pénalité basée sur la moyenne des niveaux
        score += calculate_level_penalty(team_levels)
        
        # Nouvelle pénalité basée sur la somme totale des niveaux
        score += calculate_level_penalty(team_level_sums) * 0.5 

        # Récupérer tous les niveaux de sous-équipes
        all_subteam_levels = []
        for team in teams:
            subteam_levels = [
                team.get_subteam_average_level(i) for i in range(num_subteams)
            ]
            all_subteam_levels.extend(subteam_levels)

            # Pénaliser les écarts au sein de chaque équipe
            score += (
                calculate_level_penalty(subteam_levels) * 2
            )  # Coefficient plus élevé pour les sous-équipes

        # Pénaliser les écarts entre toutes les sous-équipes
        score += calculate_level_penalty(all_subteam_levels) * 1.5

        return score

    best_score = float("inf")
    best_distribution = None
    iterations_without_improvement = 0

    for iteration in range(max_iterations):
        # Regrouper les joueurs par position
        players_by_position = defaultdict(list)
        for player in players:
            players_by_position[player.poste].append(player)

        # Distribuer les joueurs équitablement par position
        ordered_players = distribute_players_by_position(players_by_position, num_teams)
        teams = create_distribution(ordered_players, distribution_plan)
        score = evaluate_distribution(teams)

        if score < best_score:
            best_score = score
            best_distribution = teams
            iterations_without_improvement = 0
        else:
            iterations_without_improvement += 1

        # Conditions d'arrêt
        if score < 50:  # Solution très satisfaisante trouvée
            break
        if iterations_without_improvement > 100:  # Pas d'amélioration depuis longtemps
            break

    return best_distribution
