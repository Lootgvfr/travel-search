/**
 * Created by D-N on 17/02/2017.
 */

var from_input = $('#from');
var from_options = $('#from-options');
var to_input = $('#to');
var to_options = $('#to-options');

var last_input_from = new Date().getTime();
var last_input_to = new Date().getTime();

var sending_from = false;
var sending_to = false;
var from_current_options = '';
var to_current_options = '';

from_input.on('input', function(event){
    last_input_from = new Date().getTime();
});

to_input.on('input', function(event){
    last_input_to = new Date().getTime();
});

setInterval(function () {
    var time_passed = new Date().getTime() - last_input_from;
    if (from_input.val() && time_passed >= 300 && !sending_from && from_input.val() !== from_current_options){
        sending_from = true;
        $.ajax({
            url: $('#searchForm').attr('data-options-url').replace('srch', from_input.val()),
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data.type == 'success') {
                    from_options.html('');
                    for (var i = 0; i < data.options.length; i++){
                        from_options.append("<option value=\"" + data.options[i].city + ', ' + data.options[i].country + "\"/>");
                    }
                    from_current_options = from_input.val();
                }
            }
        }).always(function(){
            sending_from = false;
            from_current_options = from_input.val();
        });
    }
}, 100);

setInterval(function () {
    var time_passed = new Date().getTime() - last_input_to;
    if (to_input.val() && time_passed >= 300 && !sending_to && to_input.val() !== to_current_options){
        sending_to = true;
        $.ajax({
            url: $('#searchForm').attr('data-options-url').replace('srch', to_input.val()),
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data.type == 'success') {
                    to_options.html('');
                    for (var i = 0; i < data.options.length; i++){
                        to_options.append("<option value=\"" + data.options[i].city + ', ' + data.options[i].country + "\"/>");
                    }
                    to_current_options = to_input.val();
                }
            }
        }).always(function(){
            sending_to = false;
            to_current_options = to_input.val();
        });
    }
}, 100);


