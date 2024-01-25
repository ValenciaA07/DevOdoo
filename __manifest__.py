{
    'name': 'Simec - Ciclo Camion',
    'summary': 'Ciclo de camion de entrada y salida de producto',
    'description': '''
        El modulo sigue ciertos estatus para completar el ciclo del camion de entrada y salida de productos, generando al final su recepcion y/o oc.
        Developer: CAVG
    ''',
    'author': 'Grupo Simec, S.A.B. de C.V.',
    'website': 'https://gsimec.com.mx',
    'category': 'Custom Development',
    'version': '1.0.0',
    'depends': ['stock', 'purchase_requisition', 'purchase'],
    'data': [
        "security/ir.model.access.csv",
        "data/secuence_vigilancia.xml",
        "views/registro_entrada_views.xml",
        "views/bascula_views.xml",
        "views/boletas_chatarra.xml",
        "views/boletas_almacen.xml",
        "views/ciclo_camion.xml",
        "views/operadores_list_views.xml",
        "views/unidadestransporte_views.xml",
        "views/stock_picking_views.xml",
        "views/purchase_order_views.xml"
    ],
    'assets':{
        "web.assets_backend":[
            "/simec_ciclo_camion/static/src/js/code_fields.js",
            "/simec_ciclo_camion/static/src/xml/widget_file.xml",
        ]
    },
    'license': "LGPL-3",
    "installable": True,
    "application": False,
}