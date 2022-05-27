from api import *
import random

def getNids(etat):
    rep = []
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x, y, 0)
            if info_nid(pos) == etat:
                rep.append(pos)
    return rep


# Fonction appelée au début de la partie.
def partie_init():
    # TODO
    pass


# Fonction appelée à chaque tour.
def jouer_tour():
    for troupe in troupes_joueur(moi()):
        if troupe.inventaire == 0:
            goals = pains()
        else:
            if moi() == 0:
                goals = getNids(etat_nid.JOUEUR_0)
            else:
                goals = getNids(etat_nid.JOUEUR_1)
        if len(goals) > 0:
            goal = goals[0]
            debug_poser_pigeon(goal, pigeon_debug.PIGEON_BLEU)
            path = trouver_chemin(troupe.maman, goal)
            for a in range(PTS_ACTION):
                if a < len(path):
                    r = avancer(troupe.id, path[a])
                    if r != erreur.OK:
                        afficher_erreur(r)



# Fonction appelée à la fin de la partie.
def partie_fin():
    pass
