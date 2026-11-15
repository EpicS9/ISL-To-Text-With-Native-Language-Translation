"""
ISL Draw.io Diagram Generator
Generates valid, professional .drawio XML files for all academic diagrams:
1. Architectural Diagram (with Frontend, V3 Models, NLP, and Google Translate API)
2. Modular Design Diagram
3. Proposed System Flowchart
4. Sequence Diagram
5. Use Case Diagram
6. DFD Level 0 (Context Diagram)
7. DFD Level 1
8. DFD Level 2
9. Multi-Page Master File (all_isl_diagrams.drawio)
"""

import xml.etree.ElementTree as ET
import os

class DrawIOBuilder:
    def __init__(self, page_name="Page-1", page_id="page_1", width=1200, height=850):
        self.page_name = page_name
        self.page_id = page_id
        self.width = width
        self.height = height
        self.cell_id = 2
        self.cells = []
        
    def next_id(self):
        cid = str(self.cell_id)
        self.cell_id += 1
        return cid

    def add_node(self, label, x, y, w, h, style):
        cid = self.next_id()
        cell = {
            "id": cid,
            "value": label,
            "style": style,
            "vertex": "1",
            "parent": "1",
            "geometry": {"x": str(x), "y": str(y), "width": str(w), "height": str(h), "as": "geometry"}
        }
        self.cells.append(cell)
        return cid

    def add_edge(self, source_id, target_id, label="", style="endArrow=classic;html=1;strokeColor=#000000;strokeWidth=1.5;fontSize=11;fontFamily=Times New Roman;"):
        cid = self.next_id()
        cell = {
            "id": cid,
            "value": label,
            "style": style,
            "edge": "1",
            "parent": "1",
            "source": source_id,
            "target": target_id,
            "geometry": {"relative": "1", "as": "geometry"}
        }
        self.cells.append(cell)
        return cid

    def to_diagram_element(self):
        diagram_el = ET.Element("diagram", id=self.page_id, name=self.page_name)
        model_el = ET.SubElement(diagram_el, "mxGraphModel", dx="1200", dy="800", grid="1", gridSize="10",
                                guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
                                pageScale="1", pageWidth=str(self.width), pageHeight=str(self.height),
                                background="#ffffff", math="0", shadow="0")
        root_el = ET.SubElement(model_el, "root")
        
        # Base parent cells
        ET.SubElement(root_el, "mxCell", id="0")
        ET.SubElement(root_el, "mxCell", id="1", parent="0")
        
        for c in self.cells:
            cell_attrs = {k: v for k, v in c.items() if k not in ["geometry"]}
            cell_el = ET.SubElement(root_el, "mxCell", **cell_attrs)
            geom = c.get("geometry")
            if geom:
                ET.SubElement(cell_el, "mxGeometry", **geom)
                
        return diagram_el

    def export_drawio_xml(self):
        root = ET.Element("mxfile", host="app.diagrams.net", version="21.0.0")
        root.append(self.to_diagram_element())
        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")


# Common Academic Styling (Serif, crisp black-and-white borders, subtle fills)
BOX_STYLE = "rounded=0;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=12;fontStyle=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;align=center;"
ROUNDED_STYLE = "rounded=1;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=12;fontStyle=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;align=center;arcSize=15;"
DASHED_BOX = "rounded=0;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=12;fontStyle=1;strokeColor=#000000;strokeWidth=1.5;dashed=1;fillColor=#F8F9FA;align=center;"
CONTAINER_STYLE = "rounded=0;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=13;fontStyle=1;strokeColor=#333333;strokeWidth=1.5;fillColor=#FDFDFD;verticalAlign=top;align=left;spacingLeft=10;spacingTop=5;"
TITLE_STYLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=16;fontStyle=1;"
CAPTION_STYLE = "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontFamily=Times New Roman;fontSize=13;fontStyle=2;"
ARROW_STYLE = "endArrow=classic;html=1;strokeColor=#000000;strokeWidth=1.5;fontSize=11;fontFamily=Times New Roman;rounded=0;"
DASHED_ARROW = "endArrow=classic;html=1;strokeColor=#000000;strokeWidth=1.5;dashed=1;fontSize=11;fontFamily=Times New Roman;rounded=0;"
DIAMOND_STYLE = "rhombus;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=11;fontStyle=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;align=center;"
ELLIPSE_STYLE = "ellipse;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=11;fontStyle=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;align=center;"
ACTOR_STYLE = "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fontFamily=Times New Roman;fontSize=12;fontStyle=1;strokeColor=#000000;strokeWidth=1.5;fillColor=#FFFFFF;"
DATASTORE_STYLE = "shape=partialRectangle;top=0;bottom=0;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=11;fontStyle=1;align=center;"
EXTERNAL_ENTITY = "rounded=0;whiteSpace=wrap;html=1;fontFamily=Times New Roman;fontSize=12;fontStyle=1;strokeColor=#000000;strokeWidth=2;fillColor=#FFFFFF;align=center;"

print("DrawIO builder module defined successfully.")
