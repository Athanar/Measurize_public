var first_set = "p_username p_firstname p_lastname p_email p_password delete delete_confirm profile"
var second_set = "user_p_confirm first_p_confirm last_p_confirm"

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
    if (first_set.includes(button_id)){
        new_url = '/dailystats/profile/';
    } else if (second_set.includes(button_id)){
        data.new_name = $('#new_name').val();
        new_url = '/dailystats/profile/';
    } else if (button_id == 'mail_p_confirm'){
        data.new_email = $('#new_email').val();
        data.repeat_new_email = $('#repeat_new_email').val();
        new_url = '/dailystats/profile/';
    } else if (button_id == 'pass_p_confirm'){
        data.new_password = $('#new_password').val();
        data.repeat_new_password = $('#repeat_new_password').val();
        new_url = '/dailystats/profile/';
    } else{
        should_use = false;
    }
    if (should_use){
        $.ajax({
            type: 'POST',
            url: new_url,
            data: data,
            success : function(Response){
                if (button_id == 'user_p_confirm') {
                    usernameChange(Response, '#'+button_id);
                } else if (button_id == 'pass_p_confirm'){
                    passwordChange(Response, '#'+button_id)
                } else if (button_id == 'mail_p_confirm'){
                    emailChange(Response, '#'+button_id)
                } else if (button_id == 'first_p_confirm' ||
                           button_id == 'last_p_confirm'){
                    nameChange(Response, '#'+button_id)
                } else if (button_id == 'delete_confirm'){
                    userDelete()
                } else {
                    $('#main').html(Response)
                }
            },
        });
    }
})

// Handles username changes
function usernameChange(response, place){
    var replace = true
    $(place).popover('dispose');
    if (response.check == false){
        replace = false
        $(place).popover({
            html: true,
            content: '<b>'+response.message+'</b>',
        }).popover('show');
    } 
    if (replace){
        $('#p_username').html(response.name);
        $('#p_card').html("");
    }
}

// Handles password changes
function passwordChange(response, place){
    var replace = true
    $(place).popover('dispose');
    if (response.check == false){
        replace = false
        $(place).popover({
            html: true,
            content: '<b>'+response.message+'</b>',
        }).popover('show');
    } 
    if (replace){
        loadTemplate('login', 'main');
        loadTemplate('info/sidenav/', 'aside');
        loadTemplate('info/navbar/', 'nav');
        alert("Password successfully changed");
    }
}

// Handles email changes
function emailChange(response, place){
    var replace = true
    $(place).popover('dispose');
    if (response.check == false){
        replace = false
        $(place).popover({
            html: true,
            content: '<b>'+response.message+'</b>',
        }).popover('show');
    } 
    if (replace){
        $('#p_email').html(response.name);
        $('#p_card').html("");
    }
}

function nameChange(response, place){
    if (place.includes('first')){
        $('#p_first').html(response.name);
    } else {
        $('#p_last').html(response.name);
    }
    $('#p_card').html("");
}

function userDelete(){
    loadTemplate('info/navbar/', 'nav')
    loadTemplate('login', 'main')
    loadTemplate('info/sidenav/', 'aside')
}