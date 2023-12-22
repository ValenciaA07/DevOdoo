from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date

class BoletasAlmacen(models.Model):
    _check_company_auto = True
    _name = "boletas.almacen"
    _description = 'Boletas Almacen'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'

    name = fields.Char('Referencia', required=True, copy=False, readonly=True, default='New')
    ciclo_camion_id = fields.Many2one(comodel_name='ciclo.camion', string='Referencia Ciclo Camion')
    pase_acceso_alm = fields.Many2one(related='ciclo_camion_id.pase_acceso_cc', string='Pase Acceso')
    producto_recibido_alm = fields.Many2one(comodel_name='product.product', string='Producto Recibido')
    estatus_camion_alm = fields.Selection(related='ciclo_camion_id.estatus_camion_cc', string='Estatus Camion')
    estatus_vigilancia_alm = fields.Selection(related="ciclo_camion_id.estatus_vigilancia_cc", string='Estatus Vigilancia', readonly=True) 
    nombre_almacen = fields.Selection(selection=[('stts_blt', 'Billet'),('stts_ins', 'Insumos'),('stts_mp', 'Materia Prima'),('stts_rf', 'Refacciones'),('stts_rfcs', 'Refractarios'),('stts_rd', 'Rodillos'),('stts_pt', 'Producto Terminado')], string='Almacen')
    fecha_inicial = fields.Datetime(string='Fecha Inicial', default=fields.Datetime.now)
    fecha_final = fields.Datetime(string='Fecha Final')
    notas_almacen = fields.Char(string='Notas Almacen')
    nombre_almacenista = fields.Many2one('res.users', string='Almacenista', index=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Empresa', required=True, index=True, default=lambda self: self.env.company)

    def btn_registrar_producto(self):
        self.fecha_inicial = fields.Datetime.now()
        self.ciclo_camion_id.estatus_camion_cc = 'stts_b2'
         
    def btn_confirmar(self):
        self.fecha_final = fields.Datetime.now()
        self.ciclo_camion_id.estatus_camion_cc = 'stts_v2'
         
