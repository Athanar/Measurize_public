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
    if (button_id == "7_day_overview" || button_id == "30_day_overview"){
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
            },
        });
    }
})

// Listens for changes in select fields
$(document).on('change', 'select', function(event){
    event.preventDefault();
    button_id = $(this).attr('id')
    chosen_option = $("#" + button_id + " option:selected").attr('id')
    relevant_measure = $("#" + button_id + " option:selected").attr('value')
    if (chosen_option.includes('overview_cat_')){
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