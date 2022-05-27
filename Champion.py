from api import *
import random


# Fonction appelée au début de la partie.
def partie_init():
    # TODO
    pass


# Fonction appelée à chaque tour.
def jouer_tour():
    for i in range(1, NB_TROUPES+1):
        goal = pains()[0]
        path = trouver_chemin(troupes_joueur(moi())[i-1].maman, goal)
        for a in range(PTS_ACTION):
            if a < len(path):
                avancer(i, path[a])



# Fonction appelée à la fin de la partie.
def partie_fin():
    # TODO
    pass
