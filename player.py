from dataclasses import dataclass


@dataclass
class Player:
    prénom: str
    poste: str  # G, D, Att, Ail, Mil
    niveau: int  # 1 à 4
    
myplayer = Player("Zinédine", "Att", 4)
print(f"Mon player est {myplayer.prénom}, son poste est {myplayer.poste} et son niveau est {myplayer.niveau}.")
