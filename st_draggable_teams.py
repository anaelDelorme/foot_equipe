import os
import streamlit.components.v1 as components
import streamlit as st

# Construct the absolute path to the frontend build directory
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend", "build")

# Create the component
_component_func = components.declare_component("st_draggable_teams", path=frontend_dir)


def st_draggable_teams(teams, non_disponibles):
    """
    Create a draggable teams component

    Parameters:
    -----------
    teams : dict
        Dictionary of teams and their players
    non_disponibles : list
        List of unavailable players

    Returns:
    --------
    dict or None
        Updated team configuration
    """
    component_value = _component_func(
        team_data=teams,
        non_disponibles=non_disponibles,
        key="draggable_teams_component",
    )
    return component_value
