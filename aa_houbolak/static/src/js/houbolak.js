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
    });
})