GUI_PARAMETERS = """[
    {
    "type":"number",
    "name":"Geometry/Undo previous action",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Heal/ CAD",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Heal/ Surfaces",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Add/A point on a curve (ratio)",
    "values":[0],
    "min":0,
    "max":1,
    "step":0.1
    },
    {
    "type":"number",
    "name":"Geometry/Add/A surface by curve loop",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Add/A surface by point loop",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Split/A surface by a curve",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Add/A volume between two surfaces",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Project/A point on a curve",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Project/A surface on a surface",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Split/A volume by an infinite plane (3 points)",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Split/A volume by a finite plane (4 points)",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Split/A volume by a point loop",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Split/A triangle surface",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Split/A wedge volume",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Remove/Surfaces",
    "values":[0],
    "choices":[0, 1]
    },
    
    {
    "type":"number",
    "name":"Geometry/Remove/Curves",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Remove/All orphan curves",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Remove/All duplicates",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Merge/Two Curves",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Geometry/Merge/Two Surfaces",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"Mesh/Set number of nodes on /One edge",
    "values":[5],
    "min":1,
    "max":100,
    "step":1
    },
    {
    "type":"number",
    "name":"Mesh/Set number of nodes on /All edges",
    "values":[5],
    "min":1,
    "max":100,
    "step":1
    },
    {
    "type":"number",
    "name":"View/Show all volumes",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"View/Hide all meshable volumes",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"View/Hide all non-meshable volumes",
    "values":[0],
    "choices":[0, 1]
    },
    {
    "type":"number",
    "name":"View/Hide volumes by selecting a surface",
    "values":[0],
    "choices":[0, 1]
    },
    {
        "type":"string", 
        "name":"ONELAB/Button", 
        "values":["Mesh CAD", "Write mesh"],
        "visible":false
    }
]"""
