from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
 
class OperadoresList(models.Model):
    _name = 'operadores.list'
    _inherit = ['mail.thread']
    _description = 'Lista de choferes'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _mail_post_access = 'read'
    _check_company_auto = True
    
    name = fields.Char(string= 'name', required=True, copy=False)
    ine = fields.Char(string= 'INE', required=True, copy=False)
    licencia = fields.Char(string= 'Licencia', required=True, copy=False)
    curp = fields.Char(string= 'CURP', copy=False)
    estatus = fields.Boolean(string= 'Activo', default='1')  
    fecha_alta = fields.Datetime(string= 'Fecha alta', readonly=True, default=fields.Datetime.now)
    fecha_modificacion = fields.Datetime(string= 'Fecha Modificación', readonly=True, default=fields.Datetime.now)
    comentarios = fields.Char(string= 'Observaciones')
    categoria = fields.Char(string= 'Categoria', readonly=True, default='Chofer')
    user_id = fields.Many2one('res.users', string="Usuario", check_company=True, domain="[('company_ids', 'in', company_id)]", default=lambda self: self.env.uid)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    status_registrado = fields.Boolean(string='Bandera', readonly=True)

    # Guardar registro
    def btn_registrar(self):
        # validaciones basicas para reducir basura
        if self.name == '':
           raise UserError (("OBLIGATORIO un nombre de chofer")) 
        else:
            self.name = self.name.title()

        if self.ine != 'NA' and self.ine != 'na' and len(self.ine)  != 18 :
           raise UserError (("INE debe ser de 18 caracteres o NA, verifique"))
        else:
            self.ine = self.ine.upper() 

        if self.licencia != 'NA' and self.licencia != 'na' and len(self.licencia) < 12:
            raise UserError (("Licencia debe ser de minimo 12 caracteres o NA, verifique")) 
        else:
            self.licencia = self.licencia.upper()
            
        if self.curp != 'NA' and self.curp != 'na' and len(self.curp) != 18:
            raise UserError (("CURP debe ser de 18 caracteres o NA, verifique"))   
        else:
            self.curp = self.curp.upper()      

        if self.estatus == False:
            raise UserError (("AVISO: Indique motivo de desactivar-betar al chofer"))  
        
        self.status_registrado = True               
                       
     # Actualizar registro 
    def btn_actualizar(self):
        # validaciones basicas para reducir basura
        if self.ine != 'NA' and self.ine != 'na' and len(self.ine)  != 18 :
           raise UserError (("INE no tiene 18 caracteres, verifique"))
        else:
            self.ine = self.ine.upper() 

        if self.licencia != 'NA' and self.licencia != 'na' and len(self.licencia) < 12:
            raise UserError (("Licencia tiene menos de 12 caracteres, verifique")) 
        else:
            self.licencia = self.licencia.upper()
        
        if self.curp != 'NA' and self.curp != 'na' and len(self.curp) != 18:
            raise UserError (("CURP no tiene 18 caracteres, verifique")) 
        else:    
             self.curp = self.curp.upper()    

        if self.estatus == False:
            raise UserError (("AVISO: Indique motivo de desactivar-betar al chofer"))                       
                
        self.status_registrado = True            
        self.fecha_modificacion = fields.Datetime.now()
        