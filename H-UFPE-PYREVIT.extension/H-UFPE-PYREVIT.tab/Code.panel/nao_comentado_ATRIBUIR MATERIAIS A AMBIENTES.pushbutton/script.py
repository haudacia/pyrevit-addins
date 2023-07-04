# -*- coding: utf-8 -*-
import Autodesk.Revit.DB as revit

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
app = __revit__.Application

materiais = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Materials)
ambientes = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Rooms)
all_walls = revit.FilteredElementCollector(doc).OfCategory(revit.BuiltInCategory.OST_Walls)
all_walls_instances = all_walls.WhereElementIsNotElementType()
all_walls_types = all_walls.WhereElementIsElementType()
for wall in all_walls:
    id = wall.Id
    print(id)
    nome_parede = wall.Name
    parede_elem = doc.GetElement(id)
    print(parede_elem)

ambiente_testando = doc.GetElement(revit.ElementId(611306))
parede_testando = doc.GetElement(revit.ElementId(358513))

CODREVEST_PAREDES = ambiente_testando.LookupParameter('COD-REVEST_PAREDES')
print(CODREVEST_PAREDES)
material_teste = doc.GetElement(revit.ElementId(414))
material_teste_ID = material_teste.Id
nome_material_teste_NOME = material_teste.Name
material_teste_MARCA = material_teste.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK)

# t = revit.Transaction(doc, "aplicar cod revest a ambiente")
# t.Start()
# CODREVEST_PAREDES.Set(material_teste_ID)
# t.Commit()
ab = parede_testando.GetMaterialIds(False)
for id_elemento_material_parede in ab:
    for material in materiais:
        print(material)
        if material.Id == id_elemento_material_parede:
            # print('deu certo')
            mat_parede = material
            cod_mat_parede = material.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK)
            cod_mat_parede_str = material.get_Parameter(revit.BuiltInParameter.ALL_MODEL_MARK).AsValueString()
            # print(cod_mat_parede) #LOCALIZEI AQUI O CÓDIGO ESCRITO NO CAMPO NATIVO 'MARCA',DENTRO
            # DE CADA MATERIAL.

# camadas = doc.GetElement(revit.ElementId(1977638)).CompoundStructure
# print(list(camadas.GetLayers()))

#     PRA O LOOKUP FUNCIONAR NESSE CASO ONDE ELE ITERA POR TODAS, VOU TER QUE USAR ERROR HANDLING PRA
#     QUANDO ELE SE DEPARAR COM PAREDES QUE POR ALGUMA RAZÃO TENHAM VALOR NULO NESSE PARAMETRO 'ÁREA'
#     OU ERROR HANDLING (IMAGINO QUE SEJA A FORMA MAIS ELEGANTE/EM CONFOMRIDADE COM BOAS PRÁTICAS) OU
#     CRIAR UM IF/CONDIÇAO P Q ELE SO ACESSE/PRINTE O PARAMETRO ÁREA DAS PAREDES Q TENHAM ESSE PARAMETRO, NE
#     print(area_parede.AsValueString())
#     print(wall.Id)
#     for p in wall.Parameters:
#         # print(p.Definition.Name)
#         wall_c = wall.get_Parameter(revit.BuiltInParameter.ALL_MODEL_TYPE_NAME)
#         print(wall_c.AsString())
#     print(wall.Name) #nao funciona!! nao faz sentido pq Name é um mebro (DO TIPO eLEMENT) DA wALLtYPE
#


# print(list(wall_id.Parameters))
# for p in wall_id.Parameters:
#         print('\n{}'.format(p.Definition.Name))
#
# ambiente_hall = doc.GetElement(revit.ElementId(611306))
# #abaixo, ele encontrou o parametro compartilhado de revest de paredes no ambiente especificado.
# for parametro in ambiente_hall.Parameters:
#     id_param = parametro.Id
#     print(id_param)
#     nome_param = parametro.Definition.Name
#     print(nome_param)
#     if nome_param == 'COD-REVEST_PAREDES':
#         revest_parede = parametro
#         print('aqui,{}'.format(revest_parede.AsValueString()))
#         #abaixo, acessei o valor atribuído ao parametro compartilhado COD-REVEST_PAREDES:
#         print(parametro.AsValueString())
#         for material in materiais:
#             if material.Name == revest_parede.AsValueString():
#                 print('achou') #ele identificou aqui dentre todos os materiais presentes no projeto,
#                 #armazenados na variavel materiais, aquele encontrado no objeto ambiente_hall.
