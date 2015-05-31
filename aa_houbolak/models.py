# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv


class aa_houbolak(models.Model):
    _inherit = 'sale.order.line'
    hoogte = fields.Float()
    breedte = fields.Float()
    aantal = fields.Float()
    #Checkboxes
    links = fields.Boolean(string='L')
    rechts = fields.Boolean(string='R')
    boven = fields.Boolean(string='B')
    onder = fields.Boolean(string='O')
    barcode = fields.Char()
    boringen = fields.Char()
    opmerkingen = fields.Char()

    def on_change_hoeveelheid_berekenen(self, cr, uid, ids, hoogte, breedte, aantal):
        resultaat = hoogte * breedte / 1000000 * aantal
        #hoeveelheid = (hoogte * breedte / 1000) * aantal
        res = {
            'value': {
                # This sets the total quantity on the field.
                'product_uom_qty': resultaat
            }
        }
        #Return the values to update it in the view.
        return res


class aa_houbolak_invoice(models.Model):
    _inherit = 'account.invoice.line'
    hoogte = fields.Float()
    breedte = fields.Float()
    aantal = fields.Float()
    #Checkboxes
    links = fields.Boolean(string='L')
    rechts = fields.Boolean(string='R')
    boven = fields.Boolean(string='B')
    onder = fields.Boolean(string='O')
    barcode = fields.Char()
    boringen = fields.Char()
    opmerkingen = fields.Char()

    def on_change_hoeveelheid_factuur_berekenen(self, cr, uid, ids, hoogte, breedte, aantal):
        resultaat = hoogte * breedte / 1000000 * aantal

        #product.product_uom_qty = cr.hoogte
        #hoeveelheid = (hoogte * breedte / 1000) * aantal
        res = {
            'value': {
                # This sets the total quantity on the field.
                'quantity': resultaat
            }
        }
        #Return the values to update it in the view.
        return res


class sale_order_line_your_extension(osv.osv):
    _inherit = "sale.order.line"

    #Color should still be migrated from quotation/order > invoice!
    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
        ret = super(sale_order_line_your_extension, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=False, context=context)
        hoogte = 0
        breedte = 0
        aantal = 0
        quantity = 0
        links = False
        rechts = False
        boven = False
        onder = False
        kleur = ''
        barcode = ''
        boringen = ''
        opmerkingen = ''
        kleur = ''
        if line.hoogte:
            hoogte = line.hoogte
        if line.breedte:
            breedte = line.breedte
        if line.aantal:
            aantal = line.aantal
        if line.product_uom_qty:
            quantity = line.product_uom_qty
        if line.links:
            links = line.links
        if line.rechts:
            rechts = line.rechts
        if line.boven:
            boven = line.boven
        if line.onder:
            onder = line.onder
        if line.barcode:
            barcode = line.barcode
        if line.boringen:
            boringen = line.boringen
        if line.opmerkingen:
            opmerkingen = line.opmerkingen
        if self.kleurenpicker:
            kleur = self.kleurenpicker
        ret['hoogte'] = hoogte
        ret['breedte'] = breedte
        ret['aantal'] = aantal
        ret['quantity'] = quantity
        ret['links'] = links
        ret['rechts'] = rechts
        ret['boven'] = boven
        ret['onder'] = onder
        ret['barcode'] = barcode
        ret['boringen'] = boringen
        ret['opmerkingen'] = opmerkingen
        ret['kleurenpicker'] = kleur
        return ret


class sale_order_line_colorpicker(models.Model):
    _name = 'sale.order.colorpicker'
    _description = 'Voor dropdown van kleuren bij offerte/order/factuur'
    name = fields.Char('Name', required=True)
    website_publish = fields.Boolean('Published')


#Add many2one (for color dropdown) to sale.order
class aa_houbolak_colorpicker_in_salemodel(models.Model):
    _inherit = 'sale.order'
    kleurenpicker = fields.Many2one('sale.order.colorpicker', 'Kleur')


#Add many2one (for color dropdown) to account.invoice
class aa_houbolak_colorpicker_in_accountmodel(models.Model):
    _inherit = 'account.invoice'
    kleurenpicker = fields.Many2one('sale.order.colorpicker', 'Kleur')
