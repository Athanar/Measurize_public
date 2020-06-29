var first_set = "change_username change_firstname change_lastname change_email change_password delete delete_confirmed profile"
var second_set = "user_change_confirmed first_change_confirmed last_change_confirmed"
var info_set = "news about contact navbar sidenav"
var current_active = 'home';

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
    } else if (button_id == 'mail_change_confirmed'){
        data.new_email = $('#new_email').val();
        data.repeat_new_email = $('#repeat_new_email').val();
        new_url = '/dailystats/profile/';
    } else if (button_id == 'pass_change_confirmed'){
        data.new_password = $('#new_password').val();
        data.repeat_new_password = $('#repeat_new_password').val();
        new_url = '/dailystats/profile/';
    } else if (button_id == 'login'){
        data.name = $('#username').val();
        data.password = $('#password').val();
        new_url = '/dailystats/login/';
    } else if (button_id == 'new_user' || button_id == 'logout_button' || button_id == 'login_button'){
        new_url = '/dailystats/login/';
    } else if (button_id == 'make_user'){
        data.name = $('#username').val();
        data.password = $('#password').val();
        data.confirmation = $('#confirmation').val();
        new_url = '/dailystats/registrateUser/';
    } else if (button_id == 'open_sidebar'){
        openNav()
        should_use = false;
    } else if (button_id == 'close_sidebar'){
        closeNav()
        should_use = false;
    } else if (button_id == 'ms_submit'){
        data.name = $('#mf_name').val();
        data.value = $('#mf_value').val();
        data.number = $('#mf_number').val();
        new_url = '/dailystats/home/';
    } else if (button_id.includes('mf_deleteb_')){
        data.check = 'delete';
        new_url = '/dailystats/home/';
    } else if (info_set.includes(button_id)){
        new_url = '/dailystats/info/' + button_id + '/';
    } else{
        should_use = false;
    }
    if (should_use){
        $.ajax({
            type: 'POST',
            url: new_url,
            data: data,
            success : function(Response){
                document.getElementById('main').innerHTML = Response;
                if (button_id == 'delete_confirmed' || button_id == 'login' || 
                    button_id == 'logout_button' || button_id == 'login_button'){
                    loadTemplate('info/navbar/', 'nav')
                    
                    if (button_id == 'login'){ 
                        loadTemplate('home', 'main')
                        loadTemplate('info/sidenav/', 'aside')
                    } 
                }
            },
        });
    }
    if(document.getElementById(current_active)){
        document.getElementById(current_active).className = '';
        this.className = 'active';
        current_active = button_id;
    }else{
        current_active = 'home';
    } 
})

// Listens for changes in input fields
$(document).on('change', 'input', function(event){
    event.preventDefault();
    button_id = $(this).attr('id')
    if (button_id.includes('mf_amount_')){
        $.ajax({
        type: 'POST',
        url: '/dailystats/home/',
        data: {
            number: button_id,
            value:  $(this).val(),
            action: "update_valuefield",
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
        },
        success : function(Response){
            document.getElementById('main').innerHTML = Response;                
        },
    })
        
    }
})

//Loads templates into a base template
function loadTemplate(page, location) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function (params) {
        if (this.readyState == 4 && this.status == 200) {
            var mainDiv = document.getElementsByTagName(location)[0];
            mainDiv.innerHTML = this.responseText;
        }
    }
    xhttp.open("GET", "/dailystats/"+page, true);
    xhttp.send();
}

document.addEventListener("DOMContentLoaded", function() {
    loadTemplate("info/navbar/", 'nav');
});

function openNav() {
    document.getElementById("mySidenav").style.width = "200px";
    document.getElementById("main").style.marginLeft = "200px";
    document.getElementById("close_sidebar").style.marginLeft = "160px";
    document.getElementById("close_sidebar").style.position = "absolute";
    document.getElementById("close_sidebar").style.top = "0";
    document.getElementById("close_sidebar").style.fontSize = "36px";
}
  
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
}