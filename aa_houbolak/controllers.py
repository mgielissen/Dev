# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale
import logging
_logger = logging.getLogger(__name__)
from openerp.tools.translate import _


class website_yenth(website_sale):

    @http.route(['/shop'], type='http', auth="user", website=True)
    def shop(self, page=0, category=None, search='', **post):
        if not request.session.get('aa_houbolak_afwerking'):
            return request.redirect("/shop/afwerking")
        return super(website_yenth, self).shop(page=page, category=category, search=search, **post)

    @http.route(['/shop/extra'], type='http', auth="user", website=True)
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

    @http.route(['/shop/checkout'], type='http', auth="user", website=True)
    def checkout(self, **post):
        if not request.session.get('extra_info_done'):
            return request.redirect("/shop/extra")
        return super(website_yenth, self).checkout(**post)

    @http.route(['/shop/afwerking'], type='http', auth="user", website=True)
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

    @http.route(['/shop/confirm_order'], type='http', auth="user", website=True)
    def confirm_order(self, **post):
        response = super(website_yenth, self).confirm_order(**post)
        if response.location == "/shop/payment":
            response = request.redirect("/shop/final")
        return response

    @http.route(['/shop/payment'], type='http', auth="user", website=True)
    def payment(self, **post):
        # should be never in this controller
        return request.redirect("/shop/final")

    @http.route(['/shop/final'], type='http', auth="user", website=True)
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

    @http.route(['/shop/cart/update'], type='http', auth="user", methods=['POST'], website=True)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        MIN_QTY = 1
        resp = request.website.sale_get_order(force_create=1)._cart_update(product_id=int(product_id), add_qty=float(add_qty), set_qty=float(set_qty), line_id=False)
        order = request.website.sale_get_order()
        values = {}
        for line in order.order_line:
            if line.id == resp.get('line_id'):
                if not order.afwerkingpicker:
                    values = {'afwerkingpicker': request.session['aa_houbolak_afwerking']}
		if line.aantal > 0:
                    resultaatBerekening = int(kw.get('hoogteWebshop')) * int(kw.get('breedteWebshop')) / 1000000 * line.aantal
		else:
		    resultaatBerekening = int(kw.get('hoogteWebshop')) * int(kw.get('breedteWebshop')) / 1000000 * float(add_qty)
		_logger.critical("line.aantal: " + str(line.aantal) + "add_qty: " + str(add_qty) + " resultaatBerekening: " + str(resultaatBerekening))
                values['order_line'] = [(1, line.id, {
                    'hoogte': int(kw.get('hoogteWebshop')),
                    'breedte': int(kw.get('breedteWebshop')),
                    'aantal': float(add_qty),
                    'product_uom_qty': max(resultaatBerekening, MIN_QTY),
                    'links': bool(kw.get('linksWebshop')),
                    'rechts': bool(kw.get('rechtsWebshop')),
                    'boven': bool(kw.get('bovenWebshop')),
                    'onder': bool(kw.get('onderWebshop')),
                    'boringen': kw.get('boringenWebshop', ''),
                    'opmerkingen': kw.get('opmerkingenWebshop', ''),
                })]
                order.write(values)
                break
        return request.redirect("/shop/cart")

    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def payment_get_status(self, sale_order_id, **post):
        cr, uid, context = request.cr, request.uid, request.context

        order = request.registry['sale.order'].browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        assert order.id == request.session.get('sale_last_order_id')

        if not order:
            return {
                'state': 'error',
                'message': '<p>%s</p>' % _('Uw order is succesvol verwerkt.'),
            }

        tx_ids = request.registry['payment.transaction'].search(
            cr, SUPERUSER_ID, [
                '|', ('sale_order_id', '=', order.id), ('reference', '=', order.name)
            ], context=context)

        if not tx_ids:
            if order.amount_total:
                return {
                    'state': 'error',
                    'message': '<p>%s</p>' % _('Uw order is succesvol verwerkt.'),
                }
            else:
                state = 'done'
                message = ""
                validation = None
        else:
            tx = request.registry['payment.transaction'].browse(cr, SUPERUSER_ID, tx_ids[0], context=context)
            state = tx.state
            if state == 'done':
                message = '<p>%s</p>' % _('Your payment has been received.')
            elif state == 'cancel':
                message = '<p>%s</p>' % _('The payment seems to have been canceled.')
            elif state == 'pending' and tx.acquirer_id.validation == 'manual':
                message = '<p>%s</p>' % _('Your transaction is waiting confirmation.')
                if tx.acquirer_id.post_msg:
                    message += tx.acquirer_id.post_msg
            else:
                message = '<p>%s</p>' % _('Your transaction is waiting confirmation.')
            validation = tx.acquirer_id.validation

        return {
            'state': state,
            'message': message,
            'validation': validation
        }

    #Override default cart
    """@http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True, **kw):
        order = request.website.sale_get_order(force_create=1)
        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        if not display:
            return None
        value['cart_quantity'] = order.cart_quantity
        value['website_sale.total'] = request.website._render("website_sale.total", {
                'website_sale_order': request.website.sale_get_order()
            })
	for line in order.order_line:
            if line.id == value.get('line_id'):
		resultaatBerekening = (line.hoogte * line.breedte) / 1000000 * value.get('quantity')
		value['product_uom_qty'] = resultaatBerekening
        return value
    """
