odoo.define('website_short_cart.website_process_cart', function (require) {
    'use strict';
    var rpc = require('web.rpc');
    require('web.dom_ready')

    //     // http://localhost:8070/shop/multicart/move?
    //     // csrf_token=44a790ab2be2c6f6820709864bb0f8c83ad604fdo1726600032
    //     // &cart_id=1
    //     // &slected_cart=
    //     // &marge_cart=True
   
    $(document).ready(function() {
        $('.dooit-click-cart-short').click( async function(){
            let cart_id = $(this).attr('data-cart_id');
            let slected_cart = 0
            // URL
            let URL = `${window.location.origin}/shop/multicart/move?cart_id=${cart_id}&checkout_cart=${true}&replace_cart=${true}`
            // send data

            await fetch(URL).then(
                (res)=>{
                    console.log(res)
                    if(res.status == 200 && res.ok){
                        window.location.href = res.url
                    }
                }
            ).catch((e)=>console.error(e))
            // console.log(URL)

        })

    });

});
