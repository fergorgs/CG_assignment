# GRUPO
# Alexandre Galocha Pinto Junior  10734706
# Eduardo Pirro                   10734665
# Fernando Gorgulho Fayet         10734407


import glm
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import math


# serialize_objects3d: serializes all the vertices and texture coordinates of the given
# objects into two single arrays
# RECEIVES: a list of objects to be serialized
def serialize_objects3d(objects):
    vertices = []
    tex_coords = []

    for o in objects:
        vertices.extend(o.serialized_vert)
        del o.serialized_vert
        
        tex_coords.extend(o.serialized_tex)
        del o.serialized_tex

    return vertices, tex_coords


# Object3D: class, representing a 3d model. It stores many informations,
# such as the model's vertices, the model's textures coordinates, and it's
# transformations properties (translation, rotation and scale)
class Object3D:
    def __init__(self):
        self.__vert_indexes = []        # list of vertex indexes
        self.__vertices = []            # list of vertex coordinates
        self.__tex_indexes = []         # list of texture indexes
        self.__tex_coords = []          # list of texture coordinates

        self.serialized_vert = []
        self.serialized_tex = []

        self.__len = 0

        self.__texture_ids = []         # for each component of the model, which texture id to use
        self.__textures_offsets = []    # the offset of vertices in which each texture ends and a new one begins

        self.t_x = 0.0                  # x coord in global coodinates
        self.t_y = 0.0                  # y coord in global coodinates
        self.t_z = 0.0                  # z coord in global coodinates
        self.s_x = 1.0                  # global x scale
        self.s_y = 1.0                  # global y scale
        self.s_z = 1.0                  # global z scale
        self.a_x = 0                    # x axies angle, around it's center
        self.a_y = 0                    # y axies angle, around it's center
        self.a_z = 0                    # z axies angle, around it's center
        # self.angle = 0.0                # global rotation, in degrees
        # self.r_x = 0.0                  # rotation in x enabled
        # self.r_y = 0.0                  # rotation in y enabled
        # self.r_z = 1.0                  # rotation in z enabled




    # __model: calculates the model's model matrix
    # Using glm functions, applies translation, rotation in the 3 axies,
    # and scale to the model
    def __model(self):
        matrix_transform = glm.mat4(1.0)
                                                        
        matrix_transform = glm.translate(
            matrix_transform, glm.vec3(self.t_x, self.t_y, self.t_z))
        matrix_transform = glm.rotate(
            matrix_transform, math.radians(self.a_x),
            glm.vec3(1.0, 0.0, 0.0))
        matrix_transform = glm.rotate(
            matrix_transform, math.radians(self.a_y),
            glm.vec3(0.0, 1.0, 0.0))
        matrix_transform = glm.rotate(
            matrix_transform, math.radians(self.a_z),
            glm.vec3(0.0, 0.0, 1.0))
        matrix_transform = glm.scale(
            matrix_transform, glm.vec3(self.s_x, self.s_y, self.s_z))

        matrix_transform = np.array(matrix_transform).T

        return matrix_transform




    # load from file: loads an object
    # RECEIVES: an '.obj' file, contening the informations of the model
    def load_from_file(self, filename):
        """Loads a Wavefront OBJ file. """

        # self.__texture_ids = texture_ids

        # abre o arquivo obj para leitura
        for line in open(filename, "r"):  # para cada linha do arquivo .obj
            if line.startswith('#'):
                continue  # ignora comentarios
            values = line.split()  # quebra a linha por espaço
            if not values:
                continue

            # recuperando vertices
            if values[0] == 'v':
                self.__vertices.append(values[1:4])

            # recuperando coordenadas de textura
            elif values[0] == 'vt':
                self.__tex_coords.append(values[1:3])

            # recuperando faces
            elif values[0] in ('usemtl', 'usemat'):
                self.__textures_offsets.append(len(self.__vert_indexes))     # salva o offset em que detectou uma nova textura

            elif values[0] == 'f':
                for v in values[1:]:
                    w = v.split('/')
                    self.__vert_indexes.append(int(w[0]))
                    if len(w) >= 2 and len(w[1]) > 0:
                        self.__tex_indexes.append(int(w[1]))
                    else:
                        self.__tex_indexes.append(0)

        # serialize vertices using indexes
        for idx in self.__vert_indexes:
            self.serialized_vert.append(self.__vertices[idx - 1])

        # serialize texture coords using indexes
        for idx in self.__tex_indexes:
            self.serialized_tex.append(self.__tex_coords[idx - 1])

        # deleting temp lists, checking for errors
        del self.__tex_coords, self.__tex_indexes

        if len(self.serialized_vert) != len(self.serialized_tex):
            print("ERROR! Texture and vertex lists with different sizes")
        else:
            self.__len = len(self.serialized_vert)
        
        # if no 'usemtl' tag was found in the obj file, 
        # considers the model to have only a single texture
        if(len(self.__textures_offsets) == 0):
            self.__textures_offsets.append(0)

        self.__textures_offsets.append(len(self.__vert_indexes))   # aux




    # bind_textures: binds the object to its respective textures ids
    # RECEIVES: a list of texture ids used by this object. The actual loading of
    # the textures must be done on the main code
    def bind_textures(self, texture_ids):
        self.__texture_ids = texture_ids
    



    # render: renders a given model
    # RECEIVES: a reference to the transformation matrix on the GPU;
    # the model's offset on the serialized vertices array sent to the GPU
    # a list of matrixes representing any additional transformations to be applied on the model
    def render(self, model_location, init_offset, extra_mats = []):

        trans_mat = self.__model()                  # qualquer transformação adicional é
        for mat in extra_mats:                      # é aplicada à matriz model
            trans_mat = np.matmul(mat, trans_mat)
        
        glUniformMatrix4fv(model_location, 1, GL_TRUE, trans_mat)       # changes the transformation matrix

        # for every component, changes the texture and renders only the 
        # vertecies to that component, using the values in the 
        # 'textures_offsets' array
        for i in range(len(self.__textures_offsets)-1):
            component_len = self.__textures_offsets[i+1] - self.__textures_offsets[i]
            glBindTexture(GL_TEXTURE_2D, self.__texture_ids[i])
            glDrawArrays(GL_TRIANGLES, init_offset + self.__textures_offsets[i], component_len)
            
        # returns the offset of the next model to be rendered (curent offset + current model's length)
        return init_offset + self.__len

    # def get_txt_ids_array(self, filename, base_txt_id):

    #     textures = {}
    #     txt_ids = []
    #     cnt = base_txt_id
    #     for line in open(filename, "r"):
    #         if line.startswith('#'):
    #             continue
    #         values = line.split()
    #         if not values:
    #             continue

    #         if values[0] in ('usemtl', 'usemat'):
    #             if(values[1] in textures):
    #                 txt_ids.append(textures[values[1]])
    #             else:
    #                 textures[values[1]] = cnt
    #                 txt_ids.append(textures[values[1]])
    #                 cnt += 1
        
    #     return txt_ids
