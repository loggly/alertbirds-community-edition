var SUBDOMAIN = document.URL.split('/')[3].split('/')[0]; //pulls subdomain out of the URL
var alert_channel = hex_md5('alertbirds' + SUBDOMAIN);    //md5's alertbirds'subdomain' for unique channel binding

$(document).ready(function() {

var isDisco = false;
    $(document).keydown( function(event) {
        if ( event.shiftKey && event.altKey ) {
            $('.disco').toggle();
            isDisco = !isDisco;
        }
        
    });
    $('div, a, img, span, tr, th, td').live('click', function() {
        if ( !isDisco ) {

            return true;
        }

            $(this).toggleClass('catchadream');
            return false;
    });
    soundManager.url = '/static/js/swf/';
    soundManager.debugMode = false;          //deactivate the soundmanager2 debug console
    soundManager.flashLoadTimeout = 0;       //(patiently) waits forever for flash to load

    soundManager.onready( function() {       //creates all sounds for previewing
        soundManager.createSound('crow','/static/sounds/crow.mp3');
        soundManager.createSound('owls','/static/sounds/owls.mp3');
        soundManager.createSound('seagull','/static/sounds/seagull.mp3');
        soundManager.createSound('wren','/static/sounds/wren.mp3');
        soundManager.createSound('squawk','/static/sounds/squawk.mp3');
    });
    
    $('.mute_False').live('click', function() {  //changes unmuted icon to muted icon, mutes sound, makes api call to store muted status
        $(this).removeClass('mute_False');
        $(this).addClass('mute_True');
        soundManager.mute($(this).attr('sound'));
        $.get(SUBDOMAIN + '/api/alert/mute/' + $(this).attr('sound'));
        console.log($(this).attr('sound'));
            
    });
    $('.mute_True').live('click', function() {  //changes muted icon to unmuted icon, unmutes sound, makes api call to store unmuted status
        $(this).removeClass('mute_True');
        $(this).addClass('mute_False');
        soundManager.unmute($(this).attr('sound'));
        $.get(SUBDOMAIN + '/api/alert/unmute/' + $(this).attr('sound'));
        console.log($(this).attr('sound'));
    });

    $('.alert_enable div').live('click', function() {  //makes api call to enable alert and store enable status
        $.get(SUBDOMAIN + '/api/alert/enable/' + $(this).parent().parent().attr('id'));
        $(this).parent().removeClass('alert_enable');
        $(this).parent().addClass('alert_disable');
    });

    $('.alert_disable div').live('click', function() { //makes api call to enable alert and store enable status
        $.get(SUBDOMAIN + '/api/alert/disable/' + $(this).parent().parent().attr('id'));
        $(this).parent().removeClass('alert_disable');
        $(this).parent().addClass('alert_enable');
    });

    $('.loggly_view a').live('click', function() {  //links saved search to loggly dashboard
        var alert_id = $(this).parent().parent().attr('id')
        $.get(SUBDOMAIN + '/api/alert/getssurl/' + alert_id, function(url) {
            location = url
        });
    });

    var pusher = new Pusher('5f241ac02d8f7a4a664b');    //pusher key 
    var channel = pusher.subscribe(alert_channel);      //pusher channel set to hash of alertbirds plus user's subdomain

    channel.bind('chirp', function(data) {  //listens for 'chirp' events on my channel 'alert'
        soundManager.createSound(data.key, '/static/sounds/' + data.sound + '.mp3');  //creates sound using unique alert id on demand
        stateChange = new Date( data.last_state_change*1000 );

        if (data.state == 'C') {    //changes state of alert to critical or neutral as appropriate (changes color of the birds from green to red)
            $('#state_' + data.key).removeClass('alert_state_N');  
            $('#state_' + data.key).addClass('alert_state_C');  

            soundManager.play(data.key);        //plays sound first
            if (data.muted) {                   //mutes sound for specific alert automatically if that alerts mute status is true
                soundManager.mute(data.key);
            } 

            $.Growl.show( '<div class="timestamp">In this state since: <br/>' + stateChange.toLocaleDateString() + ' ' + stateChange.toLocaleTimeString() + '</div><br/>' + 'Description: ' + data.description, {
                'icon': false,
                'title': data.name,
                'cls': '',
                'speed': 500,
                'timeout': 15000

            });
        } else if (data.state == 'N') {

            $('#state_' + data.key).removeClass('alert_state_C');  
            $('#state_' + data.key).addClass('alert_state_N');  

        }



    }); 
    // websocket, flash install and flash block handling
    var flashLink = 'http://get.adobe.com/flashplayer/'; //current flashplayer link
    //detects whether device viewing the page is an iOS device or not
    var Apple = {}; 
    Apple.UA = navigator.userAgent;
    Apple.Device = false;
    Apple.Types = ["iPhone", "iPod", "iPad"];
    for (var d = 0; d < Apple.Types.length; d++) {
        var t = Apple.Types[d];
        Apple[t] = !!Apple.UA.match(new RegExp(t, "i"));
        Apple.Device = Apple.Device || Apple[t];
    } 
    if(!Apple.Device) { //none of the flash tests apply to iOS devices

        if(!window.WebSocket) {  //if browser doesn't support web sockets

            if(!FlashDetect.installed) {    //if flash is not installed, informs user that flash is required for websocket functionality in this browser
                $('.alert_bubble').css('visibility', 'visible');

                $('.fail_wrapper').show();
                $('.fail_header').html('<h2>Websockets are not supported in this browser.</h2>');
                $('.fail_message').html('<p>You aren\'t using a browser that supports websockets, so <a href="' + flashLink + '" target="_blank">Adobe Flash</a> is required to view alerts in Alert Birds.  PagerDuty events will still fire if you\'ve set up an endpoint.</p>');


            } else {  //tests for flash blocking
                FBD.initialize(noSocketFlashBlock);

            }
        } else {  //if browser does support web sockets
            if(!FlashDetect.installed) {    //if flash is not installed, informs user that flash is required for sounds
                $('.alert_bubble').css('visibility', 'visible');
                
                $('.fail_wrapper').show();
                $('.fail_header').html('<h2>Flash not installed.</h2>');
                $('.fail_message').html('<p>SoundManager2\'s HTML 5 audio support is in beta, you\'ll still see visual alerts in Alert Birds and get pages from PagerDuty, but if you aren\'t hearing sounds, install <a href="' + flashLink + '" target="_blank">Adobe Flash</a>.</p>');

            } else {
                FBD.initialize(yesSocketFlashBlock);  //tests for flash blocking
            }
        }

    } else if(Apple.Device) {  //if apple device, informs user that sounds for alerts aren't supported
        
        $('.alert_bubble').css('visibility', 'visible');
        
        $('.fail_wrapper').show();
        $('.fail_header').html('<h2>Sounds not supported on this device.</h2>');
        $('.fail_message').html('<p>You\'re on an iOS device, so alerting with sounds is impossible.  Watch for visual cues for alerts and make sure you have a PagerDuty endpoint configured.</p>');

    }
    function noSocketFlashBlock(flash_is_blocked) {  //flashblock detection function for browser that doesn't support websockets
        if(flash_is_blocked) {
            $('.alert_bubble').css('visibility', 'visible');

            $('.fail_header').html('<h2>Websockets not supported in this browser.</h2>');
            $('.fail_message').html('<p>You aren\'t using a browser that supports websockets, so <a href="' + flashLink + '" target="_blank">Adobe Flash</a> needs to be enabled to view alerts.  PagerDuty events will still fire if you\'ve set up an endpoint.</p>');

        }   
    }    

    function yesSocketFlashBlock(flash_is_blocked) {    //flashblock detection function for browser that does support websockets
        if(flash_is_blocked) {
            $('.alert_bubble').css('visibility', 'visible');

            $('.fail_wrapper').show();
            $('.fail_header').html('<h2>Flashblock detected.</h2>');
            $('.fail_message').html('<p>SoundManager2\'s HTML 5 audio support is in beta, you\'ll still see visual alerts in Alert Birds and get pages from Pager Duty, but if you aren\'t hearing sounds, enable <a href="' + flashLink + '" target="_blank">Adobe Flash</a>.</p>');


        } 
    }
    // end websocket, flash install and flash block handling
        
    $('.close_bubble').click( function() {
        $('.alert_bubble').css('visibility', 'hidden');
        $('.alert_description').html('');
    });
    $('.play_button').live('click',function() {
        soundManager.play($('#sound').attr('value'), {
            onfinish: function() {
                $('.chirp_sound img').attr('src', '/static/images/play.png').attr('class', 'play_button');
            }
        });
        if (!$('#sound').attr('value').playState) {
            $('.chirp_sound img').attr('src', '/static/images/stop.png').attr('class', 'stop_button');
        }
    });
    $('.stop_button').live('click', function() {
        soundManager.stop($('#sound').attr('value'));
        $('.chirp_sound img').attr('src', '/static/images/play.png').attr('class', 'play_button');
    });
    $('.question[tooltip]').each(function() {
        $(this).qtip({     
            content: $(this).attr('tooltip')
        });
    });

    $('.dropdown_closed').live('click', function() {
        
        $('#' + $(this).attr('expand')).show();
        $(this).removeClass('dropdown_closed');
        $(this).addClass('dropped_down');
    });
   
    $('.dropped_down').live('click', function() {
    
        $('#' + $(this).attr('expand')).hide();
        $(this).removeClass('dropped_down');
        $(this).addClass('dropdown_closed');
    });

    $('.delete_alert').click(function () {
        if (confirm('Are you sure you want to delete this alert?')) {
            $.ajax({type: 'GET',
                    url: $(this).attr('href'),
                    success: function() {
                        location = location;
                    }
            });
        }  
        return false;
    });       

    $('tr:even').addClass('shaded');
    
    $('select').selectmenu();

});
