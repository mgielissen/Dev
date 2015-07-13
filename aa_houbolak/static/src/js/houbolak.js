$(document).ready(function () {
    $('.oe_website_sale').each(function () {
        //USING JQUERY VALIDATE
        $('#opmerkingenWebshop').closest('form').validate();

        //OR CUSTOMIZE HERE YOUR OWN CHECK YOUR SELF IN JS
        $('#opmerkingenWebshop').closest('form').on('submit', function(o) {
            $('form-group').removeClass('has-error');

            var required = ['#opmerkingenWebshop', '#breedteWebshop', '#hoogteWebshop', '#boringenWebshop'];
            var error = false;

            $(required).each(function(i, x) {
                if ($(x).val() == "") {
                    $(x).closest('.form-group').addClass('has-error');
                    error = true;
                }
            })

            return !error;
        })

        $('div.deleteMe i').on('click', function(o) {
            openerp.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': $(this).closest('tr').find('input').data('line-id'),
                'product_id': $(this).closest('tr').find('input').data('product-id'),
                'set_qty': 0})
            .then(function (data) {
                // refresh since line is removed
                location.reload();
            });
        });
    });
})