$(document).ready(function() {
    $('.question[tooltip]').each(function() {
        $(this).qtip({    
            content: $(this).attr('tooltip')
        }); 
    });

    $('select[multiple="multiple"]').multiselect({
       selectedText: '# of # selected'
    });
    
    if (METHOD == 'create') {
        $('select[multiple="multiple"]').multiselect('checkAll');
    }
        
    $('.cancel_modal').click( function() {
        $('#modal_div').dialog('close');
        $("#modal_div").html("<img class='loading_img' src='/static/images/loading.gif'/>"); 
    });

    $('#savedsearch_form').submit(function() { 
        $('#submit_search input').attr('class', 'saving_button').attr('value', 'Saving...');
        $.ajax({
            type: 'POST',
            url: $('#savedsearch_form').attr('action'),
            data: $(this).serializeArray(),
            dataType: 'json',
            success: function() {
                $.ajax({
                    type: 'GET',
                    dataType: 'json',
                    url: '/' + SUBDOMAIN + '/api/savedsearch/retrieve', 
                    async: false,
                    success: function(saved_searches) {
                        var selected = parseInt($('#saved_search').val());
                        var html = '';
                        var json = {};
                        console.log(selected);
                        for (var i in saved_searches) {
                            if (saved_searches[i]['id'] === selected) {
                                html += '<option value="' + saved_searches[i]['id'] + '" SELECTED>' + saved_searches[i]['name'] + '</option>';
                            } else {
                                html += '<option value="' + saved_searches[i]['id'] + '">' + saved_searches[i]['name'] + '</option>';
                            }

                            json[saved_searches[i]['id']] = saved_searches[i]['name'];
                             
                        }
                        $('#saved_search').html(html).selectmenu('destroy').selectmenu(json);
                        $("#modal_div").html("<img class='loading_img' src='/static/images/loading.gif'/>"); 
                        $('#modal_div').dialog('close');
                    }
                });

            },
            error: function(xhr) {
                $('#submit_search input').attr('class', 'primary_button').attr('value', 'Save');
                var errors = JSON.parse(xhr.responseText);
                var html = '';
                for (var field in errors) {
                    for (var i in errors[field]) {
                        html += $('#'+field).parent().prev().children().html() + ': ' + errors[field][i] + '<br />';
                    }
                }
                $('.errors').html(html)
            }
        });


        return false;
    });
});
