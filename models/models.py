# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class License(models.Model):

    _name="license.license"

    _sql_constraints = [('license_product_uniq', 'unique (products)',     
                 'Duplicate products in license line not allowed !')]
    
    status=fields.Selection([("draft","Draft"),("confirmed","Confirmed"),("expired","Expired")],string="Status",default="draft")
    license_number = fields.Char(string="License Number",required=True)
    license_issue_date = fields.Date(string="License Issue Date",required=True)
    license_poe = fields.Many2one("license.poe",string="License Port of Entry",required=True)
    license_expire_date = fields.Date(string="License Expiration Date",required=True)
    document_copy = fields.Binary(string="Upload Document")
    product_lines=fields.One2many("license.product","license_product_conn",string="product_lines")
    notes=fields.Text(string="Notes")
    



    def exp_check(self):
        today = datetime.date.today()
        records = self.env["license.license"].search([("license_expire_date","<",today)])
        for rcd in records:
            license_lines = rcd.product_lines.product_id.licenses
            line_id = 0
            for licen_rcd in license_lines:
                if licen_rcd.license_number == rcd.license_number:
                    line_id = licen_rcd.id
            rcd.product_lines.product_id.write({"licenses":[(2,line_id,{})]})
            rcd.status = "expired"

    


            
            
        


    def confirm_license(self):
        # vals={}
        # lines={}
        # vals.update({"license_number":self.license_number,
        #                  "license_expire_date":self.license_expire_date,
        #                  "license_issue_date":self.license_issue_date,
        #                  "license_poe":self.license_poe})
        for line in self.product_lines:
            line.product_id.write({"licenses":[(0,0,{
                         "license_number":self.license_number,
                         "license_expire_date":self.license_expire_date,
                         "license_issue_date":self.license_issue_date,
                         "license_poe":self.license_poe,
                         "quantity":line.quantity,
                         "license_id":self.id
                                })]})

        self.status = "confirmed"

    def update_license(self):
        for line in self.product_lines:
            lines = line.product_id.licenses
            line_id = 0
            for licen_rcd in lines:
                if licen_rcd.license_number == self.license_number:
                    line_id = licen_rcd.id
            line.product_id.write({"licenses":[(1,line_id,{
                         "license_expire_date":self.license_expire_date,
                         "license_issue_date":self.license_issue_date,
                         "license_poe":self.license_poe,
                         "quantity":line.quantity,
                                })]})
            
class PortsofEntry(models.Model):

    _name="license.poe"
    
    name = fields.Char(string="Port of Entry")


class ProductsofLicense(models.Model):
    _name="license.product"
    
    license_product_conn = fields.Many2one("license.license",readonly=True,invisible=True)
    product_license_link = fields.Many2one("product.template",readonly=True,invisible=True)
    license_id = fields.Many2one("license.license",readonly=True,invisible=True)
    product_id= fields.Many2one('product.product', string="products")
    quantity = fields.Integer(string="Certification Quantity")
    license_number = fields.Char(string="License Number",readonly=True)
    license_issue_date = fields.Date(string="License Issue Date",readonly=True)
    license_poe = fields.Many2one("license.poe",string="License Port of Entry",readonly=True)
    license_expire_date = fields.Date(string="License Expiration Date",readonly=True)    

class ProductLicense(models.Model):
    _inherit="product.template"
    
    licenses = fields.One2many("license.product","product_license_link",readonly=True)
    
class PurchaseLicense(models.Model):
    _inherit="purchase.order"

    enforce_license = fields.Boolean(string="Enforce Licenses on this P.O")

    def button_confirm(self):
        
        if not self.enforce_license:
            res = super(PurchaseLicense,self).button_confirm()
            return res
        else:
            for product in self.order_line:
                if product.product_id.licenses: #checks if the product has a license in its licenses field
                    list_of_lines = list(product.product_id.licenses) #returns a list of product license objects
                    sort_by_exp = lambda l: l.license_expire_date 
                    list_of_lines.sort(key=sort_by_exp)
                    subt_item = list_of_lines[0]
                    if subt_item.quantity > 0:
                        subt_item.quantity = subt_item.quantity - product.product_qty
                        self.notes= subt_item.quantity
                        license_lines = subt_item.license_id.product_lines
                        wanted_line = license_lines.search([('product_id', '=', product.product_id.id)],limit=1)
                        product.product_id.write({'licenses': [(1, wanted_line.id, {
                            'quantity': subt_item.quantity
                        })]})
                        if subt_item.quantity == 0 :
                            product.product_id.write({"licenses":[(2,subt_item.id,{})]})
                        # res = super(PurchaseLicense,self).button_confirm()
                        # return res
                    else:
                        raise UserError(_("One or more products has no valid license"))
                else:
                    raise UserError(_("One or more products has no valid license"))


                

