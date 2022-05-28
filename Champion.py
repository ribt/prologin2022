from api import *
import random
from time import time

"""
Strategie globale :
- se deplacer tres vite au debut pour conquerir deux nids (si possible)
- creuser un tunnel entre le spawn de chaque troupe et le trou avec le plus de papys autour (regenerer la carte des tunnels a creuser en cas de respawn)
- grossir si la taille est inferieure a 21 (pouvoir porter 7 pains)
- aller vers le pain le plus proche ou le nid le plus proche si l'inventaire est plein
- s'il reste des points d'action a la fin du tour, choisir un case au hasard et se diriger vers elle
- si mon score est superieur a 100, essayer d'entourer la tete des mamans adverses pour les bloquer

Et la super technique secrete :
- Si possible, placer 10 buissons SOUS des pains pour tromper ceux qui utilisent trouver_chemin
"""


########################## fonctions de debug ##########################

##### Variables de debug globales #####
DEBUG = False    # affiche plein d'infos dans la console et sur la carte avec des pigeons       
logs = ''        # stocke des infos a afficher si le temps d'execution se rapproche du TO

def trace(*args):
    if DEBUG:
        print(*args)


def trace2(*args):
    global logs
    logs += " ".join(map(str, args))+"\n"

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

def drawPath(orig, path, pigeon):
    """ Dessine le chemin avec des pigeons de couleur """
    pos = orig
    for d in path:
        pos = nextPos(pos, d)
        debug_poser_pigeon(pos, pigeon)
########################## fin des fonctions de debug ##########################


########################## fonction utilitaires ##########################
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
    """ Renvoie la position a cote de 'orig' dans la direction 'd' """
    x, y, z = orig
    if d == direction.NORD: y += 1
    if d == direction.SUD: y -= 1
    if d == direction.EST: x += 1
    if d == direction.OUEST: x -= 1
    if d == direction.HAUT: z += 1
    if d == direction.BAS: z -= 1
    return (x, y, z)

def isPosValid(pos):
    """ Renvoie True si la case n'est pas en dehors de la map """
    x, y, z = pos
    if not 0 <= x < LARGEUR:
        return False
    if not 0 <= y < HAUTEUR:
        return False
    if not -1 <= z <= 0:
        return False
    return True

def getPositionsAdjacentesTete(troupe):
    """ Renvoie les trois positions devant la tete d'une maman """
    pos = troupe.maman
    rep = []

    for d in [direction.NORD, direction.SUD, direction.EST, direction.OUEST]:
        if d == reverseDir(troupe.dir):
            continue
        target = nextPos(pos, d)
        if isPosValid(target):
            rep.append(target)
    return rep

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

def getNidsJoueur(joueur, ouLibre):
    """ Renvoie les positions des nids du joueur 'joueur' + les nids libres si 'ouLibre' """
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
    """ Renvoie la position de la liste 'positions' la plus proche de 'fromPos' """
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

def reverseDir(d):
    """ Renvoie la direction opposee a 'd' """
    if d == direction.NORD: return direction.SUD
    if d == direction.SUD: return direction.NORD
    if d == direction.EST: return direction.OUEST
    if d == direction.OUEST: return direction.EST
    if d == direction.HAUT: return direction.BAS
    if d == direction.BAS: return direction.HAUT

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
########################## fin des fonction utilitaires ##########################


########################## fonctions strategiques ##########################
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
        return getClosest(troupe.maman, goals)          # trouver le plus proche
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
    """ Si la taille de la troupe inferieure a taille optimale, grandit de 1 puis va a l'objectif """
    troupe = troupes_joueur(moi())[numTroupe]
    if troupe.taille < TAILLE_OPTIMALE:
        grandir(troupe.id)
    goToBestGoal(numTroupe)

def consommerPtsActions(numTroupe):
    """ Consomme les points d'actions restant moins betement qu'en foncant tout droit """
    troupe = troupes_joueur(moi())[numTroupe]

    for _ in range(450):                            # si possible, aller vers une case random (450 = valeur magique evitant le TO)
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
            # consommerPtsActions(numTroupe)        # pas d'appel recursif cette fois-ci
            return

def genererCarteTunnels(troupe):
    """ Genere la carte a creuser : faire un tunnel entre le trou le plus proche du spawn de la troupe et celui avec le plus de papys autour """
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
    if DEBUG:
        for p in aCreuser[troupe.id]:
            debug_poser_pigeon(p, pigeon_debug.PIGEON_ROUGE)
    trace("aCreuser", troupe.id, aCreuser[troupe.id])

def creuser():
    """ Creuse une fois sur deux le tunnel de chaque troupe """
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
    """ Essaye d'entourer la tete des mamans adverses de buissons (si mon score est superieur a 100) """
    if score(moi()) < 100:
        trace("score trop faible :", score(moi()))
        return

    for troupe in troupes_joueur(adversaire()):
        # if troupe.inventaire < 7:
        #     continue
        targets = getPositionsAdjacentesTete(troupe)
        trace([info_case(target) for target in targets])
        if all([(not caseLibre(target) or info_case(target).est_constructible) for target in targets]):
            for target in targets:
                trace(construire_buisson(target))
########################## fin des fonctions strategiques ##########################


########################## fonctions de l'API ##########################

##### Variables globales #####
TAILLE_OPTIMALE = 21    # taille max des troupes
papys = []              # liste des positions des papys
aCreuser = {}           # dico associant la liste des cases a creuser au troupe.id
TOUR = -1               # tour de jeu (de 0 a 199)
trolling = 0            # compteur de buissons poses sous les pains pour blaguer
debut = 0               # heure de lancement du tour de jeu (utilise pour debug seulement)

def partie_init():
    """ Appelée au début de la partie, remplit la liste des papys et initialise aCreuser (sera remplie par les troupes sur les cases de spawn) """
    global papys, aCreuser
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            pos = (x, y, 0)
            if info_case(pos).contenu == type_case.PAPY:
                papys.append(pos)

    for troupe in troupes_joueur(moi()):
        aCreuser[troupe.id] = []


def jouer_tour():
    """ Fonction appelée à chaque tour """
    global TOUR, trolling, logs, debut
    debut = time()
    logs = ''
    TOUR += 1
    trace("\n================================ TOUR", TOUR, "================================")

    for troupe in troupes_joueur(moi()):
         if troupe.taille == 1:            # je viens de respawn
            genererCarteTunnels(troupe)

    creuser()
    trace2("fin creuser", time()-debut)

    attaquer()
    trace2("fin attaquer", time()-debut)

    if DEBUG:
        # dessinerTunnels()
        printTunnels()
    for numTroupe, troupe in enumerate(troupes_joueur(moi())):
        trace2("\ntroupe", troupe.id)
        if moi() == 0:                         # pose un pigeon de couleur pour identifier quel joueur je joue
            debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_ROUGE)
        else:
            debug_poser_pigeon(troupe.maman, pigeon_debug.PIGEON_BLEU)

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


def partie_fin():
    """ Fonction appelée à la fin de la partie """
    pass
########################## fin des fonctions de l'API ##########################