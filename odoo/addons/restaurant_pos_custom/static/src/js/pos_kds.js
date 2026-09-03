// pos_kds.js - simple polling KDS client
odoo.define('restaurant_pos_custom.pos_kds', function(require){
    'use strict';
    var ajax = require('web.ajax');

    function fetchAndRender(){
        ajax.jsonRpc('/restaurant/kds/orders','call',{}).then(function(data){
            // simple console output; real implementation would render DOM
            console.log('KDS Orders:', data);
            // TODO: render in a proper KDS template
        }).catch(function(err){
            console.error('KDS error', err);
        });
    }

    // Poll every 4 seconds
    setInterval(fetchAndRender, 4000);

    // initial fetch
    fetchAndRender();
});
