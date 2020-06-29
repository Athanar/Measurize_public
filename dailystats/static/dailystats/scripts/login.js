// Listens for button clicks and handles any such event
$(document).on('click','button', function(event){
    event.preventDefault();  
    var button_id = $(this).attr('id')
    var new_url = ''
    var data = {
        action: button_id,
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
    };
    var should_use = true;
    if (button_id == 'login'){
        data.name = $('#username').val();
        data.password = $('#password').val();
        new_url = '/dailystats/login/';
    } else if (button_id == 'new_user'){
        new_url = '/dailystats/login/';
    } else if (button_id == 'make_user'){
        data.name = $('#username').val();
        data.password = $('#password').val();
        data.confirmation = $('#confirmation').val();
        new_url = '/dailystats/registrateUser/';
    } else{
        should_use = false;
    }
    if (should_use){
        $.ajax({
            type: 'POST',
            url: new_url,
            data: data,
            success : function(Response){
                if (button_id == 'make_user'){
                    makeUser(Response);
                } 
                else if (button_id == 'new_user'){
                    document.getElementById('main').innerHTML = Response;
                }
                else {
                    HandleLogin(Response);
                }
            },
        });
    }
})

// Handles enter press
$(document).keypress(function(event){
    data = {
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
    }
    var keycode = (event.keyCode ? event.keyCode : event.which);
	if(keycode == '13' && $('#login')[0] != null){
        data.name = $('#username').val();
        data.password = $('#password').val();
        data.action = 'login';
		$.ajax({
            type: 'POST',
            url: '/dailystats/login/',
            data: data,
            success : function(Response){
                HandleLogin(Response);
            },
        });
    }
    else if (keycode == '13' && $('#make_user')[0] != null) {
        data.name = $('#username').val();
        data.password = $('#password').val();
        data.confirmation = $('#confirmation').val();
        data.action = 'make_user';
		$.ajax({
            type: 'POST',
            url: '/dailystats/registrateUser/',
            data: data,
            success : function(Response){
                makeUser(Response);
            },
        });
    }
	
});

// Handles user creation attempts
function makeUser(response){
    var replace = true
    $('#username').popover('dispose');
    $('#password').popover('dispose');
    if (response.check == false){
        replace = false
        $('#username').popover({
            html: true,
            placement: 'right',
            content: '<b>'+response.message+'</b>',
        }).popover('show');
    } 
    if (response.pwcheck == false){
        replace = false
        $('#password').popover({
            html: true,
            placement: 'right',
            content: '<b>'+response.pwmessage+'</b>',
        }).popover('show');
    }
    if (replace){
        document.getElementById('main').innerHTML = response;
    }
}

// Handles response to login attempt and loads next views
function HandleLogin(response){
    $('#login').popover('dispose');
    if (response.check == false){
        $('#login').popover({
            html: true,
            placement: 'bottom',
            content: '<b>'+response.message+'</b>',
        }).popover('show');
    } else{
        loadTemplate('home', 'main')
        loadTemplate('info/sidenav/', 'aside')
        loadTemplate('info/navbar/', 'nav')
    }
}
