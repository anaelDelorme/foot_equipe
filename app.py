import streamlit as st
import pandas as pd
from player import Player
from distribution import distribute_players
from pdf_generator import create_pdf
from utils import get_team_color
import json
import copy
from streamlit_sortables import sort_items
import random
import io

st.set_page_config(page_title="FCE Répartition Equipe", page_icon="⚽")


def generate_random_data(num_players=20):
    prenoms = [
        "Alice",
        "Béatrice",
        "Clara",
        "Diane",
        "Élodie",
        "Fanny",
        "Gisèle",
        "Hélène",
        "Isabelle",
        "Jade",
        "Karine",
        "Léa",
        "Mélanie",
        "Nathalie",
        "Océane",
        "Pascale",
        "Quentin",
        "Roxane",
        "Sophie",
        "Tatiana",
        "Ursula",
        "Valérie",
        "Wendy",
        "Xavier",
        "Yasmine",
        "Zoé",
    ]
    postes = ["G", "Def", "Mill", "Ailier", "Att"]
    niveaux = [1, 2, 3, 4]
    presences = ["X", ""]

    data = {
        "prénom": [random.choice(prenoms) for _ in range(num_players)],
        "poste": [random.choice(postes) for _ in range(num_players)],
        "niveau": [random.choice(niveaux) for _ in range(num_players)],
        "présence": [random.choice(presences) for _ in range(num_players)],
    }
    return pd.DataFrame(data)


def transform_data(team_data, non_disponibles):
    original_items = []

    # Ajouter les équipes
    for team_index, (team_name, subteams) in enumerate(team_data.items()):
        color_name, _ = get_team_color(team_index, len(team_data))
        for subteam_id, players in subteams.items():
            header = f"{color_name} - {subteam_id}"
            items = [
                f"{player['prénom']} ({player['poste']}, {player['niveau']})"
                for player in players
            ]
            original_items.append({"header": header, "items": items})

    # Ajouter les joueurs non disponibles
    if non_disponibles:
        header = "Non disponibles"
        items = [
            f"{player['prénom']} ({player['poste']}, {player['niveau']})"
            for player in non_disponibles
        ]
        original_items.append({"header": header, "items": items})

    return original_items


def calculate_stats(team_data):
    stats = {}
    for team_name, subteams in team_data.items():
        team_levels = []  # Liste des niveaux pour toute l'équipe
        stats[team_name] = {}
        for subteam_id, players in subteams.items():
            levels = [player["niveau"] for player in players]
            stats[team_name][subteam_id] = {
                "sum": sum(levels),
                "average": sum(levels) / len(levels) if levels else 0,
                "total_players": len(players),
            }
            team_levels.extend(levels)

        stats[team_name]["team"] = {
            "sum": sum(team_levels),
            "average": sum(team_levels) / len(team_levels) if team_levels else 0,
            "total_players": len(team_levels),
        }
    return stats


def main():
    st.title("⚽ Répartiteur d'équipes")

    # Initialisation des états de session
    if "initial_teams" not in st.session_state:
        st.session_state.initial_teams = None
    if "initial_non_disponibles" not in st.session_state:
        st.session_state.initial_non_disponibles = None
    if "team_data" not in st.session_state:
        st.session_state.team_data = None

    # Bouton pour télécharger un modèle de fichier Excel
    if st.button("Générer un modèle de fichier Excel"):
        df = generate_random_data()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Modèle", index=False)
            writer.close()  # Utiliser close au lieu de save
        st.download_button(
            label="Télécharger le modèle",
            data=buffer,
            file_name="modele_excel.xlsx",
            mime="application/vnd.ms-excel",
        )

    uploaded_file = st.file_uploader("Choisis un fichier Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Aperçu du fichier uploadé :")
        st.dataframe(df)

        num_teams = st.slider("Nombre d'équipes", min_value=2, max_value=5, value=3)
        num_subteams = st.slider(
            "Nombre de sous-équipes par équipe", min_value=1, max_value=5, value=2
        )

        if st.button("🚀 Générer les équipes"):
            players = []
            non_disponibles = []
            for index, row in df.iterrows():
                player = Player(
                    prénom=row["prénom"], poste=row["poste"], niveau=row["niveau"]
                )
                if row["présence"] == "X":
                    players.append(player)
                else:
                    non_disponibles.append(
                        {
                            "prénom": row["prénom"],
                            "poste": row["poste"],
                            "niveau": row["niveau"],
                        }
                    )

            teams = distribute_players(players, num_teams, num_subteams)

            team_data = {}
            for team in teams:
                team_name = f"Équipe {team.team_id + 1}"
                team_data[team_name] = {}
                for subteam_id, subteam in enumerate(team.subteams):
                    team_data[team_name][subteam_id + 1] = [
                        {
                            "prénom": player.prénom,
                            "poste": player.poste,
                            "niveau": player.niveau,
                        }
                        for player in subteam
                    ]

            st.session_state.initial_teams = copy.deepcopy(team_data)
            st.session_state.initial_non_disponibles = copy.deepcopy(non_disponibles)
            st.session_state.current_teams = team_data
            st.session_state.current_non_disponibles = non_disponibles

        # Gestion des équipes modifiables
        if "current_teams" in st.session_state:
            # Transformer les données pour streamlit-sortables
            original_items = transform_data(
                st.session_state.current_teams, st.session_state.current_non_disponibles
            )

            # Utilisation du composant streamlit-sortables
            updated_items = sort_items(original_items, multi_containers=True)

            if updated_items:
                # Reconvertir les données en format d'origine
                new_team_data = {}
                non_disponibles = []

                for item in updated_items:
                    header = item["header"]
                    items = item["items"]

                    if "Non disponibles" in header:
                        for player_str in items:
                            prénom, poste_niveau = player_str.split(" (")
                            poste, niveau = poste_niveau.rstrip(")").split(", ")
                            non_disponibles.append(
                                {
                                    "prénom": prénom,
                                    "poste": poste,
                                    "niveau": int(niveau),
                                }
                            )
                    else:
                        team_name, subteam_id = header.split(" - ")
                        if team_name not in new_team_data:
                            new_team_data[team_name] = {}
                        new_team_data[team_name][int(subteam_id)] = []
                        for player_str in items:
                            prénom, poste_niveau = player_str.split(" (")
                            poste, niveau = poste_niveau.rstrip(")").split(", ")
                            new_team_data[team_name][int(subteam_id)].append(
                                {
                                    "prénom": prénom,
                                    "poste": poste,
                                    "niveau": int(niveau),
                                }
                            )

                st.session_state.current_teams = new_team_data
                st.session_state.current_non_disponibles = non_disponibles

            # Afficher les statistiques
            stats = calculate_stats(st.session_state.current_teams)
            st.write("Statistiques des équipes:")
            for team_name, subteams in stats.items():
                team_stats = subteams.pop("team")
                st.write(
                    f"**{team_name}** : "
                    f"{team_stats['total_players']} joueuses - "
                    f"Moyenne : {team_stats['average']:.1f} - "
                    f"Total : {team_stats['sum']}"
                )
                for subteam_id, stat in subteams.items():
                    st.write(
                        f"Sous-équipe {subteam_id} : "
                        f"{stat['total_players']} joueuses - "
                        f"Moyenne : {stat['average']:.1f} - "
                        f"Total : {stat['sum']}"
                    )

            # Générer le PDF avec les données actuelles
            if st.button("⏳ Générer le PDF"):
                create_pdf(
                    st.session_state.current_teams,
                    st.session_state.current_non_disponibles,
                )
                with open("teams.pdf", "rb") as file:
                    st.download_button(
                        label="✅ Télécharger le PDF des équipes",
                        data=file,
                        file_name="teams.pdf",
                        mime="application/pdf",
                    )


if __name__ == "__main__":
    main()
