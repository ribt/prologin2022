from api import *
import random
from time import time

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

def trace(*args):
    if DEBUG:
        print(*args)

logs = ''
def trace2(*args):
    global logs
    logs += " ".join(map(str, args))+"\n"

def caseLibre(pos):
    """ Renvoie True si la case donnee est n'est pas occupee par un obstacle """
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
    """ Renvoie la liste des positions des trous """
    rep = []
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x,y,0)
            if info_case(pos).contenu == type_case.TROU:
                rep.append(pos)
    return rep

def nextPos(orig, d):
    x, y, z = orig
    if d == direction.NORD: y += 1
    if d == direction.SUD: y -= 1
    if d == direction.EST: x += 1
    if d == direction.OUEST: x -= 1
    if d == direction.HAUT: z += 1
    if d == direction.BAS: z -= 1
    return (x, y, z)

def isPosValid(pos):
    x, y, z = pos
    if not 0 <= x < LARGEUR:
        return False
    if not 0 <= y < HAUTEUR:
        return False
    if not -1 <= z <= 0:
        return False
    return True


def getPositionsAdjacentesTete(troupe):
    pos = troupe.maman
    rep = []

    for d in [direction.NORD, direction.SUD, direction.EST, direction.OUEST]:
        if d == reverseDir(troupe.dir):
            continue
        target = nextPos(pos, d)
        if isPosValid(target):
            rep.append(target)
    return rep


# def dessinerTunnels():
#     for y in range(HAUTEUR):
#         for x in range(LARGEUR):
#             pos = (x,y,-1)
#             if info_case(pos).contenu == type_case.TUNNEL:
#                 debug_poser_pigeon(pos, pigeon_debug.PIGEON_JAUNE)


def getPtsActions(numTroupe):
    """ Renvoie le nombre de points d'actions restants actuellement a ma troupe """
    return troupes_joueur(moi())[numTroupe].pts_action
    
def findPainSurConstructible():
    """ Renvoie la liste des positions de pains sur des cases constructibles """
    positions = []
    for pos in set(pains()):
        if info_case(pos).est_constructible:
            positions.append(pos)
    if len(positions) == 0:
        return None
    return random.choice(positions)

def printMap():
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            print(info_case((x,y,0)).contenu, end="")
        print()

def printTunnels():
    """ Affiche le sous sol pour voir les tunnels """
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            if info_case((x,y,-1)).contenu == type_case.TUNNEL:
                print("#", end="")
            else:
                print(" ", end="")
        print()

def getNidsJoueur(joueur, ouLibre):
    """ Renvoie les positions des nids du joueur 'joueur' + les nids a personne si 'ouLibre' """
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
    """ Renvoie les positions des nids n'appartenant a personne et accessibles depuis 'fromPos' """
    rep = []
    nids = getNidsJoueur(None, True)
    for nid in nids:
        if len(trouver_chemin(fromPos, nid)) > 0:
            rep.append(nid)
    return rep


def getClosest(fromPos, positions):
    """ Renvoie la position de 'positions' la plus proche de 'fromPos' """
    mini = 0
    for pos in positions:
        d = len(trouver_chemin(fromPos, pos))
        trace("d", fromPos, pos, "=", d)
        if d > 0 and (mini == 0 or d < mini):
            mini = d
            sol = pos
    if mini == 0:
        return None
    return sol

def drawPath(orig, path, pigeon):
    """ Dessine le chemin avec des pigeons de couleur """
    pos = orig
    for d in path:
        pos = nextPos(pos, d)
        debug_poser_pigeon(pos, pigeon)

def reverseDir(d):
    """ Renvoie la direction opposee a 'd' """
    if d == direction.NORD: return direction.SUD
    if d == direction.SUD: return direction.NORD
    if d == direction.EST: return direction.OUEST
    if d == direction.OUEST: return direction.EST
    if d == direction.HAUT: return direction.BAS
    if d == direction.BAS: return direction.HAUT

def findGoal(troupe):
    """ Cherche un objectif a atteindre """
    if troupe.inventaire < troupe.taille//3:            # si l'inventaire n'est pas plein on cherche un pain
        goals = pains()
        trace("goals = pains =", goals)
        if len(goals) == 0:                             # si pas de pain on cherche un papy
            goals = papys
            trace("goals = papys =", goals)
    else:                                               # si l'inventaire est plein on cherche un nid a moi ou libre
        goals = getNidsJoueur(moi(), True)
        trace("goals = nids =", goals)

    goals = list(set(goals))                            # supprimer les doublons
    goals = [pos for pos in goals if caseLibre(pos)]    # supprimer les cases innacessibles a ce moment (patch trouver_chemin)
    if DEBUG:
        for g in goals:
            debug_poser_pigeon(g, pigeon_debug.PIGEON_JAUNE)
    if len(goals) > 0:
        return getClosest(troupe.maman, goals)          # aller au plus proche
    return None

def goToBestGoal(numTroupe):
    """ Recuperer l'objectif et avancer dans sa direction """
    troupe = troupes_joueur(moi())[numTroupe]
    trace("\ntroupe", troupe.id)
    trace('maman', troupe.maman)

    goal = findGoal(troupe)
    trace("goal", goal)
    if goal:
        debug_poser_pigeon(goal, pigeon_debug.PIGEON_BLEU)
        path = trouver_chemin(troupe.maman, goal)
        if DEBUG:
            drawPath(troupe.maman, path, pigeon_debug.PIGEON_JAUNE)
        trace("path", path)
        for a in range(troupe.pts_action):          # on avance tant qu'on a des points d'action
            if a < len(path):
                r = avancer(troupe.id, path[a])
                if r != erreur.OK:
                    afficher_erreur(r)
            else:                                   # appel recursif si objectif atteint mais reste points d'actions
                goToBestGoal(numTroupe)
                return
    else:
        trace("pas de goal :'-(")

def prendreNids(numTroupe):
    """ Cherche le nid libre le plus proche et se dirige vers lui """
    troupe = troupes_joueur(moi())[numTroupe]
    goals = getNidsLibresAccessibles(troupe.maman)
    goal = getClosest(troupe.maman, goals)
    if goal:
        path = trouver_chemin(troupe.maman, goal)
        for a in range(troupe.pts_action):          # on avance tant qu'on a des points d'action
            if a < len(path):
                r = avancer(troupe.id, path[a])
                if r != erreur.OK:
                    afficher_erreur(r)
            else:                                   # appel recursif si objectif atteint mais reste points d'actions
                prendreNids(numTroupe)
                return

def grandirEtAvancer(numTroupe):
    """ Si taille de la troupe inferieure a taille optimale, grandit de 1 puis va a l'objectif """
    troupe = troupes_joueur(moi())[numTroupe]
    if troupe.taille < TAILLE_OPTIMALE:
        grandir(troupe.id)
    goToBestGoal(numTroupe)

def consommerPtsActions(numTroupe):
    """ Consomme les points d'actions restant moins betement qu'en foncant tout droit """
    troupe = troupes_joueur(moi())[numTroupe]

    for _ in range(450):            # si possible, aller vers une case random
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
            # consommerPtsActions(numTroupe)
            return

def getScorePos(pos):
    """ Calcule un score d'interet pour une position, base sur le nombre de papys proches """
    score = 0
    for papy in papys:
        if pos == papy:
            score += 3
        d = len(trouver_chemin(pos, papy))
        if d > 0:
            score += 1/d
    return score

def getBestScore(positions):
    """ Renvoie la position de la liste avec le plus gros score """
    maxi = getScorePos(positions[0])
    best = positions[0]
    for pos in positions[1:]:
        s = getScorePos(pos)
        if s > maxi:
            maxi = s
            best = pos
    return best

def genererCarteTunnels(troupe):
    trace('genererCarteTunnels')
    aCreuser[troupe.id] = []
    trous = getTrous()
    if len(trous) > 1:              # fait un tunnel entre le spawn initial de chaque troupe et le point le plus rentable
        departTunnel = getClosest(troupe.maman, trous)
        if departTunnel:
            trous.remove(departTunnel)
            arriveeTunnel = getBestScore(trous)
            
            for x in range(min(departTunnel[0], arriveeTunnel[0]), max(departTunnel[0],arriveeTunnel[0])+1):
                aCreuser[troupe.id].append((x, departTunnel[1], -1))
            for y in range(min(departTunnel[1],arriveeTunnel[1]), max(departTunnel[1],arriveeTunnel[1])+1):
                aCreuser[troupe.id].append((arriveeTunnel[0], y, -1))
    # aCreuser[troupe.id] = list(set(aCreuser[troupe.id]))
    for p in aCreuser[troupe.id]:
        debug_poser_pigeon(p, pigeon_debug.PIGEON_ROUGE)
    trace("aCreuser", troupe.id, aCreuser[troupe.id])

papys = []
aCreuser = {}
# Fonction appelée au début de la partie.
def partie_init():
    """ Remplit la liste des papys et les cases a creuser """
    global papys, aCreuser
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x, y, 0)
            if info_case(pos).contenu == type_case.PAPY:
                papys.append(pos)

    for troupe in troupes_joueur(moi()):
        aCreuser[troupe.id] = []
        # genererCarteTunnels(troupe)

def creuser():
    for _ in range(FREQ_TUNNEL):                            # creuse les cases restantes a creuser
        r = erreur.NON_CREUSABLE
        cases = aCreuser[troupes_joueur(moi())[TOUR%2].id]
        while r == erreur.NON_CREUSABLE and len(cases) > 0:
            c = cases.pop()
            r = creuser_tunnel(c)
            # print("creuse", c, r)
        cases = aCreuser[troupes_joueur(moi())[TOUR%2 - 1].id]
        while r == erreur.NON_CREUSABLE and len(cases) > 0:
            c = cases.pop()
            r = creuser_tunnel(c)
            # print("creuse", c, r)

def attaquer():
    if score(moi()) < 100:
        trace("score trop faible :", score(moi()))
        return

    # print(troupes_joueur(adversaire()))
    for troupe in troupes_joueur(adversaire()):
        # if troupe.inventaire < 7:
        #     continue
        targets = getPositionsAdjacentesTete(troupe)
        # print(targets)
        trace([info_case(target) for target in targets])
        if all([(not caseLibre(target) or info_case(target).est_constructible) for target in targets]):
            for target in targets:
                trace(construire_buisson(target))

TOUR = -1
trolling = 0
debut = 0
# Fonction appelée à chaque tour.
def jouer_tour():
    global TOUR, trolling, logs, debut
    debut = time()
    logs = ''
    TOUR += 1
    trace("\n================================ TOUR", TOUR, "================================")

    creuser()
    trace2("fin creuser", time()-debut)

    attaquer()
    trace2("fin attaquer", time()-debut)

    if DEBUG:
        # dessinerTunnels()
        printTunnels()
    for numTroupe, troupe in enumerate(troupes_joueur(moi())):
        trace2("\ntroupe", troupe.id)
        if moi() == 0:
            debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_ROUGE)
        else:
            debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_BLEU)

        if troupe.taille == 1:                 # je viens de respawn
            genererCarteTunnels(troupe)

        mesNids = getNidsJoueur(moi(), False)
        if len(mesNids) < 2:                   # fonce prendre 2 nids au debut
            prendreNids(numTroupe)

        trace2("fin getNids", time()-debut)

        if getPtsActions(numTroupe) > 0:       # atteint taille optimale puis prend des pains et les ramene au nid
            grandirEtAvancer(numTroupe)

        trace2("fin grandirEtAvancer", time()-debut)

        if getPtsActions(numTroupe) > 0:       # eviter de finir en tout droit
            consommerPtsActions(numTroupe)

        trace2("fin consommerPtsActions", time()-debut)

        if getPtsActions(numTroupe) > 0:
            print("LOSER")

        if trolling < 10:                       # mettre des buissons sous les pains pour tromper ceux qui utilisent trouver_chemin
            pos = findPainSurConstructible()
            if pos:
                if construire_buisson(pos) == erreur.OK:
                    trolling += 1

        trace2("FINI", time()-debut)

    chrono = time()-debut

    if chrono > 0.2:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!! risque TO:", chrono)
        print(logs)





# Fonction appelée à la fin de la partie.
def partie_fin():
    pass
