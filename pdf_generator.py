# pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from utils import get_team_color


def create_pdf(teams, non_disponibles):
    """
    Génère un PDF avec les sous-équipes empilées verticalement par équipe,
    avec des en-têtes colorés répétés pour chaque sous-équipe
    """
    doc = SimpleDocTemplate(
        "teams.pdf",
        pagesize=landscape(A4),
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    # Calculer le nombre maximum de joueurs pour dimensionner le tableau
    max_players = max(
        len(players) for team in teams.values() for players in team.values()
    )

    # Préparer les données
    data = []

    # Créer les en-têtes des sous-équipes 1
    headers_1 = []
    for i in range(len(teams)):
        team_name, _ = get_team_color(i, len(teams))
        simple_name = team_name.replace("Équipe ", "").capitalize()
        headers_1.append(f"{simple_name} 1")
    headers_1.append("Non disponibles")
    data.append(headers_1)

    # Remplir les données des joueurs de la sous-équipe 1
    for i in range(max_players):
        row = []
        for team in teams.values():
            if 1 in team and i < len(team[1]):
                row.append(team[1][i]["prénom"])
            else:
                row.append("")
        # Ajouter un espace pour les non disponibles
        row.append("")
        data.append(row)

    # Créer les en-têtes des sous-équipes 2
    headers_2 = []
    for i in range(len(teams)):
        team_name, _ = get_team_color(i, len(teams))
        simple_name = team_name.replace("Équipe ", "").capitalize()
        headers_2.append(f"{simple_name} 2")
    headers_2.append("Non disponibles")
    data.append(headers_2)

    # Remplir les données des joueurs de la sous-équipe 2
    for i in range(max_players):
        row = []
        for team in teams.values():
            if 2 in team and i < len(team[2]):
                row.append(team[2][i]["prénom"])
            else:
                row.append("")
        # Ajouter les non disponibles
        if i < len(non_disponibles):
            row.append(non_disponibles[i]["prénom"])
        else:
            row.append("")
        data.append(row)

    # Créer le tableau
    col_width = (A4[1] - inch) / (len(teams) + 1)
    table = Table(data, colWidths=[col_width] * (len(teams) + 1))

    styles = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
        ("OUTLINE", (0, 0), (-1, -1), 1, colors.black),
    ]

    # Ajouter les couleurs pour les en-têtes d'équipe 1 et 2
    for i in range(len(teams)):
        _, color = get_team_color(i, len(teams))
        if isinstance(color, str):
            color = colors.HexColor(color)

        # Style pour l'en-tête de la sous-équipe 1
        styles.extend(
            [
                ("BACKGROUND", (i, 0), (i, 0), color),
                ("TEXTCOLOR", (i, 0), (i, 0), colors.white),
                ("FONT", (i, 0), (i, 0), "Helvetica-Bold", 12),
            ]
        )

        # Style pour l'en-tête de la sous-équipe 2
        header_2_row = max_players + 1
        styles.extend(
            [
                ("BACKGROUND", (i, header_2_row), (i, header_2_row), color),
                ("TEXTCOLOR", (i, header_2_row), (i, header_2_row), colors.white),
                ("FONT", (i, header_2_row), (i, header_2_row), "Helvetica-Bold", 12),
            ]
        )

    # Style pour "Non disponibles"
    styles.extend(
        [
            ("BACKGROUND", (-1, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (-1, 0), (-1, 0), colors.white),
            ("FONT", (-1, 0), (-1, 0), "Helvetica-Bold", 12),
            ("BACKGROUND", (-1, max_players + 1), (-1, max_players + 1), colors.gray),
            ("TEXTCOLOR", (-1, max_players + 1), (-1, max_players + 1), colors.white),
            (
                "FONT",
                (-1, max_players + 1),
                (-1, max_players + 1),
                "Helvetica-Bold",
                12,
            ),
        ]
    )

    # Ajouter des lignes verticales entre les équipes
    for i in range(len(teams)):
        styles.append(("LINEAFTER", (i, 0), (i, -1), 1, colors.black))

    # Ajouter une ligne horizontale entre les sous-équipes 1 et 2
    styles.append(("LINEBELOW", (0, max_players), (-1, max_players), 1, colors.black))

    table.setStyle(TableStyle(styles))
    doc.build([table])
