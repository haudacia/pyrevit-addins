from Autodesk.Revit.DB import *

doc = __revit__.ActiveUIDocument.Document

# Get the selected room
selection = __revit__.ActiveUIDocument.Selection

room = doc.GetElement(element_id)

area_tags = list(room.GetDependentElements(Filters.AreaTagFilter(), False))
if area_tags:
    area_value = area_tag.Area
print("Room Area (from AreaTag):", area_value)

