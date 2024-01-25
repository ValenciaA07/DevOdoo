from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date

class CicloCamion(models.Model):
    _check_company_auto = True
    _name = "ciclo.camion"
    _description = 'Ciclo de Camion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'

    name = fields.Char(string='Referencia', required=True, copy=False, readonly=True, default='New')
    pase_acceso_cc = fields.Many2one(comodel_name='registro.entrada', string='Pase Acceso')
    responsable_cc = fields.Many2one('res.users', string='Responsable', index=True, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Empresa', required=True, index=True, default=lambda self: self.env.company)
    contacto_cc = fields.Many2one(related="pase_acceso_cc.contacto_id", string='Contacto', readonly=True)
    tipo_operacion_cc = fields.Many2one(related="pase_acceso_cc.tipo_movimiento_id", string='Tipo Movimiento', readonly=True)
    contrato_compra_cc = fields.Many2one('purchase.requisition', string='Contrato de Compra')
    orden_compra_peso_cc = fields.Many2one(comodel_name="purchase.order", string="Orden de Compra con Peso")
    estatus_camion_cc = fields.Selection(selection=[('stts_b1', 'Báscula primer pesada'),('stts_cd', 'Descargando/Cargando'),('stts_b2', 'Báscula segunda pesada'),('stts_ra', 'Confirmar Almacen'),('stts_v2', 'Cerrado'),('stts_bc', 'Boleta Confirmada')], string='Estatus Camion')
    estatus_vigilancia_cc = fields.Selection(related="pase_acceso_cc.estatus_vigilancia", string='Estatus Vigilancia', readonly=True)
    prefijo_operacion_cc = fields.Char(related='tipo_operacion_cc.sequence_code', string='Prefijo secuencia', readonly=True)
    purchase_order_count = fields.Integer(compute="_compute_purchase_order_count")
    stock_picking_count = fields.Integer(compute="_compute_stock_picking_count")
        #---------VIGILANCIA---------------
    placas_tracto_cc = fields.Many2one(related="pase_acceso_cc.placas_vehiculo_vg", string='Placa Tracto')
    chofer_cc = fields.Many2one(related="pase_acceso_cc.chofer_vg", string='Chofer')
    placas_remolque_cc = fields.Many2one(related="pase_acceso_cc.placas_remolque_vg", string='Placa Remolque')
    vigilante_cc = fields.Many2one(related="pase_acceso_cc.nombre_vigilante", string='Vigilante', readonly=True)
    fecha_ingreso_cc = fields.Datetime(related="pase_acceso_cc.fecha_entrada", string='Fecha Ingreso', readonly=True)
    fecha_salida_cc = fields.Datetime(related="pase_acceso_cc.fecha_salida", string='Fecha Salida', readonly=True)
    #-------BOLETA BASCULA--------------
    boleta_bascula_id = fields.Many2one(comodel_name='bascula', string='Referencia Bascula')
    basculista_cc = fields.Many2one(related="boleta_bascula_id.nombre_basculista_b", string='Basculista', readonly=True)
    fecha_primer_pesada_cc = fields.Datetime(related="boleta_bascula_id.fecha_primer_pesada_b", string='Fecha Primera Pesada')
    fecha_segunda_pesada_cc = fields.Datetime(related="boleta_bascula_id.fecha_segunda_pesada_b", string='Fecha Segunda Pesada')
    producto_registrado_cc = fields.Many2one(related="boleta_bascula_id.producto_registrado_b", string='Producto Registrado')
    peso_bruto_cc = fields.Float(related="boleta_bascula_id.peso_bruto_b", string='Peso Bruto')
    peso_tara_cc = fields.Float(related="boleta_bascula_id.peso_tara_b", string='Peso Tara')
    peso_neto_cc = fields.Float(related="boleta_bascula_id.peso_neto_b", string='Peso Neto')
    impureza_cc = fields.Float(related="boleta_bascula_id.impureza_porcentaje_b", string='Peso Neto')
    peso_pagar_cc = fields.Float(related="boleta_bascula_id.peso_neto_pagar_b", string='Peso Neto a Pagar')
    #--------BOLETA CHATARRA-------------
    boleta_chatarra_cc = fields.Many2one(comodel_name='boletas.chatarra', string='Boletas Chatarra')
    clasificador_cc = fields.Many2one(related="boleta_chatarra_cc.nombre_clasificador", string='Clasificador')
    clasificacion_chat_cc = fields.Many2one(related="boleta_chatarra_cc.clasificacion_chatarra", string='Clasificacion Chatarra')
    volumen_caja_cc = fields.Float(related="boleta_chatarra_cc.volumen_caja_ch", string='Volumen Caja')
    densidad_caja_cc = fields.Float(related="boleta_chatarra_cc.densidad_remisionada_ch", string='Densidad Remisionada')
    notas_clasificador_cc = fields.Char(related="boleta_chatarra_cc.notas_clasificador", string='Notas Clasificador')
    # --------BOLETA ALMACEN----------------
    boleta_almacen_cc = fields.Many2one(comodel_name="boletas.almacen", string="Boletas Almacen")
    producto_recibido_cc = fields.Many2one(related="boleta_almacen_cc.producto_recibido_alm", string='Producto Recibido')
    almacen_cc = fields.Selection(related="boleta_almacen_cc.nombre_almacen", string='Almacen')
    almacenista_cc = fields.Many2one(related="boleta_almacen_cc.nombre_almacenista", string='Almacenista')
    fecha_inicial_cc = fields.Datetime(related="boleta_almacen_cc.fecha_inicial", string='Fecha Inicial')
    fecha_final_cc = fields.Datetime(related="boleta_almacen_cc.fecha_final", string='Fecha Final')
    # --------OTRA INFORMACION------------
    orden_compra_id = fields.Many2one(comodel_name="purchase.order", string="OC")
    trasladar_id = fields.Many2one(comodel_name="stock.picking", string="Traslado")

    def btn_ConfirmarBoleta(self):
    # raise UserError("Boleta confirmada")
        if self.tipo_operacion_cc.sequence_code == 'IN-Chatarra' :
            if not self.orden_compra_id :
                var_po = {
                 'ciclo_camion_id': self.id,
                 'partner_id': self.contacto_cc.id,
                 'requisition_id': self.contrato_compra_cc.id,
                 'picking_type_id': self.tipo_operacion_cc.id,
                 'date_planned': fields.Datetime.now(),
                 'origin': self.contrato_compra_cc.name,
                 'company_id': self.company_id.id,
                 'tipo_orden_compra': 'CH'
                 }
                new_purchase_order = self.env['purchase.order'].create(var_po)
                self.orden_compra_id = new_purchase_order.id
     
                precio_prod = 0
                for var_order_line in self.contrato_compra_cc.line_ids :
                    if var_order_line.product_id.id == self.boleta_bascula_id.producto_registrado_b.product_variant_id.id and self.contrato_compra_cc.vendor_id.id == self.contacto_cc.id :
                        precio_prod = var_order_line.price_unit/1000
                        break
                var_po_line = {  
                    'product_id': self.boleta_bascula_id.producto_registrado_b.product_variant_id.id,
                    'name': f"{self.boleta_bascula_id.producto_registrado_b.name}-{self.name}",
                    'date_planned': fields.Datetime.now(),
                    'product_qty': self.boleta_bascula_id.peso_neto_b,
                    'order_id': new_purchase_order.id,
                    'partner_id': self.contacto_cc.id,
                    'product_uom': 12,
                    'price_unit': precio_prod
                }
                purchase_order_line = self.env['purchase.order.line'].create(var_po_line)
     
                res = new_purchase_order.button_confirm()
                if isinstance(res, dict):
                    action = res
     
                var_stock_moves = new_purchase_order.picking_ids
     
                for new_stock_move in var_stock_moves:
                    self.trasladar_id = new_stock_move
                    self.trasladar_id.ciclo_camion_id = self.id
                    break
    
                res = self.trasladar_id.action_set_quantities_to_reservation()
                if isinstance(res, dict):
                    action = res
    
                res = self.trasladar_id.button_validate()
                if isinstance(res, dict):
                    action = res
     
        if self.tipo_operacion_cc.sequence_code == 'IN-Insumos' :
            if not self.orden_compra_peso_cc.ciclo_camion_id :
                self.orden_compra_peso_cc.ciclo_camion_id = self.id
        self.estatus_camion_cc = 'stts_bc'
 
    
     #---------S E C U E N C I A  R E F E R E N C I A------
    @api.model
    def create(self,vals):
        if vals.get('name', 'New') == 'New':
           vals['name']= self.env['ir.sequence'].next_by_code('referencia.camion') or 'New'
        return super(CicloCamion, self).create(vals)

    def crear_boletas(self):
        if self.tipo_operacion_cc.sequence_code == 'IN-Chatarra':
            if not self.boleta_bascula_id:
                dic = {'ciclo_camion_id': self.id, 'name': self.name}
                bascula = self.env['bascula'].create(dic)
                self.boleta_bascula_id = bascula.id
            if not self.boleta_chatarra_cc:
                dic = {'ciclo_camion_id': self.id, 'name': self.name}
                boleta_chatarra = self.env['boletas.chatarra'].create(dic)
                self.boleta_chatarra_cc = boleta_chatarra.id
        elif self.tipo_operacion_cc.sequence_code == 'IN-Insumos':
            if not self.boleta_bascula_id:
                dic = {'ciclo_camion_id': self.id, 'name': self.name}
                bascula = self.env['bascula'].create(dic)
                self.boleta_bascula_id = bascula.id
            if not self.boleta_almacen_cc:
                dic = {'ciclo_camion_id': self.id, 'name': self.name}
                boleta_almacen = self.env['boletas.almacen'].create(dic)
                self.boleta_almacen_cc = boleta_almacen.id

    # ---CONTADOR BOTON INTELIGENTE ---
    def _compute_purchase_order_count(self):
        for record in self:
            record.purchase_order_count = record.env['purchase.order'].search_count([('ciclo_camion_id','=', record.id)])
    #--- ACCION VENTANA BOTON INTELIGENTE ---
    def get_purchase_order(self):
        self.ensure_one()
        return {
            'name': ('Orden de Compra'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('ciclo_camion_id', '=', self.id)],
            'context': {'search_default_ciclo_camion_id': self.id,'default_ciclo_camion_id': self.id},
        }

    # ---CONTADOR BOTON INTELIGENTE ---
    def _compute_stock_picking_count(self):
        for record in self:
            record.stock_picking_count = record.env['stock.picking'].search_count([('ciclo_camion_id','=', record.id)])
       #--- ACCION VENTANA BOTON INTELIGENTE ---
    def get_stock_picking(self):
        self.ensure_one()
        return {
            'name': ('Recepción'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('ciclo_camion_id', '=', self.id)],
            'context': {'search_default_ciclo_camion_id': self.id,'default_ciclo_camion_id': self.id},
        }
