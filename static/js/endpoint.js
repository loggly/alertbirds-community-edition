$(document).ready(function() {
    $('.cancel_modal').click( function() {
        $('.close').click();
        $("#modal_div").html("<img class='loading_img' src='/static/images/loading.gif'/>"); 
    });
    $('#endpoint_form').submit(function() { 
        $('#submit_endpoint input').attr('class', 'saving_button').attr('value', 'Saving...');
        $.ajax({
            type: 'POST',
            url: $('#endpoint_form').attr('action'),
            data: $(this).serializeArray(),
            success: function() {
                $.get('/' + SUBDOMAIN + '/api/endpoint/retrieve', function(endpoints) {
                    var selected = $('#endpoint').val();
                    var html = '';
                    var json = {};
                    for (var i in endpoints) {
                        if (endpoints[i]['id'] === selected) {
                            html += '<option value="' + endpoints[i]['id'] + '" SELECTED>' + endpoints[i]['description'] + '</option>';
                        } else {
                            html += '<option value="' + endpoints[i]['id'] + '">' + endpoints[i]['description'] + '</option>';
                        }

                        json[endpoints[i]['id']] = endpoints[i]['description'];

                    }

                    $('#endpoint').html(html).selectmenu('destroy').selectmenu(json);

                }, 'json');

                $("#modal_div").html("<img class='loading_img' src='/static/images/loading.gif'/>"); 
                $('#modal_div').dialog('close');
            },
            error: function(xhr) {
                $('#submit_endpoint input').attr('class', 'primary_button').attr('value', 'Save');
                var errors = JSON.parse(xhr.responseText);
                var html = '';
                for (var field in errors) {
                    for (var i in errors[field]) {
                        html += $('#'+field).parent().prev().children().html() + ': ' + errors[field][i] + '<br />';
                    }
                }
                $('.errors').html(html);
            }
        });

        // don't reload window on either success or failure
        return false;
    });

    $('#provider').selectmenu();

    $('.question[tooltip]').each(function() {
        $(this).qtip({    
            content: $(this).attr('tooltip')
        }); 
    });
});
