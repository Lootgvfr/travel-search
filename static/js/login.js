/**
 * Created by D-N on 15/02/2017.
 */

var form = $('#loginForm');
var error = $('#error-text');

form.on('submit', function(event){
    event.preventDefault();
    error.html('');
    $.ajax({
        url: form.attr('data-link'),
        type: 'POST',
        dataType: 'json',
        data: form.serialize(),
        success: function(data){
            if (data.type == 'error'){
                error.html(data.message);
            }
            else if (data.type == 'redirect'){
                window.location.href = data.redirect_url;
            }
        }
    });
});