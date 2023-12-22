from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date

class RegistroEntrada(models.Model):
    _check_company_auto = True
    _name = "registro.entrada"
    _description = 'Registro Entrada'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default='New')
    tipo_movimiento_id = fields.Many2one(comodel_name='stock.picking.type', string='Tipo de operacion')
    contacto_id = fields.Many2one(comodel_name='res.partner', string='Contacto')
    chofer_vg = fields.Many2one(comodel_name='operadores.list', string='Chofer')
    ine_vg = fields.Char(related='chofer_vg.ine', string='Ine')
    curp_vg = fields.Char(related='chofer_vg.curp', string='Curp')
    licencia_vg = fields.Char(related='chofer_vg.licencia', string='Licencia')
    placas_vehiculo_vg = fields.Many2one(comodel_name='unidadestransporte.list', string='Placas del Vehiculo')
    tipo_unidad_vg = fields.Selection(related='placas_vehiculo_vg.tipo_unidad', string='Tipo Unidad vg' )
    placas_remolque_vg = fields.Many2one(comodel_name='unidadestransporte.list', string='Placas Remolque')
    estatus_vigilancia = fields.Selection(selection=[('stts_pr', 'Pre-registro'),('stts_ev', 'Entrada Vigilancia'),('stts_ep', 'En Planta'),('stts_sv', 'Salida Vigilancia'),], string='Estatus Vigilancia', default='stts_pr')
    estatus_autorizacion = fields.Selection(selection=[('stts_ee', 'En espera'),('stts_rqd', 'Requerido'),], string='Autorizacion')
    fecha_preregistro = fields.Datetime(string='Pre-registro Fecha', default=fields.Datetime.now)
    fecha_requerido = fields.Datetime(string='Requerido Fecha')
    fecha_entrada = fields.Datetime(string='Fecha ingreso a planta')
    fecha_salida = fields.Datetime(string='Fecha salida')
    nombre_vigilante = fields.Many2one('res.users', 'Vigilante', index=True, default=lambda self: self.env.user)
    nombre_autoriza = fields.Many2one('res.users', 'Autoriza', index=True)
    nombre_ingreso = fields.Many2one('res.users', 'Ingreso', index=True)
    company_id = fields.Many2one('res.company', 'Empresa', required=True, index=True, default=lambda self: self.env.company)
    notas_vigilancia = fields.Char(string='Notas Vigilancia')
    producto_remisionado = fields.Char(string='Producto Remisionado')
    origen_producto = fields.Char(string='Origen del Producto')
    destino_producto = fields.Char(string='Destino del Producto')
    prefijo_operacion = fields.Char(related='tipo_movimiento_id.sequence_code', string='Prefijo secuencia', readonly=True)
    ciclo_camion_ids = fields.One2many('ciclo.camion','pase_acceso_cc', string='Ciclo camion ids')
    estatus_camion_vg = fields.Selection(related='ciclo_camion_ids.estatus_camion_cc', string='Estatus Camion')
    transportes_ciclo_camion_count = fields.Integer(compute="_compute_transporte_count")

    def btn_preregistro(self):
        self.estatus_vigilancia = 'stts_pr'
        self.estatus_autorizacion = 'stts_ee'
                        
    def btn_autorizar(self):
        self.fecha_requerido = fields.Datetime.now()
        self.estatus_vigilancia = 'stts_ev'
        self.estatus_autorizacion = 'stts_rqd'
        self.nombre_autoriza = self.env.user

    def btn_ingresar(self):
        self.fecha_entrada = fields.Datetime.now()
        self.nombre_ingreso = self.env.user
        self.estatus_vigilancia = 'stts_ep'
        #Se crea el primer ciclo de camión
        dic = {'pase_acceso_cc': self.id,'tipo_operacion_cc': self.tipo_movimiento_id.id}
        ciclo = self.env['ciclo.camion'].create(dic)
        ciclo['estatus_camion_cc'] = 'stts_b1'
        ciclo['responsable_cc'] = self.env.user
        ciclo.crear_boletas()

    def btn_cerrar(self):
        self.fecha_salida = fields.Datetime.now()
        self.estatus_vigilancia = 'stts_sv'
    
    #----S E C U E N C I A  V I G I L A N C I A-----
    @api.model
    def create(self,vals):
        if vals.get('name', 'New') == 'New':
           vals['name']= self.env['ir.sequence'].next_by_code('registro.entrada') or 'New'
        return super(RegistroEntrada, self).create(vals)

     # ---CONTADOR BOTON INTELIGENTE ---
    def _compute_transporte_count(self):
        for record in self:
            record.transportes_ciclo_camion_count = record.env['ciclo.camion'].search_count([('pase_acceso_cc','=', record.id)])

    #--- ACCION VENTANA BOTON INTELIGENTE ---
    def get_ciclos_camion(self):
        self.ensure_one()
        return {
            'name': ('Transportes'),
            'type': 'ir.actions.act_window',
            'res_model': 'ciclo.camion',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('pase_acceso_cc', '=', self.id)],
            'context': {'search_default_pase_acceso_cc': self.id,'default_pase_acceso_cc': self.id},
        }
        
