$(document).ready(function() {
    $('#test_button').click(function() {
        $('#test_button a').html('Testing...');
        var url = encodeURI('/' + SUBDOMAIN + '/api/savedsearch/run/' + $('#saved_search').val() + '?threshold_time_secs=' + $('#threshold_time_secs').val());
        $.get(url, function(result) {
            $('#test_button a').html('Test');

            $.Growl.show('Testing: <br/>' + result['numFound'] + ' results found in the last ' + ($('#threshold_time_secs').val() / 60) + ' minutes.', {
                'icon': false,
                'title': '',
                'cls': '', 
                'speed': 500,
                'timeout': 5000

            });
        }, 'json');
    });

    $('#delete_saved_search_button').click(function() {
        if (confirm('Are you sure?')) {
            $('#delete_saved_search_button a').html('Deleting...');
            var url = encodeURI('/' + SUBDOMAIN + '/api/savedsearch/delete/' + $('#saved_search').val());
            $.get(url, function(result) {
                $.ajax({
                    type: 'GET',
                    dataType: 'json',
                    url: '/' + SUBDOMAIN + '/api/savedsearch/retrieve', 
                    success: function(saved_searches) {
                        var html = '';
                        var json = {};
                        for (var i in saved_searches) {
                            html += '<option value="' + saved_searches[i]['id'] + '">' + saved_searches[i]['name'] + '</option>';
                            json[saved_searches[i]['id']] = saved_searches[i]['name'];
                        }
                        $('#saved_search').html(html).selectmenu('destroy').selectmenu(json);
                        $('#delete_saved_search_button a').html('Delete');
                    }
                });
            });
        }
    });

    $('#alert_form').submit(function() {
        if (!$('#endpoint').val()) {
            if (!confirm('You are about to create an alert that you\'ll only see if you\'re on Alert Birds.' +
                'I\'d like to respectfully suggest that you configure an endpoint so your things don\'t catch on fire, etc.  Are you sure?')) {
                return false;
            }
                            
        }
    });

    $('#modal_div').dialog({
                        modal: true,
                        draggable: false,
                        resizable: false,   
                        autoOpen: false,
                        open: function() { 
                            //$('body').css('overflow', 'hidden');
                        },
                        beforeClose: function() { 
                            $("#modal_div").html("<img class='loading_img' src='/static/images/loading.gif'/>"); 
                            $('.question[tooltip]').qtip('hide');     
                            $('body').css('overflow', 'auto');
                        }
    });

    $('.modal_button').click(function() {
        if ($(this).attr('method') == 'endpoint_edit') {
            if (!$('#endpoint').val()) { 
                alert('Please first select an endpoint.'); 
                return false; 
            }

            $('#modal_div').load($(this).attr('popup') + $('#endpoint').val());
        } else if ($(this).attr('method') == 'savedsearch_edit') {
            $('#modal_div').load($(this).attr('popup') + $('#saved_search').val());
        } else {
            $('#modal_div').load($(this).attr('popup'));
        }

        $('#modal_div').dialog({position: ['center', 200], width: $(this).attr('modal_width')});
        $('#modal_div').dialog('open');
    });
    $('.close, .ui-widget-overlay').live('click', function() {
        $('#modal_div').dialog('close');
    });
});
