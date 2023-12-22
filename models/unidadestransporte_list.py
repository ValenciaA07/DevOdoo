from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
 
class UnidadesTransporteList(models.Model):
    _name = 'unidadestransporte.list'
    _inherit = ['mail.thread']
    _description = 'Lista de unidades de transporte'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'
    _check_company_auto = True
    
    name = fields.Char(string= 'name', required=True, copy=False)
    tipo_unidad = fields.Selection(selection=[('TO', 'TORTON'),('TRC', 'TRACTO'),('RML', 'REMOLQUE'), ('GON', 'GONDOLA'),('OTRO', 'OTRO'),], string='Tipo de Unidad', required=True)
    modelo = fields.Char(string= 'Año, modelo de unidad')
    configuracion = fields.Selection(selection=[('VL', 'Vehiculo de carga Ligero '),('C2', 'Camión Unitario (2 llantas en el eje delantero y 4 llantas en el eje trasero)'), 
    ('C3', 'Camión Unitario (2 llantas en el eje delantero y 6 o 8 llantas en los dos ejes traseros)'), ('C2R2', 'Camión-Remolque (6 llantas en el camión y 8 llantas en remolque)'),
    ('C3R2', 'Camión-Remolque (10 llantas en el camión y 8 llantas en remolque)'),('C2R3', 'Camión-Remolque (6 llantas en el camión y 12 llantas en remolque)'),
    ('C3R3', 'Camión-Remolque (10 llantas en el camión y 12 llantas en remolque)'),('T2S1', 'Tractocamión Articulado (6 llantas en el tractocamión, 4 llantas en el semirremolque'),
    ('T2S2', 'Tractocamión Articulado (6 llantas en el tractocamión, 8 llantas en el semirremolque)'), ('T2S3', 'Tractocamión Articulado (6 llantas en el tractocamión, 12 llantas en el semirremolque)'),
    ('T3S1', 'Tractocamión Articulado (10 llantas en el tractocamión, 4 llantas en el semirremolque)'),
    ('T3S2', 'Tractocamión Articulado (10 llantas en el tractocamión, 8 llantas en el semirremolque)'), ('T3S3', 'Tractocamión Articulado (10 llantas en el tractocamión, 12 llantas en el semirremolque'),
    ('T2S1R2', 'Tractocamión Semirremolque-Remolque (6 llantas en el tractocamión, 4 llantas en el semirremolque y 8 llantas en el remolque)'), ('T2S2R2','Tractocamión Semirremolque-Remolque (6 llantas en el tractocamión, 8 llantas en el semirremolque y 8 llantas en el remolque)'),
    ('T2S1R3', 'Tractocamión Semirremolque-Remolque (6 llantas en el tractocamión, 4 llantas en el semirremolque y 12 llantas en el remolque)'),('T3S1R2','Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 4 llantas en el semirremolque y 8 llantas en el remolque)'),
    ('T3S1R3', 'Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 4 llantas en el semirremolque y 12 llantas en el remolque)'), ('T2S2R2', 'Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 8 llantas en el semirremolque y 8 llantas en el remolque)'),
    ('T3S2R3', 'Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 8 llantas en el semirremolque y 12 llantas en el remolque)'),('T3S2R4','Tractocamión Semirremolque-Remolque (10 llantas en el tractocamión, 8 llantas en el semirremolque y 16 llantas en el remolque)'),
    ('T2S2S2','Tractocamión Semirremolque-Semirremolque (6 llantas en el tractocamión, 8 llantas en el semirremolque delantero y 8 llantas en el semirremolque trasero)'),('T3S2S2','Tractocamión Semirremolque-Semirremolque (10 llantas en el tractocamión, 8 llantas en el semirremolque delantero y 8 llantas en el semirremolque trasero)'),
    ('T3S3S2','Tractocamión Semirremolque-Semirremolque (10 llantas en el tractocamión, 12 llantas en el semirremolque delantero y 8 llantas en el semirremolque trasero)'), ('OTROEVGP','Especializado de carga Voluminosa y/o Gran Peso'),
    ('OTROSG','Servicio de Grúas'), ('GPLUTA','Grúa de Pluma Tipo A'), ('GPLUTB','Grúa de Pluma Tipo B'),
    ('GPLUTC','Grúa de Pluma Tipo C'), ('GPLUTD','Grúa de Pluma Tipo D'), ('GPLATA','Grúa de Plataforma Tipo A'),('GPLATB','Grúa de Plataforma Tipo B'),
    ('GPLATC','Grúa de Plataforma Tipo C'),('GPLATD','Grúa de Plataforma Tipo D')], string='Configuración Vehicular', required= True)
    activo = fields.Boolean(string= 'Activo', default= True)  
    comentarios = fields.Char(string= 'Observaciones')
    comentarios2 = fields.Char(string= 'Comentarios')
    fecha_alta = fields.Datetime(string= 'Fecha alta', readonly=True, default=fields.Datetime.now)
    fecha_modificacion = fields.Datetime(string= 'Fecha Modificación', readonly=True, default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string="Usuario", check_company=True, domain="[('company_ids', 'in', company_id)]", default=lambda self: self.env.uid)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    status_registrado = fields.Boolean(string='Placas Validadas', readonly=True)

    # Guardar registro
    def btn_registrar(self):
        self.name = self.name.replace('-', '')  
        self.name = self.name.replace('/', '')
        self.name = self.name.replace(' ', '')   
        
        if len(self.name) < 7:
           raise UserError (("Las placas deben ser minimo de 7 caracteres, unidad NO se ACTIVARA hasta que quede correcto"))
        else:
            self.name = self.name.upper() 
            self.status_registrado = True
            self.fecha_modificacion = fields.Datetime.now() 
        