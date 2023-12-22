from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, date

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ciclo_camion_id = fields.Many2one(comodel_name='ciclo.camion', string='Ciclo de Camion')
    


   