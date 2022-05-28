from api import *
import random

DEBUG = False

TAILLE_OPTIMALE = 21

"""
idee de strategie:
si pain sur case constructible: poser buisson


problemes:
- si la troupe ne peut acceder a un point elle devrait pouvoir faire un gros demi tour
- si tous ses nids sont occupes et que l'inventaire est plein elle ne fait rien
au debut:
foncer prendre quelques nids
"""

def caseLibre(pos):
    typeCase = info_case(pos).contenu
    if typeCase in [type_case.BUISSON, type_case.TERRE]:
        return False 
    if typeCase == type_case.BARRIERE and info_barriere(pos) == etat_barriere.FERMEE:
        return False
    for j in [moi(), adversaire()]:
        for troupe in troupes_joueur(j):
            for canard in troupe.canards:
                if pos == canard:
                    return False
    return True

def getTrous():
    rep = []
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x,y,0)
            if info_case(pos).contenu == type_case.TROU:
                rep.append(pos)
    return rep


def getPtsActions(numTroupe):
    return troupes_joueur(moi())[numTroupe].pts_action
    
def findPainSurConstructible():
    positions = []
    for pos in set(pains()):
        if info_case(pos).est_constructible:
            positions.append(pos)
    if len(positions) == 0:
        return None
    return random.choice(positions)

def trace(*args):
    if DEBUG:
        print(*args)

def printMap():
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            print(info_case((x,y,0)).contenu, end="")
        print()

def printTunnels():
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            if info_case((x,y,-1)).contenu == type_case.TUNNEL:
                print("#", end="")
            else:
                print(" ", end="")
        print()

def getNidsJoueur(joueur, ouLibre):
    rep = []
    etats = []
    if joueur == 0:
        etats = [etat_nid.JOUEUR_0]
    if joueur == 1:
        etats = [etat_nid.JOUEUR_1]
    if ouLibre:
        etats.append(etat_nid.LIBRE)
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x, y, 0)
            if info_nid(pos) in etats:
                rep.append(pos)
    return rep

def getNidsLibresAccessibles(fromPos):
    rep = []
    nids = getNidsJoueur(None, True)
    for nid in nids:
        if len(trouver_chemin(fromPos, nid)) > 0:
            rep.append(nid)
    return rep


def getClosest(orig, positions):
    mini = 0
    for pos in positions:
        d = len(trouver_chemin(orig, pos))
        trace("d", orig, pos, "=", d)
        if d > 0 and (mini == 0 or d < mini):
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
    if troupe.inventaire < troupe.taille//3:
        goals = pains()
        trace("goals = pains =", goals)
        if len(goals) == 0:
            goals = papys
            trace("goals = papys =", goals)
    else:
        goals = getNidsJoueur(moi(), True)
        trace("goals = nids =", goals)

    goals = list(set(goals))
    goals = [pos for pos in goals if caseLibre(pos)]
    for g in goals:
        debug_poser_pigeon(g, pigeon_debug.PIGEON_JAUNE)
    if len(goals) > 0:
        return getClosest(troupe.maman, goals)
    return None

def goToBestGoal(numTroupe):
    troupe = troupes_joueur(moi())[numTroupe]
    trace("\ntroupe", troupe.id)
    trace('maman', troupe.maman)

    goal = findGoal(troupe)
    trace("goal", goal)
    if goal:
        debug_poser_pigeon(goal, pigeon_debug.PIGEON_BLEU)
        path = trouver_chemin(troupe.maman, goal)
        # if DEBUG:
        #     drawPath(troupe.maman, path, pigeon_debug.PIGEON_JAUNE)
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
        trace("pas de goal :'-(")

def prendreNids(numTroupe):
    troupe = troupes_joueur(moi())[numTroupe]
    goals = getNidsLibresAccessibles(troupe.maman)
    goal = getClosest(troupe.maman, goals)
    if goal:
        path = trouver_chemin(troupe.maman, goal)
        for a in range(troupe.pts_action):
            if a < len(path):
                r = avancer(troupe.id, path[a])
                if r != erreur.OK:
                    afficher_erreur(r)
            else:
                prendreNids(numTroupe)
                return

def grandirEtAvancer(numTroupe):
    troupe = troupes_joueur(moi())[numTroupe]
    if troupe.taille < TAILLE_OPTIMALE:
        grandir(troupe.id)
    goToBestGoal(numTroupe)

def consommerPtsActions(numTroupe):
    troupe = troupes_joueur(moi())[numTroupe]

    for _ in range(HAUTEUR*LARGEUR):
        x = random.randrange(LARGEUR)
        y = random.randrange(HAUTEUR)
        path = trouver_chemin(troupe.maman, (x, y, 0))
        if len(path) > 0:
            break

    for a in range(troupe.pts_action):
        if a < len(path):
            r = avancer(troupe.id, path[a])
            if r != erreur.OK:
                afficher_erreur(r)
        else:
            consommerPtsActions(numTroupe)
            return

def getScorePos(pos):
    score = 0
    for papy in papys:
        if pos == papy:
            score += 3
        d = len(trouver_chemin(pos, papy))
        if d > 0:
            score += 1/d
    return score

def getBestScore(positions):
    maxi = getScorePos(positions[0])
    best = positions[0]
    for pos in positions[1:]:
        s = getScorePos(pos)
        if s > maxi:
            maxi = s
            best = pos
    return best

papys = []
aCreuser = []
# Fonction appelée au début de la partie.
def partie_init():
    global papys, aCreuser
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x, y, 0)
            if info_case(pos).contenu == type_case.PAPY:
                papys.append(pos)


    trous = getTrous()
    for troupe in troupes_joueur(moi()):
        if len(trous) > 1:
            departTunnel = getClosest(troupe.maman, trous)
            trous.remove(departTunnel)
            arriveeTunnel = getBestScore(trous)

            for x in range(min(departTunnel[0],arriveeTunnel[0]), max(departTunnel[0],arriveeTunnel[0])+1):
                aCreuser.append((x, departTunnel[1], -1))
            for y in range(min(departTunnel[1],arriveeTunnel[1]), max(departTunnel[1],arriveeTunnel[1])+1):
                aCreuser.append((x, y, -1))
    aCreuser = list(set(aCreuser))
    trace(aCreuser)


TOUR = 0
trolling = 0
# Fonction appelée à chaque tour.
def jouer_tour():
    global TOUR, trolling
    trace("================================ TOUR", TOUR, "================================")
    for _ in range(FREQ_TUNNEL):
        if len(aCreuser) > 0:
            r = creuser_tunnel(aCreuser.pop())
            if r != erreur.OK:
                    afficher_erreur(r)
    if DEBUG:
        printTunnels()
    for numTroupe, troupe in enumerate(troupes_joueur(moi())):
        if moi() == 0:
            debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_ROUGE)
        else:
            debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_BLEU)

        mesNids = getNidsJoueur(moi(), False)
        if len(mesNids) < 2:
            prendreNids(numTroupe)

        if getPtsActions(numTroupe) > 0:
            grandirEtAvancer(numTroupe)

        if getPtsActions(numTroupe) > 0:
            consommerPtsActions(numTroupe)

        if getPtsActions(numTroupe) > 0:
            print("LOSER")

        if trolling < 10:
            pos = findPainSurConstructible()
            if pos:
                if construire_buisson(pos) == erreur.OK:
                    trolling += 1
        
    TOUR += 1



# Fonction appelée à la fin de la partie.
def partie_fin():
    pass
