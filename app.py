import streamlit as st
import pandas as pd
from player import Player
from distribution import distribute_players
from pdf_generator import create_pdf
from utils import get_team_color
import json
import copy

st.set_page_config(page_title="Foot Répartition Equipe", page_icon="⚽", layout="wide")


def get_draggable_list(team_data, non_disponibles):
    teams_html = """
    <div class="teams-container" style="display: flex; flex-wrap: wrap; gap: 20px;">
    """

    for team_name in team_data.keys():
        team_color = get_team_color(
            list(team_data.keys()).index(team_name), len(team_data)
        )[1]

        teams_html += f"""
        <div class="team-box" style="border: 2px solid {team_color}; padding: 10px; min-width: 200px;">
            <h3 style="color: {team_color}"><span class="team-name">{team_name}</span> (<span class="team-average">Calcul en cours...</span>)</h3>
        """

        for subteam_num, players in team_data[team_name].items():
            teams_html += f"""
            <div class="subteam" id="{team_name}-{subteam_num}" 
                 style="border: 1px solid #eee; margin: 10px; padding: 5px;">
                <h4>Sous-équipe {subteam_num} (<span class="subteam-average">Calcul en cours...</span>)</h4>
                <ul class="sortable-list" style="min-height: 50px; list-style: none; padding: 0;">
            """

            for player in players:
                teams_html += f"""
                <li class="sortable-item" data-player='{json.dumps(player)}' 
                    style="padding: 5px; margin: 2px; background: #f0f0f0; cursor: move;">
                    {player['prénom']} ({player['poste']}) - Niveau: {player['niveau']}
                </li>
                """

            teams_html += """
                </ul>
            </div>
            """

        teams_html += "</div>"

    teams_html += """
    <div class="team-box" style="border: 2px solid #808080; padding: 10px; min-width: 200px;">
        <h3 style="color: #808080">Indisponibles</h3>
        <ul class="sortable-list" style="min-height: 50px; list-style: none; padding: 0;">
    """

    for player in non_disponibles:
        teams_html += f"""
        <li class="sortable-item" data-player='{json.dumps(player)}' 
            style="padding: 5px; margin: 2px; background: #f0f0f0; cursor: move;">
            {player['prénom']} ({player['poste']}) - Niveau: {player['niveau']}
        </li>
        """

    teams_html += """
        </ul>
    </div>
    </div>
    """

    # Script JavaScript amélioré avec calcul des moyennes et mise à jour en temps réel
    teams_html += """
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.14.0/Sortable.min.js"></script>
    <script>
    function calculateAverages() {
        document.querySelectorAll('.team-box').forEach(teamBox => {
            if (!teamBox.querySelector('h3').textContent.includes('Indisponibles')) {
                let teamTotal = 0;
                let teamPlayerCount = 0;
                
                teamBox.querySelectorAll('.subteam').forEach(subteam => {
                    let subteamTotal = 0;
                    let playerCount = 0;
                    
                    subteam.querySelectorAll('.sortable-item').forEach(item => {
                        const player = JSON.parse(item.getAttribute('data-player'));
                        subteamTotal += player.niveau;
                        playerCount += 1;
                    });
                    
                    const subteamAverage = playerCount > 0 ? subteamTotal / playerCount : 0;
                    subteam.querySelector('.subteam-average').textContent = 
                        `Moyenne: ${subteamAverage.toFixed(2)}`;
                    
                    teamTotal += subteamTotal;
                    teamPlayerCount += playerCount;
                });
                
                const teamAverage = teamPlayerCount > 0 ? teamTotal / teamPlayerCount : 0;
                                teamBox.querySelector('.team-average').textContent = 
                    `Moyenne: ${teamAverage.toFixed(2)}`;
            }
        });
    }

    function updateTeams() {
        const teamData = {teams: {}, non_disponibles: []};
        
        document.querySelectorAll('.team-box').forEach(teamBox => {
            const teamNameEl = teamBox.querySelector('.team-name');
            if (!teamNameEl) {
                // Boîte des indisponibles
                teamBox.querySelectorAll('.sortable-item').forEach(item => {
                    teamData.non_disponibles.push(JSON.parse(item.getAttribute('data-player')));
                });
            } else {
                const teamName = teamNameEl.textContent;
                teamData.teams[teamName] = {};
                
                teamBox.querySelectorAll('.subteam').forEach(subteam => {
                    const subteamNum = parseInt(subteam.id.split('-')[1]);
                    teamData.teams[teamName][subteamNum] = [];
                    
                    subteam.querySelectorAll('.sortable-item').forEach(item => {
                        teamData.teams[teamName][subteamNum].push(
                            JSON.parse(item.getAttribute('data-player'))
                        );
                    });
                });
            }
        });
        
        // Mettre à jour les moyennes
        calculateAverages();
        
        // Envoi direct à Streamlit
        window.Streamlit.setComponentValue(teamData);
    }

    document.addEventListener('DOMContentLoaded', function() {
        const lists = document.querySelectorAll('.sortable-list');
        lists.forEach(list => {
            new Sortable(list, {
                group: 'shared',
                animation: 150,
                onEnd: updateTeams
            });
        });
        
        calculateAverages();
    });
    </script>
    """
    return teams_html


def main():
    st.title("Répartiteur d'équipes")

    # Initialisation des états de session
    if "initial_teams" not in st.session_state:
        st.session_state.initial_teams = None
    if "initial_non_disponibles" not in st.session_state:
        st.session_state.initial_non_disponibles = None

    uploaded_file = st.file_uploader("Choisis un fichier Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Aperçu du fichier uploadé :")
        st.dataframe(df)

        num_teams = st.slider("Nombre d'équipes", min_value=2, max_value=5, value=3)
        num_subteams = st.slider(
            "Nombre de sous-équipes par équipe", min_value=1, max_value=5, value=2
        )

        if st.button("Générer les équipes"):
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
        if hasattr(st.session_state, "current_teams"):
            # Utilisation du composant HTML avec gestion des modifications
            draggable_component = st.components.v1.html(
                get_draggable_list(
                    st.session_state.current_teams,
                    st.session_state.current_non_disponibles,
                ),
                height=600,
                scrolling=True,
            )

            # Récupération des modifications via le composant
            team_changes = st.experimental_get_query_params()

            if team_changes:
                try:
                    # Convertir les paramètres de requête en données utilisables
                    updated_teams = json.loads(team_changes.get("teams", ["{}"])[0])
                    updated_non_disponibles = json.loads(
                        team_changes.get("non_disponibles", ["[]"])[0]
                    )

                    # Mettre à jour les données de session
                    st.session_state.current_teams = updated_teams
                    st.session_state.current_non_disponibles = updated_non_disponibles

                    # Forcer un rechargement
                    st.experimental_rerun()

                except json.JSONDecodeError:
                    st.error("Erreur de décodage des données d'équipe")

            # Générer le PDF avec les données actuelles
            if st.button("Générer le PDF"):
                create_pdf(
                    st.session_state.current_teams,
                    st.session_state.current_non_disponibles,
                )
                with open("teams.pdf", "rb") as file:
                    st.download_button(
                        label="Télécharger le PDF des équipes",
                        data=file,
                        file_name="teams.pdf",
                        mime="application/pdf",
                    )


if __name__ == "__main__":
    main()
