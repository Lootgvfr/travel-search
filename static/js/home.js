/**
 * Created by D-N on 17/02/2017.
 */

var form = $('#searchForm');

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
var current_from = '';
var current_to = '';

from_input.on('input', function(event){
    last_input_from = new Date().getTime();
    from_options.children().each(function () {
        if ($(this).attr('value') === from_input.val()){
            from_current_options = from_input.val();
        }
    });
});

to_input.on('input', function(event){
    last_input_to = new Date().getTime();
    to_options.children().each(function () {
        if ($(this).attr('value') === to_input.val()){
            to_current_options = to_input.val();
        }
    });
});

setInterval(function () {
    var time_passed = new Date().getTime() - last_input_from;
    if (from_input.val() && time_passed >= 200 && !sending_from && from_input.val() !== from_current_options){
        sending_from = true;
        current_from = from_input.val();
        $.ajax({
            url: form.attr('data-options-url').replace('srch', from_input.val()),
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data.type == 'success') {
                    from_options.html('');
                    for (var i = 0; i < data.options.length; i++){
                        from_options.append("<option value=\"" + data.options[i].city + ', ' + data.options[i].country + "\"/>");
                    }
                    from_current_options = current_from;
                }
            }
        }).always(function(){
            sending_from = false;
            from_current_options = current_from;
        });
    }
}, 100);

setInterval(function () {
    var time_passed = new Date().getTime() - last_input_to;
    if (to_input.val() && time_passed >= 200 && !sending_to && to_input.val() !== to_current_options){
        sending_to = true;
        current_to = to_input.val();
        $.ajax({
            url: form.attr('data-options-url').replace('srch', to_input.val()),
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data.type == 'success') {
                    to_options.html('');
                    for (var i = 0; i < data.options.length; i++){
                        to_options.append("<option value=\"" + data.options[i].city + ', ' + data.options[i].country + "\"/>");
                    }
                    to_current_options = current_to;
                }
            }
        }).always(function(){
            sending_to = false;
            to_current_options = current_to;
        });
    }
}, 100);

form.on('submit', function(event){
    event.preventDefault();
    var dt = form.serialize();
    clear_errors();
    $.ajax({
        url: form.attr('action'),
        type: 'POST',
        dataType: 'json',
        data: dt,
        success: function(data){
            if (data.type == 'error'){
                process_errors(data.errors);
            }
            else if (data.type == 'redirect'){
                window.location.href = data.redirect_url;
            }
        }
    });
});

function clear_errors(){
    var to_clear = ['from', 'to', 'transport_types', 'price_lower', 'price_upper'];
    for(var i = 0; i < to_clear.length; i++){
        $('#' + to_clear[i])
            .css('border-color', '#ccc')
            .attr('title', '')
            .attr('data-original-title', '')
            .attr('original-title', '')
            .tooltip('hide');
    }
}

function process_errors(errors) {
    for(var i = 0; i < errors.length; i++){
        $('#' + errors[i].path)
            .css('border-color', '#cc0000')
            .attr('title', errors[i].text)
            .attr('original-title', errors[i].text)
            .attr('data-original-title', errors[i].text)
            .tooltip('show');
    }
}
