from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date

class BoletasChatarra(models.Model):
    _check_company_auto = True
    _name = "boletas.chatarra"
    _description = 'Boletas Chatarra'
    _order = 'name'
    _inherit = ['mail.thread']

    ciclo_camion_id = fields.Many2one(comodel_name='ciclo.camion', string='Referencia Ciclo Camion')
    name = fields.Char('Referencia', required=True, copy=False, readonly=True, default='New')
    pase_acceso_ch = fields.Many2one(related='ciclo_camion_id.pase_acceso_cc', string= 'Pase Acceso')
    placas_vehiculo_ch = fields.Many2one(related="ciclo_camion_id.placas_tracto_cc", string='Placas Tracto')
    nombre_chofer_ch = fields.Many2one(related="ciclo_camion_id.chofer_cc", string='Chofer')
    fecha_registro_ch = fields.Datetime(string='Fecha de Registro', default=fields.Datetime.now)
    estatus_camion_ch = fields.Selection(related="ciclo_camion_id.estatus_camion_cc", string='Estatus Camion', readonly=True)
    nombre_clasificador = fields.Many2one('res.users', string='Clasificador', index=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Empresa', required=True, index=True, default=lambda self: self.env.company)
    clasificacion_chatarra = fields.Many2one(comodel_name='product.product', string='Clasificacion de Chatarra')
    peso_remisionado_ch = fields.Float(string='Peso Remisionado')
    impureza_ch = fields.Float(string='Impureza(%)')
    merma_chatarra = fields.Float(string='Merma de Chatarra')
    #ubicacion_destino_ch = fields.Char(related='ciclo_camion_id.tipo_operacion_cc.default_location_dest_id', string='Ubicacion Destino')
    notas_clasificador = fields.Char(string='Notas Clasificador')
    ancho_caja_ch = fields.Float(string='Ancho de Caja (m)')
    largo_caja_ch = fields.Float(string='Largo de Caja (m)')
    alto_caja_ch = fields.Float(string='Alto de Caja(m)')
    volumen_caja_ch = fields.Float(string='Volumen de caja')
    densidad_remisionada_ch = fields.Float(string='Densidad Remisionada')

    # @api.depends('volumen_caja_ch', 'ancho_caja_ch', 'largo_caja_ch', 'alto_caja_ch')
    # def _compute_volumen(self):
    #     for record in self:
    #         record.volumen_caja_ch = (record.ancho_caja_ch * record.largo_caja_ch * record.alto_caja_ch)

    # @api.depends('densidad_remisionada_ch', 'peso_remisionado_ch', 'volumen_caja_ch')
    # def _compute_densidad(self):
    #     for record in self:
    #         if record.peso_remisionado_ch > 0 and record.volumen_caja_ch >= 0:
    #             record.peso_remisionado_ch = (record.peso_remisionado_ch / record.volumen_caja_ch)
    #         else:
    #             record.densidad_remisionada_ch = 0  

    def btn_registrar_clasificacion(self):
        self.fecha_registro_ch = fields.Datetime.now()
        self.ciclo_camion_id.estatus_camion_cc = 'stts_b2'
        self.volumen_caja_ch = (self.ancho_caja_ch * self.largo_caja_ch * self.alto_caja_ch)
        if self.peso_remisionado_ch > 0 and self.volumen_caja_ch == 0:
                self.densidad_remisionada_ch = (self.peso_remisionado_ch / self.volumen_caja_ch)
        else:
            self.densidad_remisionada_ch = 0  

