var info_set = "news about contact navbar sidenav"

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
    if (button_id == 'profile'){
        new_url = '/dailystats/profile/';
    } else if (button_id == 'logout_button' || button_id == 'login_button'){
        new_url = '/dailystats/login/';
    } else if (info_set.includes(button_id)){
        new_url = '/dailystats/info/' + button_id + '/';
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
                $('#main').html(Response);
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
