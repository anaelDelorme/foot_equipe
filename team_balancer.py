# team_balancer.py
import random
import pandas as pd
from utils import get_team_color
def distribute_players_by_level(players, num_teams, num_subteams):
    """
    Distribue les joueurs en s'assurant que les niveaux sont répartis équitablement
    """
    total_players = len(players)
    players_per_team = total_players // num_teams
    players_per_subteam = players_per_team // num_subteams
    
    # Grouper les joueurs par niveau
    players_by_level = {}
    for player in players:
        level = player['niveau']
        if level not in players_by_level:
            players_by_level[level] = []
        players_by_level[level].append(player)
    
    # Initialiser les équipes
    teams = {get_team_color(i, num_teams)[0]: {j: [] for j in range(1, num_subteams + 1)}
             for i in range(num_teams)}
    
    # Préparer tous les slots d'équipe/sous-équipe
    all_slots = [(team_name, subteam_num) 
                 for team_name in teams.keys() 
                 for subteam_num in range(1, num_subteams + 1)] * players_per_subteam
    
    # Ajouter des slots pour joueurs restants
    extra_slots = [(list(teams.keys())[i % num_teams], (i // num_teams) % num_subteams + 1) 
                   for i in range(total_players - len(all_slots))]
    all_slots.extend(extra_slots)
    
    # Mélanger et assigner les joueurs
    random.shuffle(all_slots)
    slot_index = 0
    for level_players in players_by_level.values():
        random.shuffle(level_players)
        for player in level_players:
            team_name, subteam_num = all_slots[slot_index]
            teams[team_name][subteam_num].append(player)
            slot_index += 1
    
    return teams

def balance_teams(df, num_teams, num_subteams):
    """
    Répartit les joueurs en équipes équilibrées
    """
    # Préparer les données
    players = []
    non_disponibles = []
    
    for _, row in df.iterrows():
        player = {
            'nom': row['prénom'],
            'niveau': row['niveau'],
            'poste': row['poste']
        }
        
        if pd.isna(row['présence']):
            non_disponibles.append(player)
        else:
            players.append(player)
    
    # Distribuer les joueurs
    teams = distribute_players_by_level(players, num_teams, num_subteams)
    
    return teams, non_disponibles