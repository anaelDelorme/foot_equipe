# main.py
import streamlit as st
import pandas as pd
from team_balancer import balance_teams
from pdf_generator import create_pdf
from utils import get_team_color
import json

def get_draggable_list(team_data, non_disponibles):
    teams_html = """
    <div class="teams-container" style="display: flex; flex-wrap: wrap; gap: 20px;">
    """
    
    for team_name in team_data.keys():
        team_color = get_team_color(list(team_data.keys()).index(team_name), len(team_data))[1]
        
        teams_html += f"""
        <div class="team-box" style="border: 2px solid {team_color}; padding: 10px; min-width: 200px;">
            <h3 style="color: {team_color}">{team_name}</h3>
        """
        
        for subteam_num, players in team_data[team_name].items():
            teams_html += f"""
            <div class="subteam" id="{team_name}-{subteam_num}" 
                 style="border: 1px solid #eee; margin: 10px; padding: 5px;">
                <h4>Sous-équipe {subteam_num}</h4>
                <ul class="sortable-list" style="min-height: 50px; list-style: none; padding: 0;">
            """
            
            for player in players:
                teams_html += f"""
                <li class="sortable-item" data-player='{json.dumps(player)}' 
                    style="padding: 5px; margin: 2px; background: #f0f0f0; cursor: move;">
                    {player['nom']}
                </li>
                """
            
            teams_html += """
                </ul>
            </div>
            """
            
        teams_html += "</div>"
    
    # Ajouter la section des non disponibles
    teams_html += """
    <div class="team-box" style="border: 2px solid #808080; padding: 10px; min-width: 200px;">
        <h3 style="color: #808080">Indisponibles</h3>
        <ul class="sortable-list" style="min-height: 50px; list-style: none; padding: 0;">
    """
    
    for player in non_disponibles:
        teams_html += f"""
        <li class="sortable-item" data-player='{json.dumps(player)}' 
            style="padding: 5px; margin: 2px; background: #f0f0f0; cursor: move;">
            {player['nom']}
        </li>
        """
    
    teams_html += """
        </ul>
    </div>
    </div>
    """
    
    # Ajouter le script Sortable
    teams_html += """
    <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.14.0/Sortable.min.js"></script>
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const lists = document.querySelectorAll('.sortable-list');
        lists.forEach(list => {
            new Sortable(list, {
                group: 'shared',
                animation: 150,
                onEnd: function(evt) {
                    // Mise à jour des données après glisser-déposer
                    updateTeams();
                }
            });
        });
        
        function updateTeams() {
            const newData = {teams: {}, non_disponibles: []};
            
            document.querySelectorAll('.team-box').forEach(teamBox => {
                const teamName = teamBox.querySelector('h3').textContent;
                
                if (teamName === 'Indisponibles') {
                    teamBox.querySelectorAll('.sortable-item').forEach(item => {
                        newData.non_disponibles.push(JSON.parse(item.getAttribute('data-player')));
                    });
                } else {
                    newData.teams[teamName] = {};
                    
                    teamBox.querySelectorAll('.subteam').forEach(subteam => {
                        const subteamNum = parseInt(subteam.id.split('-')[1]);
                        newData.teams[teamName][subteamNum] = [];
                        
                        subteam.querySelectorAll('.sortable-item').forEach(item => {
                            newData.teams[teamName][subteamNum].push(
                                JSON.parse(item.getAttribute('data-player'))
                            );
                        });
                    });
                }
            });
            
            // Envoyer les données mises à jour à Streamlit
            window.Streamlit.setComponentValue(newData);
        }
    });
    </script>
    """
    
    return teams_html

def main():
    st.title("Répartiteur d'équipes")
    
    uploaded_file = st.file_uploader("Choisis un fichier Excel", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        st.write("Aperçu du fichier uploadé :")
        st.dataframe(df)
        
        num_teams = st.slider("Nombre d'équipes", min_value=2, max_value=5, value=2)
        num_subteams = st.slider("Nombre de sous-équipes par équipe", min_value=1, max_value=5, value=2)
        
        if st.button("Générer les équipes"):
            teams, non_disponibles = balance_teams(df, num_teams, num_subteams)
            st.session_state['teams'] = teams
            st.session_state['non_disponibles'] = non_disponibles
        
        # Affichage interactif des équipes
        if 'teams' in st.session_state:
            st.components.v1.html(
                get_draggable_list(st.session_state['teams'], st.session_state['non_disponibles']),
                height=600,
                scrolling=True
            )
            
            # Générer le PDF après la modification
            if st.button("Générer le PDF"):
                create_pdf(st.session_state['teams'], st.session_state['non_disponibles'])
                with open("teams.pdf", "rb") as file:
                    st.download_button(
                        label="Télécharger le PDF des équipes",
                        data=file,
                        file_name="teams.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()