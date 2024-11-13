# pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
from utils import get_team_color


def create_pdf(teams, non_disponibles):
    """
    Génère un PDF avec les équipes et les non disponibles à la fin
    """
    doc = SimpleDocTemplate("teams.pdf", pagesize=landscape(A4),
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Trouver le nombre maximum de joueurs dans une sous-équipe
    max_players = max(len(players) for team in teams.values() for players in team.values())
    max_subteams = max(len(team) for team in teams.values())
    
    # Créer l'en-tête
    data = [list(teams.keys()) + ["Non disponibles"]]
    
    # Ajouter les sous-équipes
    for subteam_num in range(1, max_subteams + 1):
        data.append([f"Sous-équipe {subteam_num}" for _ in teams] + [""])
        
        # Ajouter chaque joueur dans la sous-équipe ou laisser vide s'il n'y en a pas
        for player_index in range(max_players):
            row_data = []
            for team in teams.values():
                if subteam_num in team and player_index < len(team[subteam_num]):
                    row_data.append(team[subteam_num][player_index]['nom'])
                else:
                    row_data.append("")
            
            # Ajouter un joueur non disponible seulement à la fin
            if subteam_num == max_subteams and player_index < len(non_disponibles):
                row_data.append(non_disponibles[player_index]['nom'])
            else:
                row_data.append("")
                
            data.append(row_data)

    # Créer et styliser le tableau
    col_width = (A4[1] - inch) / (len(teams) + 1)
    table = Table(data, colWidths=[col_width] * (len(teams) + 1))
    styles = []

    # En-têtes des équipes avec couleurs
    for i, team in enumerate(teams.keys()):
        _, color = get_team_color(i, len(teams))
        styles.append(('BACKGROUND', (i, 0), (i, 0), color))
        styles.append(('TEXTCOLOR', (i, 0), (i, 0), colors.white))
    
    # Style général
    styles.extend([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (-1, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (-1, 0), (-1, 0), colors.white),
    ])
    
    table.setStyle(TableStyle(styles))
    doc.build([table])
