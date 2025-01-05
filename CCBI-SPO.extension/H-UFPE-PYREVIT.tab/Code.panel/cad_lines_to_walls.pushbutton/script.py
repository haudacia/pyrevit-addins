# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as DB
from revit_doc_interface import (RevitDocInterface, ModelLine, find_id_by_element_name, get_name, get_names, meter_to_double)

doc = __revit__.ActiveUIDocument.Document
collect = DB.FilteredElementCollector(doc)

interface = RevitDocInterface()

# find groups of lines that represent the faces of a same wall and store them
default_wall_thickness = meter_to_double(0.15)
# print(default_wall_thickness)
default_walltype_id = find_id_by_element_name(interface.walltypes, "GENERICA_15CM")

cad_wall_lines = interface.filter_lines_by_name(["Parede"])
tolerance = 1e-5

def is_horizontal(model_line):
    return abs(model_line.end_y - model_line.start_y) == 0

def is_vertical(model_line):
    return abs(model_line.end_x - model_line.start_x) == 0

def dist_between_lines(line_A, line_B):
    if is_horizontal(line_B) and is_horizontal(line_A):
        offset = (abs(line_B.start_y - line_A.start_y))
    elif is_vertical(line_B) and is_vertical(line_A):
        offset = (abs(line_B.start_x - line_A.start_x))
    else:
        return None
    return offset

def share_point_in_perpendicular_axis(line_A, line_B):
    # for two given lines, checks if they share a common point in the opposite axis
    # to that in which they're located as straight horizontal (x) ou vertical (y) lines.
    # This means they probably represent two faces of a same wall, if wall_thickness 
    # condition is also true.
    if is_horizontal(line_B) and is_horizontal(line_A):
        if (
            line_B.start_x < line_A.start_x < line_B.end_x
        ) or (
            line_A.start_x < line_B.start_x < line_A.end_x
        ) or (
            line_B.end_x < line_A.end_x < line_B.start_x
        ) or (
            line_A.end_x < line_B.end_x < line_A.start_x
        ):
            return True
    elif is_vertical(line_B) and is_vertical(line_A):
        if (
            line_B.start_y > line_A.start_y > line_B.end_y
        ) or (
            line_A.start_y > line_B.start_y > line_A.end_y
        ) or (
            line_B.end_y > line_A.end_y > line_B.start_y
        ) or (
            line_A.end_y > line_B.end_y > line_A.start_y
        ):
            return True
    return False
    # *switch to using cases?

grouped_lines = []
i = 0

for i in range(len(cad_wall_lines)-1):
    n = i+1
    ref_line = ModelLine(cad_wall_lines[i])
        # compare list[i] com list[i+1]
    lines_of_same_wall = [ref_line]
    while n < len(cad_wall_lines):
        next_line = ModelLine(cad_wall_lines[n])
        # print('comparing now {} to {}:'.format(str(cad_wall_lines[i].Id), str(cad_wall_lines[n].Id)))
        offset = dist_between_lines(ref_line, next_line)
        if share_point_in_perpendicular_axis(ref_line, next_line) and ((offset - default_wall_thickness) < tolerance):
    # guarde-os juntos na lista se match criteria
            lines_of_same_wall.append(next_line)
            # remova da lista os que forem dando match
        # print(len(lines_of_same_wall))
        n+=1
    # recomece do proximo da lista
    if len(lines_of_same_wall) > 1:
        grouped_lines.append(lines_of_same_wall)
    i+=1
    # mantenha a posicao do 1o em i e va incrementando a n e comparando-a com i ate acabar os itens

def create_wall(doc, bound_line, default_wall_type_id, level_id, misterious_param_1 = 10, misterious_param_2 = 0 , flag_1 = False, flag_2 = False):
    t = DB.Transaction(doc, "Create new wall instance from cad line")
    t.Start()
    try:
        DB.Wall.Create(doc, bound_line, default_wall_type_id, level_id, 10, 0, False, False)
        # print("Wall created at {} and {}.".format(start_point, end_point))
    except Exception as e:
        print("Error creating wall instance: {}".format(e))
        pass
    t.Commit()

# print(grouped_lines)

def longest_in(line_list):
    if line_list[0].length >= lines[1].length:
        longest = line_list[0]
    else:
        longest = line_list[1]
    return longest

def shortest_in(line_list):
    if line_list[0].length < lines[1].length:
        shortest = line_list[0]
    else:
        shortest = line_list[1]
    return shortest

for lines in grouped_lines:
    ref_line = longest_in(lines)
    aux_line = shortest_in(lines)
    # ref_line = shortest_in(lines)
    # aux_line = longest_in(lines)
    # print(ref_line.length, aux_line.length)
    # # determine line positioning condition relative to the other(s) in the same group
    print(ref_line.start_x, aux_line.start_x)
    is_right = is_vertical(ref_line) and ref_line.start_x > aux_line.start_x
    is_left = is_vertical(ref_line) and ref_line.start_x < aux_line.start_x
    # print(is_right, is_vertical(ref_line), 'must be opposite of', is_left)
    is_above = is_horizontal(ref_line) and ref_line.start_y > aux_line.start_y
    is_below = is_horizontal(ref_line) and ref_line.start_y < aux_line.start_y

    if is_right:
        # a = ref_line.start_point - DB.XYZ(default_wall_thickness/2, .2, 0)
        # b = ref_line.end_point - DB.XYZ(default_wall_thickness/2, -.2, 0)
        a = ref_line.start_point - DB.XYZ(default_wall_thickness/2, 0, 0)
        b = ref_line.end_point - DB.XYZ(default_wall_thickness/2, 0, 0)
    elif is_left:
        # a = ref_line.start_point + DB.XYZ(default_wall_thickness/2, .2, 0)
        # b = ref_line.end_point + DB.XYZ(default_wall_thickness/2, -.2, 0)
        a = ref_line.start_point + DB.XYZ(default_wall_thickness/2, 0, 0)
        b = ref_line.end_point + DB.XYZ(default_wall_thickness/2, 0, 0)
    elif is_above:
        # a = ref_line.start_point - DB.XYZ(-.2, default_wall_thickness/2, 0)
        # b = ref_line.end_point - DB.XYZ(.2, default_wall_thickness/2, 0)
        a = ref_line.start_point - DB.XYZ(0, default_wall_thickness/2, 0)
        b = ref_line.end_point - DB.XYZ(0, default_wall_thickness/2, 0)
    elif is_below:
        # a = ref_line.start_point + DB.XYZ(-.2, default_wall_thickness/2, 0)
        # b = ref_line.end_point + DB.XYZ(.2, default_wall_thickness/2, 0)
        a = ref_line.start_point + DB.XYZ(0, default_wall_thickness/2, 0)
        b = ref_line.end_point + DB.XYZ(0, default_wall_thickness/2, 0)
    else:
        None
    bound_line = DB.Line.CreateBound(a, b)
    create_wall(doc, bound_line, default_walltype_id, interface.levels[0].Id, 10, 0 , False, False)



        

# # hadn't worked
# while i < len(cad_wall_lines):
#     n = i+1
#     while n < len(cad_wall_lines):
#         # compare the first line on the list with every other line
#         ref_line = ModelLine(cad_wall_lines[i])
#         next_line = ModelLine(cad_wall_lines[n])
#         print('comparing now {} to {}:'.format(str(cad_wall_lines[i].Id), str(cad_wall_lines[n].Id)))
#         lines_of_same_wall = [cad_wall_lines[i]]
#         # if it matches the criteria (its possible and frequent that more than one matches the criteria)
#         if share_point_in_perpendicular_axis(ref_line, next_line):
#             lines_of_same_wall.append(str(cad_wall_lines[n].Id))
#             grouped_lines.append(cad_wall_lines)
#         n+=1
#     i+=1

    # cad_wall_lines.pop(i)
    
    # testing loop:

    # if they match the criteria
    #     group them together and 
    #     remove them fromm the general list
    #     start over

    # model_line = ModelLine(line)
    # ref_line = model_line[i]
    # second_line = model_line[]
    # model_line.start_x