# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, ModelLine, find_id_by_element_name, get_name, get_names, meter_to_double)
# import math
import unicodedata

def normalize_string(input_string):
    return unicodedata.normalize('NFKD', input_string).encode('ASCII', 'ignore').decode('ASCII')

doc = __revit__.ActiveUIDocument.Document

interface = RevitDocInterface()
# find groups of lines that represent the faces of a same wall and store them
default_wall_width = meter_to_double(0.15)

def default_wall_widths(list_of_common_wall_widths):
    return [meter_to_double(common_w) for common_w in list_of_common_wall_widths]

print(default_wall_widths([0.15, 0.20, 0.25, 0.30]))
# print(default_wall_width)
default_walltype_id = find_id_by_element_name(interface.walltypes, "GENERICA_15CM")

all_levels = interface.levels

cad_wall_lines = interface.filter_lines_by_name(["Parede"])
tolerance = default_wall_width * 0.05 #allows +/- 2% variation to account for minor CAD drawing imprecisions
# print(tolerance)
def is_horizontal(model_line):
    return abs(model_line.end_y - model_line.start_y) == 0

def is_vertical(model_line):
    return abs(model_line.end_x - model_line.start_x) == 0

def is_diagonal(model_line):
    return model_line.end_x - model_line.start_x != 0 and model_line.end_y - model_line.start_y != 0

def offset_equals_wall_width(line_A, line_B):
    def dist_between_lines():
        if is_horizontal(line_B) and is_horizontal(line_A):
            return abs(line_B.start_y - line_A.start_y)
        elif is_vertical(line_B) and is_vertical(line_A):
            return abs(line_B.start_x - line_A.start_x)
        # elif is_diagonal(line_A) and is_diagonal(line_B):
            
        else:
            return default_wall_width
    offset = dist_between_lines()
    # print(abs(offset - default_wall_width))
    if abs(offset - default_wall_width) < tolerance:
        return True
    else:
        return False

def are_parallel(line_A, line_B):
    #two given lines must share the same plane (level elevation) and be equidistant at any point
    start_A = line_A.start_point
    end_A = line_A.end_point
    start_B = line_B.start_point
    end_B = line_B.end_point

    lines_share_same_plane = abs(start_A.Z - start_B.Z) < 1e-6
   
    # Calcula os vetores diretores
    vector_A = end_A - start_A
    vector_B = end_B - start_B
    
    cross_product = vector_A.CrossProduct(vector_B)
    # Verifica se o comprimento do vetor cruzado é quase zero (linhas perfeitamente paralelas)
    if cross_product.IsZeroLength():
        is_parallel = True
    else:
        # Para diagonais ou imprecisões, verifica se o comprimento do produto vetorial é pequeno (< 1)
        is_parallel = cross_product.GetLength() < .4

    # Retorna verdadeiro se as linhas estiverem no mesmo plano e forem paralelas
    return lines_share_same_plane and is_parallel

def share_point_in_perpendicular_axis(line_A, line_B):
    # for two given lines, checks if they share a common point in the opposite axis
    # to that in which they're located as straight horizontal (x) ou vertical (y) lines.
    # This means they probably represent two faces of a same wall, if wall_thickness 
    # condition is also true.
    if is_horizontal(line_A) and is_horizontal(line_B):
        if (
            line_B.start_x <= line_A.start_x <= line_B.end_x
        ) or (
            line_A.start_x <= line_B.start_x <= line_A.end_x
        ) or (
            line_B.end_x <= line_A.end_x <= line_B.start_x
        ) or (
            line_A.end_x <= line_B.end_x <= line_A.start_x
        ):
            return True
    elif is_vertical(line_A) and is_vertical(line_B):
        if (
            line_B.start_y >= line_A.start_y >= line_B.end_y
        ) or (
            line_A.start_y >= line_B.start_y >= line_A.end_y
        ) or (
            line_B.end_y >= line_A.end_y >= line_B.start_y
        ) or (
            line_A.end_y >= line_B.end_y >= line_A.start_y
        ):
            return True
    elif is_diagonal(line_A) and is_diagonal(line_B):
        return True
    return False

grouped_lines = []

i = 0
for l in interface.levels:
    print(l.Id)

for i in range(len(cad_wall_lines)):
    def lines_have_minimum_length(line_A, line_B):
        min_length = default_wall_width*1.5
        def line_length(line):
            return line.get_Parameter(DB.BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()
        # print(line_length(line_A), line_length(line_B))
        return line_length(line_A) >= min_length and line_length(line_B) >= min_length
    
    ref_line = ModelLine(cad_wall_lines[i])
    lines_of_same_wall = [ref_line]
    # def line_level_id(line):
    #     line_sketch_plane = line.get_Parameter(DB.BuiltInParameter.SKETCH_PLANE_PARAM).AsString()
    #     linel_level_name = line_sketch_plane.split()[-1]
    #     linel_level_name = normalize_string(linel_level_name)  # Normaliza a string para remover acentos

    #     for level in interface.levels:
    #         print((normalize_string(level.Name) == linel_level_name)
    #         line_level_id = level.Id if linel_level_name == normalize_string(level.Name) else None
    #     print(linel_level_name, line_level_id)
    #     return line_level_id

    # line_level_id(cad_wall_lines[i])

    n = i+1
    while n < len(cad_wall_lines):
        next_line = ModelLine(cad_wall_lines[n])
        # print('comparing now {} to {}:'.format(str(cad_wall_lines[i].Id), str(cad_wall_lines[n].Id)))
        # print('have intersecting points?', share_point_in_perpendicular_axis(ref_line, next_line))
        # print('offset equals width?', offset_equals_wall_width(ref_line, next_line))
        # print('parallel?', are_parallel(ref_line, next_line))
        # print(lines_have_minimum_length(cad_wall_lines[i], cad_wall_lines[n]))
        if (
            are_parallel(ref_line, next_line)
            and offset_equals_wall_width(ref_line, next_line)
            and share_point_in_perpendicular_axis(ref_line, next_line)
            and lines_have_minimum_length(cad_wall_lines[i], cad_wall_lines[n])
        ):
            lines_of_same_wall.append(next_line)
        n+=1

    if len(lines_of_same_wall) > 1:
        grouped_lines.append(lines_of_same_wall)
    i+=1

# print(grouped_lines)
def create_wall(doc, bound_line, default_wall_type_id, level_id, mysterious_param_1=10, mysterious_param_2=1, flag_1=False, flag_2=False):
    t = DB.Transaction(doc, "Create new wall instance from cad line")
    t.Start()
    try:
        wall = DB.Wall.Create(doc, bound_line, default_wall_type_id, level_id, mysterious_param_1, mysterious_param_2, flag_1, flag_2)
        wall_location_line = wall.get_Parameter(DB.BuiltInParameter.WALL_KEY_REF_PARAM)
        if wall_location_line and wall_location_line.IsReadOnly == False:
            wall_location_line.Set(0)  # Define Linha central da parede como Linha de localizacao
    except Exception as e:
        print("Error creating wall instance: {}".format(e))
        pass
    t.Commit()

# print(grouped_lines)

def longest(line_list):
    if line_list[0].length > lines[1].length:
        longest = line_list[0]
    else:
        longest = line_list[1]
    return longest

def equal_length(line_list):
    if (line_list[0].length - lines[1].length) < tolerance:
        return line_list[0]
    else:
        return line_list[1]

for lines in grouped_lines:
    # Ordena as linhas do grupo pelo menor ponto inicial (start_x, start_y)
    sorted_lines = sorted(
        lines,
        key=lambda line: (line.start_x, line.start_y)
    )
    print(sorted_lines)
    # Seleciona a primeira como linha de referência e a segunda como linha auxiliar
    ref_line = sorted_lines[0]
    aux_line = sorted_lines[1]
    # print(ref_line.start_x, aux_line.start_x)
    # Vetores direção para linha de referência
    ref_dir = DB.XYZ(ref_line.end_x - ref_line.start_x, ref_line.end_y - ref_line.start_y, 0)
    
    # Determina deslocamento para criar a linha entre as duas
    offset_x = default_wall_width / 2 if abs(ref_dir.X) < abs(ref_dir.Y) else 0
    offset_y = default_wall_width / 2 if abs(ref_dir.Y) < abs(ref_dir.X) else 0

    # Ajusta deslocamento com base na posição relativa
    if aux_line.start_x > ref_line.start_x:  # Auxiliar à direita
        offset_x *= -1
    if aux_line.start_y > ref_line.start_y:  # Auxiliar acima
        offset_y *= -1

    # Cria os novos pontos deslocados
    a = ref_line.start_point - DB.XYZ(offset_x, offset_y, 0)
    b = ref_line.end_point - DB.XYZ(offset_x, offset_y, 0)
    
    # Tenta criar a nova parede
    try:
        bound_line = DB.Line.CreateBound(a, b)
        create_wall(doc, bound_line, default_walltype_id, interface.levels[0].Id, 10, 0, False, False)
    except NameError as e:
        print("Erro ao criar parede: {}".format(e))