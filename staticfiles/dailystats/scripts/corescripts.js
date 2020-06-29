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
        data.cat_id = $("#cat_change_new option:selected").attr('id')
        new_url = '/dailystats/home/';
    } else if (button_id.includes('mf_deleteb_')){
        data.check = 'delete';
        new_url = '/dailystats/home/';
    } else if (info_set.includes(button_id)){
        new_url = '/dailystats/info/' + button_id + '/';
    } else if (button_id == 'cat_submit'){
        new_url = '/dailystats/home/';
        data.cat_name = $('#cat_name').val();
    } else if (button_id == "7_day_overview" || button_id == "30_day_overview"){
        new_url = '/dailystats/overview/';
    } else if (button_id == 'goals'){
        new_url = '/dailystats/goals/';
    } else if(button_id == 'set_goal'){
        new_url = '/dailystats/goals/';
        data.result_goal = $('#result_goal').val();
        data.rate_goal = $('#rate_change').val();
    } else if(button_id == 'change_goal'){
        new_url = '/dailystats/goals/';
    }
    else{
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
                    if (Response == 'Success'){ 
                        loadTemplate('home', 'main')
                        loadTemplate('info/sidenav/', 'aside')
                    } else if (Response.includes("Logged out")){
                        loadTemplate('info/sidenav/', 'aside')
                    }
                }
            },
        });
    }
    if(document.getElementById(current_active)){
        document.getElementById(current_active).className = 'bg-info';
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
            measure_id: button_id,
            new_value:  $(this).val(),
            action: "update_valuefield",
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
        },
        success : function(Response){
            document.getElementById('main').innerHTML = Response;                
        },
    })
        
    }
})

// Listens for changes in select fields
$(document).on('change', 'select', function(event){
    event.preventDefault();
    button_id = $(this).attr('id')
    chosen_option = $("#" + button_id + " option:selected").attr('id')
    relevant_measure = $("#" + button_id + " option:selected").attr('value')
    if (chosen_option.includes('change_cat_')){
        $.ajax({
        type: 'POST',
        url: '/dailystats/home/',
        data: {
            measure_id: button_id,
            new_value:  $(this).val(),
            target_cat: chosen_option,
            target_measure: relevant_measure,
            action: "change_measure_category",
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
        },
        success : function(Response){
            document.getElementById('main').innerHTML = Response;                
        },
    })} else if (chosen_option.includes('overview_cat_')){
        $.ajax({
        type: 'POST',
        url: '/dailystats/overview/',
        data: {
            measure_id: button_id,
            new_value:  $(this).val(),
            target_cat: chosen_option,
            active: relevant_measure,
            action: "change_category",
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