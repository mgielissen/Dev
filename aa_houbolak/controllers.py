# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
import logging
_logger = logging.getLogger(__name__)


class website_yenth(website_sale):

    @http.route(['/shop'], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', **post):
        if not request.session.get('aa_houbolak_afwerking'):
            return request.redirect("/shop/afwerking")
        return super(website_yenth, self).shop(page=page, category=category, search=search, **post)

    @http.route(['/shop/extra'], type='http', auth="public", website=True)
    def extra(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if post and post.get('color'):
            order.write({'kleurenpicker': int(post.get('color'))})
            request.session['extra_info_done'] = True
            return request.redirect("/shop/checkout")
        color_ids = pool['sale.order.colorpicker'].search(cr, uid, [('website_publish', '=', True)], context=context)
        colors = pool['sale.order.colorpicker'].browse(cr, uid, color_ids, context=context)
        values = dict(order=order, colors=colors)
        return request.website.render("aa_houbolak.extra", values)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True)
    def checkout(self, **post):
        if not request.session.get('extra_info_done'):
            return request.redirect("/shop/extra")
        return super(website_yenth, self).checkout(**post)

    @http.route(['/shop/afwerking'], type='http', auth="public", website=True)
    def afwerking(self, **post):
        cr, context, pool = request.cr, request.context, request.registry
        if post and post.get('afwerking'):
            # save in session, avoid to create empty sale order
            request.session['aa_houbolak_afwerking'] = int(post.get('afwerking'))
            return request.redirect("/shop")

        finishing_ids = pool['sale.order.finishing'].search(cr, SUPERUSER_ID, [('website_publish', '=', True)], context=context)
        afwerkingen = pool['sale.order.finishing'].browse(cr, SUPERUSER_ID, finishing_ids, context=context)
        values = dict(afwerkingen=afwerkingen)
        return request.website.render("aa_houbolak.categoryselection", values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        response = super(website_yenth, self).confirm_order(**post)
        if response.location == "/shop/payment":
            response = request.redirect("/shop/final")
        return response

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        # should be never in this controller
        return request.redirect("/shop/final")

    @http.route(['/shop/final'], type='http', auth="public", website=True)
    def final(self, **post):
        if not request.session.get('extra_info_done'):
            return request.redirect("/shop/extra")

        order = request.website.sale_get_order()
        if order and order.state == 'draft':
            # change state here to know that user was in final step and dont stop during extra step
            order.signal_workflow('order_confirm')
        # reset current order from the backend and start new order
        request.website.sale_reset()
        return request.website.render("website_sale.confirmation", dict(order=order))

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        res = super(website_yenth, self).cart_update(product_id, add_qty=1, set_qty=1, **kw)
        order = request.website.sale_get_order()
        values = {}
        for line in order.order_line:
            if line.product_id.id == int(product_id):
                if not order.afwerkingpicker:
                    values = {'afwerkingpicker': request.session['aa_houbolak_afwerking']}
                resultaatBerekening = int(kw.get('hoogteWebshop')) * int(kw.get('breedteWebshop')) / 1000000 * 1
                values['order_line'] = [(1, line.id, {
                    'hoogte': int(kw.get('hoogteWebshop')),
                    'breedte': int(kw.get('breedteWebshop')),
                    'aantal': 1,
                    'product_uom_qty': resultaatBerekening,
                    'links': bool(kw.get('linksWebshop')),
                    'rechts': bool(kw.get('rechtsWebshop')),
                    'boven': bool(kw.get('bovenWebshop')),
                    'onder': bool(kw.get('onderWebshop')),
                    'boringen': kw.get('boringenWebshop', ''),
                    'opmerkingen': kw.get('opmerkingenWebshop', ''),
                })]
                order.write(values)
                break
        return res
