import streamlit as st
import pandas as pd
from streamlit_sortables import sort_items
from player import Player
from distribution import distribute_players
from pdf_generator import create_pdf


def main():
    st.title("Répartiteur d'équipes")

    # Initialisation des états de session
    if "teams" not in st.session_state:
        st.session_state.teams = None
    if "non_disponibles" not in st.session_state:
        st.session_state.non_disponibles = None

    # Upload du fichier
    uploaded_file = st.file_uploader("Choisis un fichier Excel", type=["xlsx"])

    if uploaded_file:
        # Lecture du fichier
        df = pd.read_excel(uploaded_file)
        st.dataframe(df)

        # Paramètres de répartition
        col1, col2 = st.columns(2)
        with col1:
            num_teams = st.slider("Nombre d'équipes", 2, 5, 3)
        with col2:
            num_subteams = st.slider("Sous-équipes par équipe", 1, 5, 2)

        # Bouton de génération
        if st.button("Générer les équipes"):
            # Préparation des joueurs
            players = []
            non_disponibles = []

            for _, row in df.iterrows():
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

            # Distribution des joueurs
            distributed_teams = distribute_players(players, num_teams, num_subteams)

            # Formatage des données pour le composant sortable
            sortable_teams = {}
            for team in distributed_teams:
                team_name = f"Équipe {team.team_id + 1}"
                sortable_teams[team_name] = []

                for subteam in team.subteams:
                    sortable_teams[team_name].extend(
                        [
                            {
                                "label": f"{p.prénom} ({p.poste}) - Niveau: {p.niveau}",
                                "value": {
                                    "prénom": p.prénom,
                                    "poste": p.poste,
                                    "niveau": p.niveau,
                                },
                            }
                            for p in subteam
                        ]
                    )

            # Ajout des non disponibles
            sortable_teams["Indisponibles"] = [
                {
                    "label": f"{p['prénom']} ({p['poste']}) - Niveau: {p['niveau']}",
                    "value": p,
                }
                for p in non_disponibles
            ]

            # Sauvegarde dans l'état de session
            st.session_state.sortable_teams = sortable_teams

        # Réorganisation des équipes
        if hasattr(st.session_state, "sortable_teams"):
            st.header("Réorganisation des équipes")

            # Utilisation du composant sortables
            sorted_teams = sort_items(
                st.session_state.sortable_teams,
                title="Glissez et déposez les joueurs",
                multi_select=True,
            )

            # Bouton de mise à jour
            if st.button("Mettre à jour les équipes"):
                # Traitement des équipes triées
                updated_teams = {}
                non_disponibles = []

                for team_name, players in sorted_teams.items():
                    if team_name == "Indisponibles":
                        non_disponibles = [p["value"] for p in players]
                    else:
                        updated_teams[team_name] = {}
                        # Regroupement par sous-équipes (par exemple, 2 sous-équipes)
                        subteam_size = len(players) // num_subteams
                        for i in range(num_subteams):
                            start = i * subteam_size
                            end = start + subteam_size
                            updated_teams[team_name][i + 1] = [
                                p["value"] for p in players[start:end]
                            ]

                # Mise à jour des états de session
                st.session_state.teams = updated_teams
                st.session_state.non_disponibles = non_disponibles

                st.success("Équipes mises à jour !")

            # Affichage des statistiques
            if st.session_state.teams:
                for team_name, subteams in st.session_state.teams.items():
                    st.subheader(team_name)
                    for subteam_num, players in subteams.items():
                        st.write(f"Sous-équipe {subteam_num}")
                        team_df = pd.DataFrame(players)
                        st.dataframe(team_df)

                        # Calcul de la moyenne de niveau
                        niveau_moyen = team_df["niveau"].mean()
                        st.metric(
                            f"Niveau moyen sous-équipe {subteam_num}",
                            f"{niveau_moyen:.2f}",
                        )

                # Bouton PDF
                if st.button("Générer PDF"):
                    create_pdf(st.session_state.teams, st.session_state.non_disponibles)
                    with open("teams.pdf", "rb") as file:
                        st.download_button(
                            label="Télécharger le PDF",
                            data=file,
                            file_name="teams.pdf",
                            mime="application/pdf",
                        )


if __name__ == "__main__":
    main()
