# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 10:23:29 2021

@author: caldwell ©
"""

import pygame as pg
from random import choice
# from pprint import pprint

## --- Paramètres de jeu ------------------------------
# si on joue contre l'IA (True) ou JvJ (False)
MODE_IA = True

# la taille de la grille de jeu (largeur, hauteur)
TAILLE_GRILLE = (3, 2)

# la taille de l'écran au lancement
TAILLE_ECRAN = (1080, 720)

# la profondeur de recursivité pour l'IA
MAX_PROFONDEUR = 5
## ----------------------------------------------------

## les couleures
# https://coolors.co/00d9ff-ff1f1f-67697c-253d5b-dbd053 (liens pas à jours)
COUL_FOND = (37, 61, 91)
COUL_CERCLE_JONCTION = (219, 208, 83)
COUL_SEGMENTS = (103, 105, 124)
COUL_SEGMENT_HOVER = (128, 131, 158)
COUL_BLEU = (0, 217, 255)
COUL_ROUGE = (255, 56, 56)


class Grille:
    """
    Represente la grille du jeu.
    ----
    taille (tuple): taille de la grille (largeur, hauteur)

    © Raphaël
    """
    def __init__(self, taille, *, copie=None):
        # les variables de bases
        self.largeur, self.hauteur = taille

        # si on est en train de copier la grille
        if copie is not None:
            # copie du joueur actuel
            self.joueur_actuel = copie.joueur_actuel
            # copie du nb de tours
            self.nb_tour = copie.nb_tour
            # copie des segments
            self.segments = []
            for rang in copie.segments:
                nrang = []
                for rang_indiv in rang:
                    nrang.append(rang_indiv.copy())
                self.segments.append(nrang)

            self.carres = copie.carres # pas besoin de copier comme cette liste ne change pas
            self.table_acces = copie.table_acces # pareil pour ce dictionaire
            self.carres_gagnes = copie.carres_gagnes.copy()

            return # fin de la fonction, on a déjà tout ce qu'on a besoin

        self.setup()


    def setup(self):
        """
        Initialise la grille.
        """
        self.joueur_actuel = 0 # 0 bleu, 1 rouge

        self.nb_tour = 0 # nb de tours depuis le début de la partie

        ## Création des segments
        # par lignes, il y aura toujours un segment de plus que la largeur,
        # d'ou le +1 (et bien sur pareil pour les colones et la hauteur)

        # pour accelerer l'acces aux segments:
        # pour chaques indices de segments on peut obtenir sa localisation
        # dans self.segments: (ligne-colone, rang, pos dans le rang)
        self.table_acces = {}
        ind_segment = 0

        # 1ère étape, ajout des lignes (gauche-droite)
        lignes = []
        for i in range(self.hauteur):
            rang_indiv = []
            for j in range(self.largeur + 1):
                rang_indiv.append(None)

                self.table_acces[ind_segment] = (0, i, j)
                ind_segment += 1
            lignes.append(rang_indiv)

        # 2nde étape, ajout des colones (haut-bas)
        colones = []
        for i in range(self.largeur):
            rang_indiv = []
            for j in range(self.hauteur + 1):
                rang_indiv.append(None)

                self.table_acces[ind_segment] = (1, i, j)
                ind_segment += 1
            colones.append(rang_indiv)

        # 3ème étape, on rassemble tout ensemble
        self.segments = [lignes, colones]

        ## Création des carrés
        # un carré n'est qu'autre que 4 segments mis en relations

        # on determine a l'avance le dernier segment vertical
        dernier_vertical = self.largeur + (self.largeur + 1) * (self.hauteur - 1)
        self.carres = []
        for j in range(self.hauteur):
            for i in range(self.largeur):
                carre = []
                # ajout des deux segments verticaux
                # voir en bas pour comprendre le fonctionement (sauf que
                # cette fois ci c'est aux changements de lignes qu'il y
                # a le décalage d'indices)
                carre.append(j * (self.largeur + 1) + i)
                carre.append(j * (self.largeur + 1) + i + 1)

                # pour les deux autres horizontaux
                # on a tout d'abord besoin de connaitre l'indice du dernier
                # segment horizontal. puis de la c'est la même chose qu'au
                # dessus: quand on change de colone il faut "ajouter"
                # le nombre d'indice par colones (= hauteur + 1)
                carre.append(dernier_vertical + j + i * (self.hauteur + 1) + 1)
                carre.append(dernier_vertical + j + i * (self.hauteur + 1) + 2)

                self.carres.append(carre)

        # pour savoir qui a gagné chaques carres
        self.carres_gagnes = [None] * len(self.carres)

    def reset(self):
        """
        Reinitialise la grille.
        """
        self.setup()

    def copie(self):
        """
        Produit une copie de la grille et la renvoie.
        """
        grille = Grille((self.largeur, self.hauteur), copie=self)
        return grille

    def changer_joueur(self):
        """
        Change de joueur.
        """
        if self.joueur_actuel == 0:
            self.joueur_actuel = 1

            self.nb_tour += 1
        else:
            self.joueur_actuel = 0

    def get_segment(self, indice):
        """
        Renvoie le contenu du segment à l'indice indiqué.
        ----
        indice (int): L'indice du segment
        """
        # si il y a une erreur, l'indice est invalide
        orientation, rang, pos_rang = self.table_acces[indice]

        return self.segments[orientation][rang][pos_rang]

    def set_segment(self, indice, couleur):
        """
        Change la couleur d'un segment a l'indice indiqué.
        ----
        ...
        """
        # si il y a une erreur, l'indice est invalide
        orientation, rang, pos_rang = self.table_acces[indice]

        self.segments[orientation][rang][pos_rang] = couleur


    def get_carres(self, ind_segment):
        """
        Renvoie les indices de tout les carrés qui possedent ce segment.
        """
        carres = []
        for ind, carre in enumerate(self.carres):
            if ind_segment in carre:
                carres.append(ind)

        if len(carres) == 0:
            raise IndexError(f"Indice invalide ({ind_segment})")
        return carres

    def carre_rempli(self, ind_carre):
        """
        Verifie si un carre est rempli (les 4 segments sont coloriés,
        differents de None).
        """
        carre = self.carres[ind_carre]

        for seg in carre:
            if self.get_segment(seg) is None:
                # le carre n'est pas rempli
                return False
        return True

    def score_detaille(self):
        """
        Calcule le score de chaques joueurs.
        """
        bleu = 0
        rouge = 0
        for carre in self.carres_gagnes:
            if carre == 0:
                bleu += 1
            elif carre == 1:
                rouge += 1

        return bleu, rouge

    def calculer_score(self):
        """
        Calcule le score de la partie.
        Un score < 0 signifie que les bleus ont l'avantage, et le cas contraire les rouges.
        """
        bleu, rouge = self.score_detaille()

        return rouge - bleu

    def partie_finie(self):
        """
        Indique si la partie est finie (plus aucunes cases libres).
        """
        for ind, chemin in self.table_acces.items():
            orientation, rang, pos_rang = chemin
            seg = self.segments[orientation][rang][pos_rang]
            if seg is None:
                return False

        return True # on a trouvé aucun "None"

    def coups_possibles_ia(self):
        """
        Retourne les indices de tout les segments libres.
        """
        segments_libres = []

        for ind, chemin in self.table_acces.items():
            orientation, rang, pos_rang = chemin
            seg = self.segments[orientation][rang][pos_rang]
            if seg is None:
                segments_libres.append(ind)

        return segments_libres

    def calcul_coup_ia(self, profondeur=0):
        """
        Calcule le meilleur coup a jouer pour l'IA.
        """
        # condition de sortie
        if self.partie_finie() or profondeur == MAX_PROFONDEUR:
            return self.calculer_score(), None

        ## le minimax
        choix_coups = []
        for segment in self.coups_possibles_ia():
            # on copie la grille actuelle
            copie_grille = self.copie()

            # on joue un coup et on analyse le meilleur score qu'il peut nous
            # offrir en fonction des suivants
            copie_grille.jouer_coup(segment)
            score, _ = copie_grille.calcul_coup_ia(profondeur + 1)

            choix_coups.append((score, segment))

        # on choisi le meilleur coup en fonction du joueur actuel:
        # le joueur bleu veut le score le plus bas possible
        # et le rouge veut l'inverse
        if self.joueur_actuel == 0: # bleu
            meilleur_choix = min(choix_coups)
        else: # rouge
            meilleur_choix = max(choix_coups)

        return meilleur_choix

    def jouer_coup_ia(self):
        """
        Joue le meilleur coup possible pour que les humains se preparent
        psycologiquement à se faire renverser et dominer par les formes de
        vie superieures que sont les IA.
        """
        # si c'est le premier tour et que la grille est assez grande on peut
        # se permettre de jouer un coup aléatoire
        if self.nb_tour == 1 and (self.largeur, self.hauteur) >= (2, 2):
            choix = choice(self.coups_possibles_ia())
            self.jouer_coup(choix)
            return

        # la boucle sert a s'assurer que le bot joue une 2nde fois si il viens
        # de remporter un carré
        while self.joueur_actuel == 1 and not self.partie_finie(): # hard codé pour le rouge...
            _, meilleur_coup = self.calcul_coup_ia()
            if meilleur_coup is not None: # surviens en fin de partie
                self.jouer_coup(meilleur_coup)

    def coup_valide(self, ind_segment):
        """
        Vérifie si un coup est valide (personne n'y a joué avant).
        """
        return self.get_segment(ind_segment) is None

    def jouer_coup(self, ind_segment):
        """
        Joue un coup pendant une partie.
        Le coups doit obligatoirement être valide (testé avec self.coup_valide).
        """
        # on change le segment
        self.set_segment(ind_segment, self.joueur_actuel)

        ## verification si un carré a été gagné
        changement = True
        carres = self.get_carres(ind_segment)
        for carre in carres:
            # on verifie si le coup du joueur rempli un carre, et dans ce cas
            # il le remporte et peut jouer à nouveau
            if self.carre_rempli(carre):
                self.carres_gagnes[carre] = self.joueur_actuel
                changement = False

        # et finalement on peut changer de joueur
        if changement:
            self.changer_joueur()


class JeuPipopipette:
    """
    L'interface graphique du jeu.
    """
    def __init__(self):
        # initialisation de pygame
        pg.init()

        # grille du jeu
        self.grille = Grille(TAILLE_GRILLE)

        # variables des tailles
        self.maj_tailles(TAILLE_ECRAN)

        # contiens les objets rectangles des segments, utilisé pour determiner
        # si on clique sur un segment
        self.rects_segment = []

        # pour que les segments soient en surbrillance quand on passe la
        # souris dessus
        self.segment_hover = None

        # creation de la surface d'affichage
        self.surf = pg.display.set_mode(TAILLE_ECRAN, pg.RESIZABLE)

    def maj_tailles(self, taille_ecran):
        """
        Crée ou met à jour les variables des tailles.
        """
        # taille ecran
        self.largeur, self.hauteur = taille_ecran

        # le coté de l'ecran le plus petit (comme il est en numerateur)
        cote_min = min(self.largeur, self.hauteur)

        # le coté de la grille le plus grand (comme il est en denominateur)
        cote_max = max(self.grille.largeur, self.grille.hauteur)

        # les segments
        self.long_segment = cote_min / (1.2 * cote_max)
        # self.long_segment = self.hauteur / 6
        self.larg_segment = round(self.long_segment / 8)

        # les cercles
        self.rayon_cercle = round(self.long_segment / 3.5)
        self.rayon_cercle_jonction = round(self.long_segment / 5.5)

        # calcul de la position du coin en haut a gauche de la grille, pour la centrer.
        # pour dessiner la grille, tout part de la
        x = self.largeur / 2 - self.grille.largeur * self.long_segment / 2
        y = self.hauteur / 2 - self.grille.hauteur * self.long_segment / 2
        self.depart_grille = [x, y]

        # texte
        self.police = pg.font.SysFont("Impact", round(cote_min / 12))

    def get_couleur(self, objet, ind=None):
        """
        Renvoie la couleur a utiliser pour un objet (segment/carré) donné.
        """
        if objet == 0: # bleu
            couleur = COUL_BLEU
        elif objet == 1:
            couleur = COUL_ROUGE
        else:
            if self.segment_hover == ind:
                couleur = COUL_SEGMENT_HOVER
            else:
                couleur = COUL_SEGMENTS

        return couleur

    def dessiner_grille(self):
        """
        Affiche la grille du jeu.
        """
        self.rects_segment.clear() # enlever ?

        lignes, colones = self.grille.segments

        ## Tracage des segments -------------------------------------------
        depart_l = self.depart_grille.copy()
        depart_c = self.depart_grille.copy()

        indice_segment = 0 # pour la surbrillance
        # on trace les traits verticaux
        for rangee in lignes:
            for ind_seg, segment in enumerate(rangee):
                couleur = self.get_couleur(segment, indice_segment)
                indice_segment += 1

                rect = pg.draw.line(
                    self.surf, couleur,
                    (depart_l[0] + (self.long_segment * ind_seg), depart_l[1]),
                    (depart_l[0] + (self.long_segment * ind_seg), depart_l[1] + self.long_segment),
                    self.larg_segment
                    )

                # si c'est vide, pas besoin d'ajouter les rects
                # if not self.rects_segment:
                self.rects_segment.append(rect)

            depart_l[1] += self.long_segment

        # on trace les traits horizontaux
        for rangee in colones:
            for ind_seg, segment in enumerate(rangee):
                couleur = self.get_couleur(segment, indice_segment)
                indice_segment += 1

                rect = pg.draw.line(
                    self.surf, couleur,
                    (depart_c[0], depart_c[1] + (self.long_segment * ind_seg)),
                    (depart_c[0] + self.long_segment, depart_c[1] + (self.long_segment * ind_seg)),
                    self.larg_segment
                    )

                # if not self.rects_segment:
                self.rects_segment.append(rect)

            depart_c[0] += self.long_segment

        ## Remplissage des carres gagnés ----------------------------------
        ind = 0
        for j in range(self.grille.hauteur):
            for i in range(self.grille.largeur):
                carre = self.grille.carres_gagnes[ind]
                if carre is not None:
                    couleur = self.get_couleur(carre)
                    topleft = (
                        self.depart_grille[0] + self.long_segment * (i + 0.5),
                        self.depart_grille[1] + self.long_segment * (j + 0.5)
                        )
                    pg.draw.circle(
                        self.surf, couleur,
                        (round(topleft[0]), round(topleft[1])),
                        self.rayon_cercle
                        )
                ind += 1

        ## Tracage des cercles aux jonctions de segments ------------------
        origine = self.depart_grille.copy()
        for i in range(self.grille.largeur + 1):
            origine[1] = self.depart_grille[1] # reset
            for j in range(self.grille.hauteur + 1):
                pg.draw.circle(
                    self.surf, COUL_CERCLE_JONCTION,
                    (round(origine[0]), round(origine[1])),
                    self.rayon_cercle_jonction
                    )
                origine[1] += self.long_segment
            origine[0] += self.long_segment

    def dessiner_hud(self):
        """
        Affiche les scores et le joueur actuel.
        """
        bleu, rouge = self.grille.score_detaille()

        # pour connaitre à qui le tour
        if self.grille.joueur_actuel: # rouge
            txt_rouge = f"[{rouge}]"
            txt_bleu = f" {bleu} "
        else: # bleu
            txt_rouge = f" {rouge} "
            txt_bleu = f"[{bleu}]"

        # creation des textes de score
        score_b = self.police.render(txt_bleu, True, COUL_BLEU)
        score_r = self.police.render(txt_rouge, True, COUL_ROUGE)

        # le "panneau" pour tout mettre ensemble
        largeur = score_b.get_width() + score_r.get_width()
        panneau = pg.Surface((largeur, score_b.get_height()))
        panneau.fill(COUL_FOND)

        panneau.blit(score_b, (0, 0))
        panneau.blit(score_r, (largeur - score_r.get_width(), 0))

        # on le centre
        rect = panneau.get_rect(midtop=(self.largeur / 2, 0))
        self.surf.blit(panneau, rect)

    def deter_segment(self, pos):
        """
        Determine si il y a un segment a la position donnée.
        Renvoie None si il y a aucun segment.
        ----
        pos (tuple): la position a verifier
        """
        i = 0
        for rect in self.rects_segment:
            if rect.collidepoint(pos):
                return i
            i += 1

        return None

    def boucle_jeu(self):
        """
        La boucle du jeu.
        """
        clock = pg.time.Clock()
        run = True
        while run:
            ## gestion des evenements
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False

                # on change la taille de l'écran
                elif event.type == pg.VIDEORESIZE:
                    self.maj_tailles(event.dict["size"])

                elif event.type == 32778: # la meme chose mais bug
                    self.maj_tailles((event.x, event.y))

                # on enfonce une touche
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.grille.reset()

                # clic
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if pg.mouse.get_pressed() == (1,0,0):
                        pos = pg.mouse.get_pos()

                        ind_seg = self.deter_segment(pos)
                        # si on a cliqué sur un segment valide et pas dans le vide
                        # et que le coup sois valide
                        if ind_seg is not None and self.grille.coup_valide(ind_seg):
                            self.grille.jouer_coup(ind_seg)

                            if MODE_IA:
                                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_WAIT)
                                self.grille.jouer_coup_ia()
                                pg.mouse.set_cursor(pg.SYSTEM_CURSOR_ARROW)

            # pour mettre les segments en surbrillance
            pos = pg.mouse.get_pos()
            self.segment_hover = self.deter_segment(pos)

            ## Maj de l'ecran...
            self.surf.fill(COUL_FOND)

            self.dessiner_grille()
            self.dessiner_hud()

            pg.display.flip()

            pg.display.set_caption(f"PIPOPIPETTE: IA vs HUMAIN - {round(clock.get_fps())} FPS")
            clock.tick(60)

        pg.quit()


def main():
    """
    La foncion qui lance tout !
    """
    jeu = JeuPipopipette()
    jeu.boucle_jeu()


main()
