import glm
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import math


def serialize_objects3d(objects):
    vertices = []
    tex_coords = []

    for o in objects:
        vertices.extend(o.serialized_vert)
        del o.serialized_vert
        
        tex_coords.extend(o.serialized_tex)
        del o.serialized_tex

    return vertices, tex_coords


class Object3D:
    def __init__(self):
        self.__vert_indexes = []        # list of vertex indexes
        self.__vertices = []            # list of vertex coordinates
        self.__tex_indexes = []         # list of texture indexes
        self.__tex_coords = []          # list of texture coordinates

        self.serialized_vert = []
        self.serialized_tex = []

        self.__len = 0

        self.__texture_ids = []
        self.__textures_offsets = []
        self.__texture_id = -1          # gl texture id

        self.t_x = 0.0                  # x coord in global coodinates
        self.t_y = 0.0                  # y coord in global coodinates
        self.t_z = 0.0                  # z coord in global coodinates
        self.s_x = 1.0                  # global x scale
        self.s_y = 1.0                  # global y scale
        self.s_z = 1.0                  # global z scale
        self.a_x = 0
        self.a_y = 0
        self.a_z = 0
        self.angle = 0.0                # global rotation, in degrees
        self.r_x = 0.0                  # rotation in x enabled
        self.r_y = 0.0                  # rotation in y enabled
        self.r_z = 1.0                  # rotation in z enabled

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

    def load_from_file_with_texture(self, filename, texture_ids):
        """Loads a Wavefront OBJ file. """

        self.__texture_ids = texture_ids

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
            #     self.__material = values[1]
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

        # del self.__vertices, self.__vert_indexes

        # serialize texture coords using indexes
        for idx in self.__tex_indexes:
            self.serialized_tex.append(self.__tex_coords[idx - 1])

        del self.__tex_coords, self.__tex_indexes

        if len(self.serialized_vert) != len(self.serialized_tex):
            print("ERROR! Texture and vertex lists with different sizes")
        else:
            self.__len = len(self.serialized_vert)
            
        if(len(self.__textures_offsets) == 0):
            self.__textures_offsets.append(0)

        self.__textures_offsets.append(len(self.__vert_indexes))   # aux

    def render(self, model_location, init_offset, extra_mats = []):

        trans_mat = self.__model()                  # qualquer transformação adicional é
        for mat in extra_mats:                      # é aplicada à matriz model
            trans_mat = np.matmul(mat, trans_mat)
        
        glUniformMatrix4fv(model_location, 1, GL_TRUE, trans_mat)

        for i in range(len(self.__textures_offsets)-1):
            component_len = self.__textures_offsets[i+1] - self.__textures_offsets[i]
            glBindTexture(GL_TEXTURE_2D, self.__texture_ids[i])
            glDrawArrays(GL_TRIANGLES, init_offset + self.__textures_offsets[i], component_len)
            

        return init_offset + self.__len

    def get_txt_ids_array(self, filename, base_txt_id):

        textures = {}
        txt_ids = []
        cnt = base_txt_id
        for line in open(filename, "r"):
            if line.startswith('#'):
                continue
            values = line.split()
            if not values:
                continue

            if values[0] in ('usemtl', 'usemat'):
                if(values[1] in textures):
                    txt_ids.append(textures[values[1]])
                else:
                    textures[values[1]] = cnt
                    txt_ids.append(textures[values[1]])
                    cnt += 1
        
        return txt_ids
