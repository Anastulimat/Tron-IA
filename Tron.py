import random
import time
import pprint as pp
import numpy
import numba
from numba import jit
from copy import *


## fenetre d'affichage

import matplotlib
matplotlib.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
plt.ion()
plt.show()
fig,axes = plt.subplots(1,1)
fig.canvas.set_window_title('TRON')

#################################################################################
#
#  Parametres du jeu

LARGEUR = 13
HAUTEUR = 17
L = 20  # largeur d'une case du jeu en pixel

canvas = None   # zone de dessin
Grille = None   # grille du jeu
posJ1  = None   # position du joueur 1 (x,y)
NbPartie = 0   # Nombre de parties effectuées
Scores = [0 , 0]  # score de la partie / scoreTotal des scores des differentes parties

def InitPartie():  
    global Grille, PosJ1, NbPartie, Scores, GrilleTemp
    
    NbPartie += 1
    Scores[0] = 0

    Grille = numpy.zeros((LARGEUR,HAUTEUR))
    
    # #positionne les murs de l'arene
    for x in range(LARGEUR):
       Grille[x][0] = 10
       Grille[x][HAUTEUR-1] = 10
       
    for y in range(HAUTEUR):
       Grille[LARGEUR-1][y] = 10
       Grille[0][y] = 10
    
    GrilleTemp = numpy.copy(Grille)


    for x in range(5, LARGEUR-5):
        Grille[x][HAUTEUR//2] = 10
    

    # position du joueur 1
    PosJ1 = (LARGEUR//2, 1)


#################################################################################
#
# Renvoie la liste de déplacement possible du joueur
@jit
def PossibleMoves(GrilleTemp, PosJ1):
    possibleMovesList = []
    
    # Droite ==> x+1
    if(GrilleTemp[PosJ1[0]+1][PosJ1[1]] == 0):
        possibleMovesList.append((1,0))
        
    # Gauche  ==> x-1
    if(GrilleTemp[PosJ1[0]-1][PosJ1[1]] == 0):
        possibleMovesList.append((-1,0))
        
    # Tout de droit ==> y+1
    if(GrilleTemp[PosJ1[0]][PosJ1[1]+1] == 0):
        possibleMovesList.append((0,1))
        
    # Bas ==> y-1
    if(GrilleTemp[PosJ1[0]][PosJ1[1]-1] == 0):
        possibleMovesList.append((0,-1))

    return possibleMovesList
    

#################################################################################
#
# Simulation de parties
@jit
def simulationParties(GrilleTemp, PosJ1):
    nbrCasesParcourues = 0

    while(True):
        directions = PossibleMoves(GrilleTemp, PosJ1)
        if(len(directions) == 0):
            return nbrCasesParcourues
        
        GrilleTemp[PosJ1[0]][PosJ1[1]] = 1 # laisse la trace de la moto
        # Choisir l'index de la direction
        randomIndexDirection = random.randrange(len(directions))
        # Déplacement du joueur 
        PosJ = directions[randomIndexDirection]
        PosJ1 = (PosJ1[0] + PosJ[0], PosJ1[1] + PosJ[1])
        nbrCasesParcourues += 1
        

#################################################################################
#
# Monte Carlo Approch
@jit
def monteCarlo(Grille, PosJ1, nombreParties):
    scoreTotal = 0
    nb = 0
    for i in range(nombreParties):
        Grille2 = numpy.copy(Grille)
        scoreTotal += simulationParties(Grille2, PosJ1)
    return scoreTotal/nombreParties

        

#################################################################################
#
# gestion du joueur humain et de l'IA
# VOTRE CODE ICI 

def Play():   
    global Scores
    
    while (True):
        Tstart = time.time()
        global  PosJ1        
        
        Grille[PosJ1[0]][PosJ1[1]] = 1 # laisse la trace de la moto
    
        GrilleTemp = deepcopy(Grille)

        possibleMovesList = PossibleMoves(GrilleTemp, PosJ1)
    
        bestScorePos = (0, 0)
        maxScore = 0
        for currentPos in range(len(possibleMovesList)):
            currentMonteCarlo = monteCarlo(Grille, possibleMovesList[currentPos], 100000)
            if(maxScore <= currentMonteCarlo):
                maxScore = currentMonteCarlo
                bestScorePos = possibleMovesList[currentPos]

            
        PosJ1 = (PosJ1[0] + bestScorePos[0], PosJ1[1] + bestScorePos[1])

        # fin de traitement
        Scores[0] +=1 

        #print(time.time() - Tstart)
        Affiche()
        
        # detection de la collision  
        if ( Grille[PosJ1[0]][PosJ1[1]] != 0 ): return  
       
################################################################################
#    
# Dessine la grille de jeu


def Affiche():
    axes.clear()
    
    plt.xlim(0,20)
    plt.ylim(0,20)
    plt.axis('off')
    fig.patch.set_facecolor((0,0,0))
    
    axes.set_aspect(1)
    
    # dessin des murs

    Murs  = []
    Bords = []
    for x in range (LARGEUR):
       for y in range (HAUTEUR):
           if ( Grille[x][y] == 10 ) : Bords.append(  plt.Rectangle((x,y), width = 1, height = 1 ) )
           if ( Grille[x][y] == 1  ) : Murs.append(  plt.Rectangle((x,y), width = 1, height = 1 ) )
        
    axes.add_collection (  matplotlib.collections.PatchCollection(Murs,   facecolors = (1.0, 0.47, 0.42)) )
    axes.add_collection (  matplotlib.collections.PatchCollection(Bords,  facecolors = (0.6, 0.6, 0.6)) )
    
    # dessin de la moto
  
    axes.add_patch(plt.Circle((PosJ1[0]+0.5,PosJ1[1]+0.5), radius= 0.5, facecolor = (1.0, 0, 0) ))
    
    # demande reaffichage
    fig.canvas.draw()
    fig.canvas.flush_events()  
 

################################################################################
#    
# Lancement des parties      
          
def GestionnaireDeParties():
    global Scores
   
    for i in range(3):
        time.sleep(1) # pause dune seconde entre chaque partie
        InitPartie()
        Play()
        Scores[1] += Scores[0]   # scoreTotal des scores des parties
        Affiche()
        ScoMoyen = Scores[1]//(i+1)
        print("Partie " + str(i+1) + " === Score : " + str(Scores[0]) + " === Moy " + str(ScoMoyen) )
        
     
GestionnaireDeParties()

  


    
        

      
 

