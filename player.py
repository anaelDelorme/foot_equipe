from dataclasses import dataclass


@dataclass
class Player:
    prénom: str
    poste: str  # G, D, Att, Ail, Mil
    niveau: int  # 1 à 4
    
