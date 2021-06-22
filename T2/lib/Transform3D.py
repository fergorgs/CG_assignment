# GRUPO
# Alexandre Galocha Pinto Junior  10734706
# Eduardo Pirro                   10734665
# Fernando Gorgulho Fayet         10734407


import numpy as np
import math
from math import sin, cos, radians


# Translação - tranlada a forma para o ponto especificado
# recebe: t_x, t_y, as coordenadas finais para onde a forma será transladada
# retorna: a matriz de tranformação como um numpy array
def translacao(t_x, t_y, t_z):
    
    return np.array([    [1.0, 0.0, 0.0, t_x], 
                         [0.0, 1.0, 0.0, t_y], 
                         [0.0, 0.0, 1.0, t_z],
                         [0.0, 0.0, 0.0, 1.0]], np.float32)



# Escala - redimensiona uma forma no eixo x e y dado um pivot
# recebe: a nova escala no eixo x, a nova escala no eixo y, o ponto pivot
# retorna: a matriz de tranformação como um numpy array
def escala(e_x, e_y, e_z, pivot):
    
    # calculando o pivot--------------
    x_pivot = pivot[0]
    y_pivot = pivot[1]
    z_pivot = pivot[2]
    
    # matriz de transformação de escala----------
    esc_mat = np.array([    [e_x, 0.0, 0.0, 0.0], 
                            [0.0, e_y, 0.0, 0.0], 
                            [0.0, 0.0, e_z, 0.0],
                            [0.0, 0.0, 0.0, 1.0]], np.float32)
    
    
    # matriz final é o resultado da translação para a origem, 
    # redimensionamento e translação de volta para o pivot
    return np.matmul(np.matmul(translacao(x_pivot, y_pivot, z_pivot), esc_mat), translacao(-x_pivot, -y_pivot, -z_pivot))



# Rotação - rotaciona uma forma dado um pivot.
# recebe: o novo angulo de rotação em graus, o ponto pivot
# retorna: a matriz de tranformação como um numpy array
def rotacao(angulo, pivot, eixo):
    
    # calculando o pivot--------------
    x_pivot = pivot[0]
    y_pivot = pivot[1]
    z_pivot = pivot[2]
    
    # calculando seno e cosseno------------
    rad = math.radians(angulo) 
    c = math.cos(rad)
    s = math.sin(rad)
    
    # matriz de transformação de rotação----------------
    if(eixo == 'x'):
        rot_mat = np.array([[1.0, 0.0, 0.0, 0.0], 
                            [0.0,   c,  -s, 0.0], 
                            [0.0,   s,   c, 0.0],
                            [0.0, 0.0, 0.0, 1.0]], np.float32)
    elif(eixo == 'y'):
        rot_mat = np.array([[  c, 0.0,   s, 0.0], 
                            [0.0, 1.0, 0.0, 0.0], 
                            [ -s, 0.0,   c, 0.0],
                            [0.0, 0.0, 0.0, 1.0]], np.float32)
    elif(eixo == 'z'):
        rot_mat = np.array([[  c,  -s, 0.0, 0.0], 
                            [  s,   c, 0.0, 0.0], 
                            [0.0, 0.0, 1.0, 0.0],
                            [0.0, 0.0, 0.0, 1.0]], np.float32)
    
    
    # matriz final é o resultado da translação para a origem, 
    # rotação e translação de volta para o pivot
    return np.matmul(np.matmul(translacao(x_pivot, y_pivot, z_pivot), rot_mat), translacao(-x_pivot, -y_pivot, -z_pivot))
