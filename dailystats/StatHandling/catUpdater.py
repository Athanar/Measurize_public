from dailystats.models import Measure, AmountModel, Category
import datetime

def makeCategory(user, name):
    category = Category(
        user = user,
        category_name = name,
    )
    category.save()

def changeCategory(request):
    if (request.POST.get('target_measure', False)):
        target_measure = request.POST.get('target_measure', False)[8:]
        target_category = request.POST.get('target_cat', False)[11:]
        measure = Measure.objects.filter(id = target_measure)[0]
        measure.category = Category.objects.filter(id = target_category)[0]
        measure.save()

def categoryTotal(user, category, date_list):
    measure_list = Measure.objects.filter(user_link = user).order_by('id')
    total_list = [category.id]
    # Iterates through each measure and dateinput to find matching storage
    # objects. These are then appended to a list and returned 
    if (Measure.objects.exists()):
        for i in range(len(date_list)):
            tmp_list = []
            for measure in measure_list:
                if (measure.category == category and 
                    AmountModel.objects.filter(measurefield_id = measure.id, 
                        creation_date = date_list[i]).exists()):
                    # Storage object
                    relevant_amount = AmountModel.objects.filter(
                        measurefield_id = measure.id, 
                        creation_date = date_list[i])[0]
                    tmp_list.append(relevant_amount.input_value 
                        * relevant_amount.input_amount)
                else:
                    tmp_list.append(0.0)
            total_list.append(sum(tmp_list))
    return total_list

def makeCatAmountList(user, date_list, field, category):
    # Gets all measures for current user
    measure_list = Measure.objects.filter(user_link = user).order_by('id')
    amount_list = []
    # Iterates through each measure and dateinput to find matching storage
    # objects. These are then appended to a list and returned
    if (Measure.objects.exists()):
        for measure in measure_list:
            if (measure.category == category):
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