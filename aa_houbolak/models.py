# -*- coding: utf-8 -*-

from openerp import models, fields
from openerp.osv import osv
from openerp.addons.web.http import request


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
    barcode = fields.Char('Bar')
    boringen = fields.Char('Bor')
    opmerkingen = fields.Char('Opm.')

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
        ret = super(sale_order_line_your_extension, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
        ret['hoogte'] = line.hoogte or 0
        ret['breedte'] = line.breedte or 0
        ret['aantal'] = line.aantal or 0
        ret['quantity'] = line.product_uom_qty or 0
        ret['links'] = line.links or False
        ret['rechts'] = line.rechts or False
        ret['boven'] = line.boven or False
        ret['onder'] = line.onder or False
        ret['barcode'] = line.barcode or ''
        ret['boringen'] = line.boringen or ''
        ret['opmerkingen'] = line.opmerkingen or ''
        return ret


class sale_order_line_colorpicker(models.Model):
    _name = 'sale.order.colorpicker'
    _description = 'Voor dropdown van kleuren bij offerte/order/factuur'
    name = fields.Char('Name', required=True)
    website_publish = fields.Boolean('Published', default=True)


class sale_order_line_finishingpicker(models.Model):
    _name = 'sale.order.finishing'
    _description = 'Voor dropdown van afwerkingen bij offerte/order/factuur'
    name = fields.Char('Name', required=True)
    website_publish = fields.Boolean('Published', default=True)


#Add many2one (for color dropdown) to sale.order
class aa_houbolak_colorpicker_in_salemodel(models.Model):
    _inherit = 'sale.order'
    kleurenpicker = fields.Many2one('sale.order.colorpicker', 'Kleur')
    afwerkingpicker = fields.Many2one('sale.order.finishing', 'Afwerking')

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        res = super(aa_houbolak_colorpicker_in_salemodel, self)._prepare_invoice(cr, uid, order, lines, context=context)
        res['kleurenpicker'] = order.kleurenpicker.id
        res['afwerkingpicker'] = order.afwerkingpicker.id
        return res


#Add many2one (for color dropdown) to account.invoice
class aa_houbolak_colorpicker_in_accountmodel(models.Model):
    _inherit = 'account.invoice'
    kleurenpicker = fields.Many2one('sale.order.colorpicker', 'Kleur')
    afwerkingpicker = fields.Many2one('sale.order.finishing', 'Afwerking')


#Add many2many (for finishing on product) to product.template
class aa_houbolak_finishing_in_product_model(models.Model):
    _inherit = 'product.template'
    afwerkingpickerProduct = fields.Many2many('sale.order.finishing', 'product_finishing_rel', 'src_id_finishing', 'dest_id_finishing', string='Afwerking(en):')


class website(models.Model):
    _inherit = 'website'

    def sale_reset(self, cr, uid, ids, context=None):
        super(website, self).sale_reset(cr, uid, ids, context=context)
        request.session.update(dict(extra_info_done=False, aa_houbolak_afwerking=False))

    def sale_product_domain(self, cr, uid, ids, context=None):
        assert request.session.aa_houbolak_afwerking, "No afwerking define"
        return ['&'] + super(website, self).sale_product_domain(cr, uid, ids, context=context) + [('afwerkingpickerProduct.id', 'in', [request.session.aa_houbolak_afwerking])]
