# GRUPO
# Alexandre Galocha Pinto Junior  10734706
# Eduardo Pirro                   10734665
# Fernando Gorgulho Fayet         10734407


import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import math
from math import sin, cos, radians
from lib2d import Transform2D as tf


# BASIC FORMS----------------------------------------------------
# ---------------------------------------------------------------
# ---------------------------------------------------------------

# rotate_point - rotates a point around a given pivot
# RECEIVES: the point to be rotated, the angle to rotate in degrees, the origin point
# RETURNS: a tuple, the coords of the point rotate around the pivot
def rotate_point(point, angle, center_point=(0, 0)):

    angle_rad = radians(angle % 360)
    # Shift the point so that center_point becomes the origin
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * cos(angle_rad) - new_point[1] * sin(angle_rad),
                 new_point[0] * sin(angle_rad) + new_point[1] * cos(angle_rad))
    # Reverse the shifting we have done
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    return new_point



# makeCircle - creates a circle
# RECEIVES: center coords, radius, resolution (number N of verticies in the circle)
# RETURNS: an array with N tuples
def makeCircle(center, radius, resolution):
    
    coords = []
    
    for i in range(resolution):
        
        x = center[0] + radius
        y = center[1]
        
        coords.append(rotate_point((x, y), 0 + i * 360 / resolution, center))
        
    return coords



# makeRectangle - creates a rectangle
# RECEIVES: center, horizontal length, vetical length, rotation in degrees
# RETURNS: an array of 4 tuple: upper_left, upper_right, lower_right, lower_left
def makeRectangle(center, horizontal, vertical, rotation):
    
    coords = []
    coords.append((center[0] - horizontal/2, center[1] - vertical/2)) # lower left
    coords.append((center[0] - horizontal/2, center[1] + vertical/2)) # upper left
    coords.append((center[0] + horizontal/2, center[1] - vertical/2)) # lower right
    coords.append((center[0] + horizontal/2, center[1] + vertical/2)) # upper right
    
    for i in range(len(coords)):
        coords[i] = rotate_point(coords[i], rotation, center)
        
    return coords



# makeEquilateralTriangle - creates an equilateral triangle
# RECEIVES: center point of the triangle, length of the side, rotation in degrees
# RETURNS: an array of 3 tuples, each vertice of the triangle
def makeEquilateralTriangle(center, side, rotation):
    
    coords = []
    
    height = (side**2 - (side/2)**2) ** 0.5
    
    coords.append((center[0], center[1] + height/2))
    coords.append((center[0] + side/2, center[1] - height/2))
    coords.append((center[0] - side/2, center[1] - height/2))
    
    for i in range(len(coords)):
        coords[i] = rotate_point(coords[i], rotation, center)
        
    return coords
        
        
# serializeArrays - concatenates a list of arrays into a single one
# RECEIVES: a list of arrays to serialize
# RETURNS: two arrays, the first being the original arrays serialized and the second being the offsets of 
# each original array
def serializeArrays(arrays):
    
    final = []
    offsets = []
    
    for array in arrays:
        
        offsets.append(len(final))
        
        for coord in array:
            final.append(coord)
            
    return final, offsets



# serializeObjects2D - concatenate a list of objects into one single array of coords to be sent to the GPU
# RECEIVES: a list of objects to serialize
# RETURNS: two arrays, the first containing all the vertecies to the objects, serialized, the second containing
# the offsets, indicating where each object starts in the verticies array
def serializeObjects2D(objects):

    verticies = []
    offsets = []

    count = 0
    for obj in objects:
        offsets.append(len(verticies))

        for v in obj.getVerticies():
            verticies.append(v)

    return verticies, offsets


# draw2dObject - given an object, draws it on the screen
# RECEIVES: the object to draw, the offset of the object in the vertecies array, 
# a reference to the gl_Position variable, a reference to the gl_FragColor variable
def draw2dObject(object, offset, matrix_ref, color_ref):

    obj = object
    forms = obj.getVerticies()
    offsets = obj.getOffsets().copy()
    offsets.append(len(forms))
    primitives = obj.getPrimitives()
    colors = obj.getColors()

    loc_mat = matrix_ref
    loc_color = color_ref

    # changes the transformation matrix to this object's model matrix
    glUniformMatrix4fv(loc_mat, 1, GL_TRUE, obj.getModalMatrix())

    # for each form that forms the object:
        # calculates that form's offset based on the objects overall offset and the form local offset
        # chances the color value in gl_FragColor
        # draws the form
    for f in range(len(primitives)):  
        glUniform4f(loc_color, colors[f][0], colors[f][1], colors[f][2], 1.0)
        glDrawArrays(primitives[f], offsets[f] + offset, offsets[f+1] - offsets[f])



# 2D OBJECTS-----------------------------------------------------
# ---------------------------------------------------------------
# ---------------------------------------------------------------

# Object2D class - represents an object
class Object2D:

    def __init__(self):
        self.__forms = []               # list of coord
        self.__offsets = []             # list of offsets
        self.__primitives = []          # list of primitives
        self.__colors = []              # list of colors

        self.__pivot_x = 0              # pivot point x
        self.__pivot_y = 0              # pivot point y
        self.t_x = 0                    # x coord in global coodinates
        self.t_y = 0                    # y coord in global coodinates
        self.e_x = 1                    # global x scale
        self.e_y = 1                    # global y scale
        self.r = 0                      # global rotation, in degrees

    # addForm - adds a form to this object's composition
    # the forms are added according to the object's local coordinates
    # (a circle added at (0, 0) will be drawn in the center of the object, not in the
    # center of the screen)
    # RECEIVES: a list of vertecies, the primitive of the form, the color of the form
    def addForm(self, verticies, primitive, color):

        if(len(verticies) == 0):
            return

        self.__primitives.append(primitive)
        self.__offsets.append(len(self.__forms))
        self.__colors.append(color)

        for v in verticies:
            self.__forms.append(v)

        self.__pivot_x = 0
        self.__pivot_y = 0

        minX = 2
        maxX = -2
        minY = 2
        maxY = -2
        for v in self.__forms:

            minX = min(minX, v[0])
            maxX = max(maxX, v[0])
            minY = min(minY, v[1])
            maxY = max(maxY, v[1])

        self.__pivot_x = (minX + maxX)/2
        self.__pivot_y = (minY + maxY)/2

    # returns a list of vertecies that compose this object
    def getVerticies(self):
        return self.__forms

    # returns the pivot point for this object
    # by default, the pivot point is (0,0) minus the center of the object in local coordinates
    def getPivotPoint(self):
        return (self.__pivot_x, self.__pivot_y)

    # sets the pivot point to a specified value
    def setPivotPoint(self, point):
        self.__pivot_x = point[0]
        self.__pivot_y = point[1]

    # returns the list of offsets for each form that composes this object
    # the offsets are local, so the first added form will always have offset 0
    def getOffsets(self):
        return self.__offsets

    # returns the list of primitive for each form that composes this object
    def getPrimitives(self):
        return self.__primitives

    # returns the list of colors for each form that composes this object
    def getColors(self):
        return self.__colors

    # returns the model matrix of this object
    # the x and y coords, x and y scale an rotation are public variables and can be
    # altered directily
    def getModalMatrix(self):

        # as matrizes são geradas a partir das funções do arquivo "Transform2D.py"
        transMat = tf.translacao(self.t_x - self.__pivot_x, self.t_y - self.__pivot_y)
        rotMat = tf.rotacao(self.r, self.getPivotPoint())
        escMat = tf.escala(self.e_x, self.e_y, self.getPivotPoint())

        return np.matmul(np.matmul(transMat, rotMat), escMat)
