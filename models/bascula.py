from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date

class Bascula(models.Model):
    _check_company_auto = True
    _name = "bascula"
    _description = 'Bascula'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'
    
    name = fields.Char('Referencia', required=True, copy=False, readonly=True, default='New')
    ciclo_camion_id = fields.Many2one(comodel_name='ciclo.camion', string='Referencia Ciclo Camion')
    pase_acceso_b = fields.Many2one(comodel_name='registro.entrada', string='Pase Acceso')
    referencia_vigilancia = fields.Many2one(related="ciclo_camion_id.pase_acceso_cc", string='Pase Acceso')
    placas_vehiculo = fields.Many2one(related="ciclo_camion_id.placas_tracto_cc", string='Placas Tracto')
    nombre_chofer = fields.Many2one(related="ciclo_camion_id.chofer_cc", string='Chofer')
    estatus_camion_b = fields.Selection(related="ciclo_camion_id.estatus_camion_cc", string='Estatus Camion', readonly=True)
    estatus_vigilancia_b = fields.Selection(related="ciclo_camion_id.pase_acceso_cc.estatus_vigilancia", string='Estatus Vigilancia', readonly=True)
    fecha_primer_pesada_b = fields.Datetime(string='Fecha Primera Pesada')
    fecha_segunda_pesada_b = fields.Datetime(string='Fecha Segunda Pesada')
    nombre_basculista_b = fields.Many2one('res.users', string='Basculista', index=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Empresa', required=True, index=True, default=lambda self: self.env.company)
    notas_basculista = fields.Char('Notas Basculista')
    producto_remisionado_b = fields.Many2one(related='ciclo_camion_id.pase_acceso_cc.producto_remisionado', string='Producto Remisionado')
    producto_registrado_b = fields.Many2one(comodel_name='product.product', string='Producto Registrado') 
    peso_bruto_b = fields.Float(string='Peso Bruto')
    peso_tara_b = fields.Float(string='Peso Tara')
    peso_neto_b = fields.Float(compute='_compute_peso_neto',string='Peso Neto')
    impureza_porcentaje_b = fields.Float(related="ciclo_camion_id.boleta_chatarra_cc.impureza_ch", string='Impureza(%)')
    impureza_cantidad_b = fields.Float(compute='_compute_impureza',string='Impureza')
    peso_neto_pagar_b = fields.Float(compute='_compute_peso_pagar',string='Peso Neto a Pagar')
    paso_siguiente = fields.Selection(selection=[('nuevo_ciclo', 'Nuevo Ciclo'),('salida_vigilancia', 'Salida Vigilancia')], string='Paso Siguiente')
    chatarra_clasificada_b = fields.Many2one(related='ciclo_camion_id.boleta_chatarra_cc.clasificacion_chatarra', string='Chatarra Clasificada')
    producto_almacen_b = fields.Many2one(related='ciclo_camion_id.boleta_almacen_cc.producto_recibido_alm', string='Producto Almacen')

    # @api.depends('producto_registrado_b', 'producto_almacen_b', 'chatarra_clasificada_b')
    # def _compute_product(self):
    #     if self.estatus_camion_b == 'stts_b2':
    #         for record in self:
    #             if record.producto_almacen_b.id != False:
    #                 record.producto_registrado_b = record.producto_almacen_b
    #             elif record.chatarra_clasificada_b.id != False:
    #                     record.producto_registrado_b = record.chatarra_clasificada_b

    def _compute_impureza(self):
        for record in self:
            record.impureza_cantidad_b = ((record.peso_bruto_b - record.peso_tara_b) * record.impureza_porcentaje_b) / 100
    def _compute_peso_neto(self):
        for record in self:
            record.peso_neto_b = (record.peso_bruto_b - record.peso_tara_b)
    def _compute_peso_pagar(self):
        for record in self:
            record.peso_neto_pagar_b = (record.peso_neto_b - record.impureza_cantidad_b)

    def btn_peso_bruto(self):
        # raise UserError("Peso Bruto")
        if self.peso_bruto_b == 0:
            raise UserError("El peso bruto no puede ser 0")
            
        if self.peso_bruto_b < 0:
            self.peso_bruto_b == 0
            raise UserError("No puede haber negativos")
            
        if self.peso_bruto_b >= 60000:
            self.peso_bruto_b = 0
            raise UserError("Peso bruto excedió el limite 60 TN maximo")
            
        self.ciclo_camion_id.estatus_camion_cc = 'stts_cd'
        self.fecha_primer_pesada_b = fields.Datetime.now()

    def btn_ultima_pesada(self):
        # raise UserError("Ultima Pesada")
        self.fecha_segunda_pesada_b = fields.Datetime.now()
        #recibir producto
        if self.ciclo_camion_id.tipo_operacion_cc.code == 'incoming':
            if self.peso_tara_b > self.peso_bruto_b:
                raise UserError('El peso tara no debe exceder el peso bruto')
        # obtener producto para validacion
        if self.estatus_camion_b == 'stts_b2':
            if self.producto_almacen_b.id != False:
                self.producto_registrado_b = self.producto_almacen_b
            elif self.chatarra_clasificada_b.id != False:
                    self.producto_registrado_b = self.chatarra_clasificada_b
        #Traslado interno OUT producto
        if self.ciclo_camion_id.tipo_operacion_cc.code == 'internal':
            if self.peso_bruto_b > peso_tara_b:
                raise UserError('El peso bruto no debe exceder el peso tara')

        if self.ciclo_camion_id.tipo_operacion_cc.sequence_code == 'IN-Chatarra':
            self.ciclo_camion_id.estatus_camion_cc = 'stts_v2'
            self.paso_siguiente = 'salida_vigilancia'

        if self.ciclo_camion_id.tipo_operacion_cc.sequence_code == 'IN-Insumos':
            self.ciclo_camion_id.estatus_camion_cc = 'stts_ra'
            self.paso_siguiente = 'salida_vigilancia'

        if self.peso_neto_b < 0:
            raise UserError("No puede haber negativos")
        if self.peso_bruto_b == self.peso_neto_b:
            raise UserError("Error en validar el peso")

    def btn_nuevo_ciclo(self):
        #Recibir producto
        if self.ciclo_camion_id.tipo_operacion_cc.code == 'incoming':
            if self.peso_tara_b > self.peso_bruto_b:
                raise UserError('El peso tara no debe exceder el peso bruto')
        #Traslado interno OUT producto
        if self.ciclo_camion_id.tipo_operacion_cc.code == 'internal':
            if self.peso_bruto_b > peso_tara_b:
                raise UserError('El peso bruto no debe exceder el peso tara')
        # obtener producto para validacion
        if self.estatus_camion_b == 'stts_b2':
            if self.producto_almacen_b.id != False:
                self.producto_registrado_b = self.producto_almacen_b
            elif self.chatarra_clasificada_b.id != False:
                    self.producto_registrado_b = self.chatarra_clasificada_b
        #  raise UserError("Nuevo ciclo")
        self.fecha_segunda_pesada_b = fields.Datetime.now()
        if self.ciclo_camion_id.tipo_operacion_cc.sequence_code == 'IN-Chatarra':
            if self.ciclo_camion_id.boleta_chatarra_cc:
                self.ciclo_camion_id.estatus_camion_cc = 'stts_v2'
                self.paso_siguiente = 'salida_vigilancia'
                dic = {'pase_acceso_cc': self.ciclo_camion_id.pase_acceso_cc.id,
                'tipo_operacion_cc': self.ciclo_camion_id.tipo_operacion_cc.id,
                'contacto_cc': self.ciclo_camion_id.contacto_cc.id
                }
                ciclo = self.env['ciclo.camion'].create(dic)
                ciclo['estatus_camion_cc'] = 'stts_b1'
                ciclo.crear_boletas()
        if self.ciclo_camion_id.tipo_operacion_cc.sequence_code == 'IN-Insumos':
            self.ciclo_camion_id.estatus_camion_cc = 'stts_ra'
            self.paso_siguiente = 'nuevo_ciclo'
        
        

    









