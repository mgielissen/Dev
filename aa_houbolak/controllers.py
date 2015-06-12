# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_yenth(website_sale):

    @http.route(['/shop/final'], type='http', auth="public", website=True)
    def final(self, **post):
        if not request.session.get('extra_info_done'):
            return request.redirect("/shop/extra")

        order = request.website.sale_get_order()
        if order and order.state == 'draft':
            # change state here to know that user was in final step and dont stop during extra step
            order.write(dict(state='progress'))
        # reset current order from the backend,
        # will start new order
        request.website.sale_reset()
        return request.website.render("aa_houbolak.final_step", dict(order=order))

    @http.route(['/shop/extra'], type='http', auth="public", website=True)
    def extra(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        def getField(post, sol_id, field, funct):
            assert funct in [int, bool, str]
            try:
                return funct(post.get('%s-%s' % (sol_id, field)))
            except:
                if funct == str:
                    return ''
                return funct(0)

        if post:
            if post.get('color'):
                order.write({'kleurenpicker': int(post.get('color'))})
                for line in order.order_line:
                    hoogteWebshop = getField(post, line.id, 'hoogteWebshop', int)
                    breedteWebshop = getField(post, line.id, 'breedteWebshop', int)
                    resultaatBerekening = hoogteWebshop * breedteWebshop / 1000000 * 1
                    print("Result: " + str(resultaatBerekening))
                    line.write({
                        'hoogte': hoogteWebshop,
                        'breedte': breedteWebshop,
                        'aantal': 1,
                        'product_uom_qty': resultaatBerekening,
                        'links': getField(post, line.id, 'linksWebshop', bool),
                        'rechts': getField(post, line.id, 'rechtsWebshop', bool),
                        'boven': getField(post, line.id, 'bovenWebshop', bool),
                        'onder': getField(post, line.id, 'onderWebshop', bool),
                        'boringen': getField(post, line.id, 'boringenWebshop', str),
                        'opmerkingen': getField(post, line.id, 'opmerkingenWebshop', str),

                    })
            request.session['extra_info_done'] = True
            return request.redirect("/shop/final")
        color_ids = pool['sale.order.colorpicker'].search(cr, uid, [('website_publish', '=', True)], context=context)
        colors = pool['sale.order.colorpicker'].browse(cr, uid, color_ids, context=context)
        values = dict(order=order, colors=colors)
        return request.website.render("aa_houbolak.extra", values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        response = super(website_yenth, self).confirm_order(**post)
        if response.location == "/shop/payment":
            response = request.redirect("/shop/extra")
        return response

    @http.route(['/shop/payment'], type='http', auth="public", website=True)
    def payment(self, **post):
        # should be never in this controller
        return request.redirect("/shop/final")
