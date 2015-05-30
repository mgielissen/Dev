# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_yenth(website_sale):
    @http.route(['/shop/extra_add_color'], type='http', auth="public", website=True)
    def add_color(self, **post):
        if post.get('color'):
            color = post.get('color')
            cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
            pool['sale.order.colorpicker'].create(cr, uid, {'name': color, 'website_publish': True}, context=context)
            return request.make_response("<h1> Color : %s added ...</h1>" % color)
        return request.make_response("<h1> Color param missing...</h1>")

    @http.route(['/shop/extra'], type='http', auth="public", website=True)
    def extra(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        order = request.website.sale_get_order()

        if post:
            if post.get('color'):
                order.write({'color': int(post.get('color'))})
                for line in order.order_line:
                    hoogteWebshop = int(post.get('%s-%s' % (line.id, 'hoogteWebshop')))
                    breedteWebshop = int(post.get('%s-%s' % (line.id, 'breedteWebshop')))
                    resultaatBerekening = hoogteWebshop * breedteWebshop / 1000000 * 1
                    print("Result: " + str(resultaatBerekening))
                    line.write({
                        'hoogte': int(post.get('%s-%s' % (line.id, 'hoogteWebshop'))),
                        'breedte': int(post.get('%s-%s' % (line.id, 'breedteWebshop'))),
                        'aantal': 1,
                        'product_uom_qty': resultaatBerekening,
                        'links': bool(post.get('%s-%s' % (line.id, 'linksWebshop'))),
                        'rechts': bool(post.get('%s-%s' % (line.id, 'rechtsWebshop'))),
                        'boven': bool(post.get('%s-%s' % (line.id, 'bovenWebshop'))),
                        'onder': bool(post.get('%s-%s' % (line.id, 'onderWebshop'))),
                        'boringen': post.get('%s-%s' % (line.id, 'boringenWebshop')),
                        'opmerkingen': post.get('%s-%s' % (line.id, 'opmerkingenWebshop')),

                    })
            request.session['extra_info_done'] = True
            return request.redirect("/shop/extra")
        color_ids = pool['sale.order.colorpicker'].search(cr, uid, [('website_publish', '=', True)], context=context)
        colors = pool['sale.order.colorpicker'].browse(cr, uid, color_ids, context=context)
        values = dict(order=order, colors=colors)
        return request.website.render("aa_houbolak.extra", values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        if not request.session.get('extra_info_done'):
            return request.redirect("/shop/extra")
        return super(website_yenth, self).confirm_order(**post)
