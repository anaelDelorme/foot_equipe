# pdf_generator.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from utils import get_team_color
import os

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
  #  os.write(1, f"Mes teams sont {teams} !".encode())

    # Identifier le nombre maximum de joueurs
    max_players = max(
        len(players) for team in teams.values() for players in team.values()
    )

    # Préparer les données
    data = []

    # Créer les en-têtes des sous-équipes
    headers_1 = []
    for i in range(len(teams)):
        team_name, _ = get_team_color(i, len(teams))
        simple_name = team_name.replace("Équipe ", "").capitalize()
        headers_1.append(f"{simple_name} 1")
    data.append(headers_1)

    # Remplir les données des joueurs de la sous-équipe 1
    for i in range(max_players):
        row = []
        for team in teams.values():
            if 1 in team and i < len(team[1]):
                row.append(team[1][i]["prénom"])
            else:
                row.append("")
        data.append(row)

    # Créer les en-têtes des sous-équipes 2
    headers_2 = []
    for i in range(len(teams)):
        team_name, _ = get_team_color(i, len(teams))
        simple_name = team_name.replace("Équipe ", "").capitalize()
        headers_2.append(f"{simple_name} 2")
    data.append(headers_2)

    # Remplir les données des joueurs de la sous-équipe 2
    for i in range(max_players):
        row = []
        for team in teams.values():
            if 2 in team and i < len(team[2]):
                row.append(team[2][i]["prénom"])
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

    # Section pour les joueurs non disponibles
    stylesheets = getSampleStyleSheet()
    non_disponibles_section = [
        Spacer(1, 0.5 * inch),
        Paragraph("<b>Joueuses non disponibles :</b>", stylesheets["Heading3"]),
    ]

    if non_disponibles:
        non_disponibles_text = "<br/>".join(
            joueur["prénom"] for joueur in non_disponibles
        )
        non_disponibles_section.append(
            Paragraph(non_disponibles_text, stylesheets["BodyText"])
        )
    else:
        non_disponibles_section.append(
            Paragraph("Aucun joueur non disponible.", stylesheets["BodyText"])
        )

    # Générer le PDF
    doc.build([table] + non_disponibles_section)
