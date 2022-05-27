from api import *

DEBUG = False

"""
idee de strategie:
si pain sur case constructible: poser buisson
"""

def trace(*args):
    if DEBUG:
        print(*args)

def printMap():
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            print(info_case((x,y,0)).contenu, end="")
        print()

def getNids(etat):
    rep = []
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x, y, 0)
            if info_nid(pos) == etat:
                rep.append(pos)
    return rep

def getClosest(orig, positions):
    mini = 0
    for pos in positions:
        d = len(trouver_chemin(orig, pos))
        # trace("d", orig, pos, "=", d)
        if mini == 0 or d < mini:
            mini = d
            sol = pos
    if mini == 0:
        return None
    return sol

def drawPath(orig, path, pigeon):
    x, y, z = orig
    for d in path:
        if d == direction.NORD: y += 1
        if d == direction.SUD: y -= 1
        if d == direction.EST: x += 1
        if d == direction.OUEST: x -= 1
        if d == direction.HAUT: z += 1
        if d == direction.BAS: z -= 1
        debug_poser_pigeon((x,y,z), pigeon)

def reverseDir(d):
    if d == direction.NORD: return direction.SUD
    if d == direction.SUD: return direction.NORD
    if d == direction.EST: return direction.OUEST
    if d == direction.OUEST: return direction.EST
    if d == direction.HAUT: return direction.BAS
    if d == direction.BAS: return direction.HAUT

def findGoal(troupe):
    if troupe.inventaire == 0:
        goals = pains()
        trace("goals = pains =", goals)
    else:
        if moi() == 0:
            goals = getNids(etat_nid.JOUEUR_0)
        else:
            goals = getNids(etat_nid.JOUEUR_1)
        trace("goals = nids =", goals)
        if len(goals) == 0:
            goals = getNids(etat_nid.LIBRE)
    goals = list(set(goals))
    for g in goals:
        debug_poser_pigeon(g, pigeon_debug.PIGEON_JAUNE)
    if len(goals) > 0:
        return getClosest(troupe.maman, goals)
    return None

def goToBestGoal(numTroupe):
    troupe = troupes_joueur(moi())[numTroupe]
    trace("\ntroupe", troupe.id)
    trace('maman', troupe.maman)
    if moi() == 0:
        debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_ROUGE)
    else:
        debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_JAUNE)


    goal = findGoal(troupe)
    trace("goal", goal)
    if goal:
        debug_poser_pigeon(goal, pigeon_debug.PIGEON_BLEU)
        path = trouver_chemin(troupe.maman, goal)
        if DEBUG:
            drawPath(troupe.maman, path, pigeon_debug.PIGEON_JAUNE)
        trace("path", path)
        for a in range(troupe.pts_action):
            if a < len(path):
                r = avancer(troupe.id, path[a])
                if r != erreur.OK:
                    afficher_erreur(r)
            else:
                goToBestGoal(numTroupe)
                return
    else:
        #print("pas de goal :'-(")
        pass


# Fonction appelée au début de la partie.
def partie_init():
    # printMap()
    pass

TOUR = 0
# Fonction appelée à chaque tour.
def jouer_tour():
    global TOUR
    trace("================================ TOUR", TOUR, "================================")
    for numTroupe in range(NB_TROUPES):
        goToBestGoal(numTroupe)
    TOUR += 1



# Fonction appelée à la fin de la partie.
def partie_fin():
    pass
