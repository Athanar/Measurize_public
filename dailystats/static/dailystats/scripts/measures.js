// Listens for button clicks and handles any such event
$(document).on('click','button', function(event){
    event.preventDefault();  
    var button_id = $(this).attr('id')
    var data = {
        action: button_id,
        csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
    };
    var should_use = true;
    if (button_id == 'ms_submit'){
        data.name = $('#mf_name').val();
        data.value = $('#mf_value').val();
        data.number = $('#mf_number').val();
        data.cat_id = $("#cat_change_new option:selected").attr('id')
    } else if (button_id.includes('mf_deleteb_')){
        data.check = 'delete';
    } else if (button_id == 'cat_submit'){
        data.cat_name = $('#cat_name').val();
    } else if (button_id.includes('edit_view_') || 
               button_id.includes('measure_view_') ||
               button_id.includes('cat_deleteb_')) {
    } else{
        should_use = false;
    }
    if (should_use){
        $.ajax({
            type: 'POST',
            url: '/dailystats/home/',
            data: data,
            success : function(Response){
                if (button_id.includes('edit_view_')){
                    editView(button_id.substring(10), Response);
                } else if (button_id.includes('measure_view_')){
                    measureView(button_id.substring(13), Response);
                }else{
                    $('#main').html(Response);
                }
            },
        });
    }
})



// Listens for changes in input fields
$(document).on('change', 'input', function(event){
    event.preventDefault();
    input_id = $(this).attr('id')
    if (input_id.includes('mf_amount_')){
        $.ajax({
        type: 'POST',
        url: '/dailystats/home/',
        data: {
            measure_id: input_id,
            new_value:  $(this).val(),
            action: "update_amountfield",
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
        },
        success : function(Response){
            var val = $('#'+input_id).closest('table').attr('id').substring(6);
            var amount = parseFloat(document.getElementById('mf_result_'+input_id.substring(10)).innerHTML);
            var current = parseFloat(document.getElementById('result_'+val).innerHTML);
            var result = current - amount + parseFloat(Response.result.toFixed(1));
            document.getElementById('result_'+val).innerHTML =  result.toFixed(1);
            document.getElementById(input_id).value = Response.value.toFixed(1);              
            document.getElementById('mf_result_'+input_id.substring(10)).innerHTML = Response.result.toFixed(1);
        },
    })  
    } else if (input_id.includes('mf_val_')){
        $.ajax({
            type: 'POST',
            url: '/dailystats/home/',
            data: {
                measure_id: input_id,
                new_value:  $(this).val(),
                action: "update_valuefield",
                csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
            },
            success : function(Response){
                $(input_id).val(Response.value.toFixed(1));
            },
        }) 
    }
})

// Listens for changes in select fields
$(document).on('change', 'select', function(event){
    event.preventDefault();
    select_id = $(this).attr('id')
    chosen_option = $("#" + select_id + " option:selected").attr('id')
    relevant_measure = $("#" + select_id + " option:selected").attr('value')
    if (chosen_option.includes('change_cat_')){
        $.ajax({
        type: 'POST',
        url: '/dailystats/home/',
        data: {
            measure_id: select_id,
            new_value:  $(this).val(),
            target_cat: chosen_option,
            target_measure: relevant_measure,
            action: "change_measure_category",
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
        },
        success : function(Response){
            document.getElementById('main').innerHTML = Response;                
        },
    })}
})

function editView(number, response){
    $('#measure_view_'+number).removeClass("active");
    $('#edit_view_'+number).addClass("active");
    $('#table_'+number).html(response);
}

function measureView(number, response){
    $('#edit_view_'+number).removeClass("active");
    $('#measure_view_'+number).addClass("active");
    $('#table_'+number).html(response);
}
