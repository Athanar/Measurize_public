from dailystats.models import Measure, AmountModel, Category, DBUserinfo
import datetime

def makeMeasurefield(request):    
    if (request.POST.get('cat_id', False)):
        requested_category = request.POST.get('cat_id', False)[11:]
    else:
        requested_category = Category.objects.first().id
    
    # New Measure object with input data
    measure = Measure(
        category = Category.objects.filter(id = requested_category)[0],
        user_link = request.user,
        measure_name = request.POST.get('name', False),
        measure_val = float(request.POST.get('value', False)),
        measure_input = float(request.POST.get('number', False)),
    )
    measure.save()
    # New storage object with same input data
    
    new_amount = AmountModel(
        measurefield_id = measure.id, 
        input_value = float(request.POST.get('value', False)),
        input_amount = float(request.POST.get('number', False)),
        result_number = (float(request.POST.get('value', False)) * 
                        float(request.POST.get('number', False)))
    )
    new_amount.save()
    
def updateMeasurefield(request):
    # Find relevant measure to change
    current_id = request.POST.get('measure_id', False)
    measure = Measure.objects.filter(id = current_id[10:])[0]
    # Finds a storage object matching the date today and the relevant measure
    if (AmountModel.objects.filter(measurefield_id = measure.id, 
            creation_date = datetime.date.today()).exists()):
        amount = AmountModel.objects.filter(measurefield_id = measure.id, 
            creation_date = datetime.date.today()).first()
        if (float(request.POST.get('new_value', False)) < 0):
            amount.input_amount = 0.0
            amount.save()
        else:
            amount.input_amount = float(request.POST.get('new_value', False))
            amount.save()
        measure.measure_input = amount.input_amount
        measure.result_number = amount.input_amount * measure.measure_val
        measure.save()
        return measure.measure_input, round(measure.measure_val * measure.measure_input,1)
        
    else:
        makeAmountObjects(request.user, DBUserinfo.objects.filter(user_link = request.user).first())

def updateMeasureValue(request):
     # Find relevant measure to change
    current_id = request.POST.get('measure_id', False)
    measure = Measure.objects.filter(id = current_id[7:])[0]
    # Finds a storage object matching the date today and the relevant measure
    if (AmountModel.objects.filter(measurefield_id = measure.id, 
            creation_date = datetime.date.today()).exists()):
        amount = AmountModel.objects.filter(measurefield_id = measure.id, 
            creation_date = datetime.date.today()).first()
        amount.input_value = float(request.POST.get('new_value', False))
        amount.save()
        measure.measure_val = amount.input_value
        measure.result_number = amount.input_value * measure.measure_input
        measure.save()
        return measure.measure_val

def deleteMeasurefield(target):
    measure = Measure.objects.filter(id = target)[0]
    amount_list = AmountModel.objects.filter(measurefield_id = measure.id)
    for amount in amount_list:
        amount.delete()
    measure.delete()

def makeAmountObjects(user, check_field):
    # Creates new storage objects for all measurefields belonging to current user
    for measure in Measure.objects.filter(user_link = user):
        amount = AmountModel(
            measurefield_id = measure.id,
            input_value = measure.measure_val
        )
        amount.save()
        # Updated today
        check_field.last_updated = datetime.date.today()
        check_field.save()

def makeAmountList(request, date_list, field):
    # Gets all measures for current user
    measure_list = Measure.objects.filter(user_link = 
        request.user).order_by('id')
    amount_list = []
    if (Measure.objects.exists()):
        # Iterates through each measure and dateinput to find matching storage
        # objects. These are then appended to a list and returned
        for measure in measure_list:
            # Temporary list used in the loop
            tmp_list = [measure.measure_name]
            for i in range(len(date_list)):
                # Check date and measure id
                if(AmountModel.objects.filter(measurefield_id = measure.id, 
                        creation_date = date_list[i]).exists()):
                    # Storage object
                    relevant_amount = AmountModel.objects.filter(
                        measurefield_id = measure.id, 
                        creation_date = date_list[i])[0]
                    # Return the correct values
                    if (field == 'value'):
                        tmp_list.append(relevant_amount.input_value)
                    elif (field == 'amount'):
                        tmp_list.append(relevant_amount.input_amount)
                    else:
                        tmp_list.append(relevant_amount.input_value 
                            * relevant_amount.input_amount)
                else:
                    tmp_list.append(0.0)
            # Append the temp list to return list
            amount_list.append(tmp_list)
    return amount_list

def getTotal(request, date_list):
    # Gets all measures for current user
    measure_list = Measure.objects.filter(user_link = 
        request.user).order_by('id')
    total_list = []
    if (Measure.objects.exists()):
        # Iterates through each measure and dateinput to find matching storage
        # objects. These are then appended to a list and returned 
        for i in range(len(date_list)):
            tmp_list = []
            for measure in measure_list:
                if(AmountModel.objects.filter(measurefield_id = measure.id, 
                        creation_date = date_list[i]).exists()):
                    # Storage object
                    relevant_amount = AmountModel.objects.filter(
                        measurefield_id = measure.id, 
                        creation_date = date_list[i])[0]
                    tmp_list.append(relevant_amount.input_value 
                        * relevant_amount.input_amount)
                else:
                    tmp_list.append(0.0)
            # Summing up the temp list
            total_list.append(sum(tmp_list))
    else:
        total_list = [0.0 for i in range(len(date_list))]
    return total_list