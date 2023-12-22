from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date

class PurchaseOrder(models.Model):
    _inherit = 'stock.picking'

    ciclo_camion_id = fields.Many2one('ciclo.camion', string='Ciclo de Camion')