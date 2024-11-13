# utils.py

def get_team_color(index, total_teams):
    """Retourne le nom et la couleur de l'équipe basé sur l'index"""
    colors = [
        ("Équipe rouge", "#FF0000"),
        ("Équipe jaune", "#FFD700"),
        ("Équipe verte", "#008000"),
        ("Équipe bleue", "#0000FF")
    ]
    
    if index == total_teams - 1:
        return "Sans dossard", "#808080"
    
    if index < len(colors):
        return colors[index]
    
    return f"Équipe {index + 1}", "#808080"