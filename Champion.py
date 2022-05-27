from api import *
import random


# Fonction appelée au début de la partie.
def partie_init():
    # TODO
    pass


# Fonction appelée à chaque tour.
def jouer_tour():
    for i in range(1, NB_TROUPES+1):
        for _ in range(PTS_ACTION):
            avancer(i, random.choice([direction.NORD, direction.SUD, direction.EST, direction.OUEST]))



# Fonction appelée à la fin de la partie.
def partie_fin():
    # TODO
    pass
