from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
import datetime, random
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import numpy as np

from .StatHandling import mfUpdater, catUpdater, grapher, goalUpdater
from .UserReghandling import credcheck
from .models import Measure, AmountModel, Category, Goal, DBUserinfo
from .forms import FirstForm

def inputGet(request, retrieve, target):
    if (len(target) > 0):
        return (request.POST.get(retrieve, False) == target)
    else:
        return request.POST.get(retrieve, False)

def randNumber():
    return random.random()

def IndexView(request):
    return render(request, 'dailystats/index.html', {'random': randNumber()})

def infoHandler(request, site):
    return render(request, f'dailystats/{site}.html')

@login_required(login_url='/dailystats/')
def goalView(request):
    # Sets new goals or makes a new goal
    if (inputGet(request, 'action', 'set_goal')):
        if (Goal.objects.filter(user = request.user).exists()):
            goalUpdater.updateGoal(request)
        else:
            goalUpdater.makeGoal(request)
    # Changes current goal
    if (inputGet(request, 'action', 'p_goal')):
        return render(request, 'dailystats/goal.html', {
            'goal':Goal.objects.filter(user=request.user).
                latest('creation_date'), 'p_goal':True})
    # Shows current goal view and stores previous
    elif (Goal.objects.filter(user = request.user).exists()):
        goalUpdater.storeGoal(request.user)
        return render(request, 'dailystats/goal.html', {
            'goal':Goal.objects.filter(user=request.user).
                latest('creation_date')})
    else:
        return render(request, 'dailystats/goal.html')

@login_required(login_url='/dailystats/')
def OverView(request):
    current_active = 0
    categories = Category.objects.filter(user = request.user).order_by('id')
    # Used to make a list of the past week(7 days) reversed for display 
    # TODO option for display instead of only reverse
    base = datetime.date.today()
    interval = ""
    if (request.POST.get('action', False) == "7_day_overview" or 
            request.POST.get('active', False) == "7"):
        current_active = 7
        interval = "7-day"
    elif (request.POST.get('action', False) == "30_day_overview" or 
            request.POST.get('active', False) == "30"):
        current_active = 30
        interval = "30-day"
    date_list = [base - datetime.timedelta(days=x) for x in range(current_active)]
    graph_source = f"dailystats/images/{current_active}_day_overview.png"
    date_list.reverse()
    # Gets a 2D list of specific category data for past week as well as a list 
    # of sums for each day. Current returns results only
    if (request.POST.get('action', False) == "p_category" and not 
           request.POST.get('target_cat', False) == "overview_cat_all" ):
        category = Category.objects.filter(id = int(request.POST.get(
                'target_cat', False)[13:]))[0] 
        stored_amounts_list2 = catUpdater.makeCatAmountList(request.user, 
            date_list, 'result', category)
        total_list = catUpdater.categoryTotal(request.user, category, date_list)[1:]
        category_new = category.id
    # Gets a 2D list of data for past week as well as a list of sums for each day. 
    # Current returns results only
    else:
        stored_amounts_list2 = []
        for category in categories:
            new_list = [category.category_name] + catUpdater.categoryTotal(
                request.user, category, date_list)[1:]
            stored_amounts_list2.append(new_list)
        total_list = mfUpdater.getTotal(request, date_list)
        category_new = 0
    
    goal_list = goalUpdater.getGoals(request, date_list)
    grapher.plotData(total_list, goal_list, date_list, graph_source)
    return render(request, 'dailystats/overview.html', 
        {'amounts': stored_amounts_list2, 'dates': date_list,
            'total_results':total_list, 'graph': graph_source, 
                'categories': categories, 'active': current_active,
                    'random': randNumber(), 'cat_id': category_new, 
                        'goals': goal_list, 'interval': interval})

@login_required(login_url='/dailystats/')
def HomeView(request):
    action = request.POST.get('action', False)
    # Create new category
    if (action == 'cat_submit'):
        catUpdater.makeCategory(request.user, request.POST.get('cat_name', False))
    elif (not Category.objects.filter(user = request.user).order_by('id').exists()):
        catUpdater.makeCategory(request.user, "None")
    # Change category of Measure
    elif (action == 'change_measure_category'):
        catUpdater.changeCategory(request)
    elif (action and action.find('cat_deleteb_') != -1):
        category = Category.objects.filter(id = action[12:])[0]
        category.delete()
    # Method for deletion of a Measure and its corresponding stored amount objects
    elif (request.POST.get('check', False) == 'delete'):
        mfUpdater.deleteMeasurefield(action[11:])
    # Generates new storage amount objects on new day or if none currently exist        
    if (Measure.objects.filter(user_link = request.user).exists()):
        check_field = DBUserinfo.objects.filter(user_link = request.user).first()
        if (check_field.last_updated < datetime.date.today() 
                or not AmountModel.objects.exists()):
            mfUpdater.makeAmountObjects(request.user, check_field)
    # Handle category for new user and ensure that the correct categories are used for rendering
    if (not Category.objects.filter(user=request.user).exists()):
        catUpdater.makeCategory(request.user, 'None')
    categories = Category.objects.filter(user = request.user).order_by('id')
    categories2 = []
    for i in range(1, len(categories), 3):
        if (i + 3 < len(categories)):
            categories2.append(categories[i:i+3])
        elif (i + 3 == len(categories)):
            categories2.append(categories[i:i+3])
            categories2.append([categories[0]])
        else:
            categories2.append(categories[i:len(categories)])
            categories2[len(categories2)-1].append(categories[0])
    # Creates new field 
    if (request.POST.get('name', False)):
        mfUpdater.makeMeasurefield(request)
    # Updates valuefields
    elif (action == "update_amountfield"):
        cals = mfUpdater.updateMeasurefield(request)
        return JsonResponse({'value': cals[0], 'result':cals[1]})
    elif (action == "update_valuefield"):
        cals = mfUpdater.updateMeasureValue(request)
        return JsonResponse({'value': cals})
    # Generate edit view
    if (action and action.find('edit_view') != -1):
        category = Category.objects.filter(id = action[10:])[0]
        measures = Measure.objects.filter(category = category).order_by('id')
        return render(
            request, 
            'dailystats/editfield.html',
            {'measures': measures,
             'this_cat': category, 
             'categories': categories, 
             'edit': True})
    elif (action and action.find('measure_view') != -1):
        category = Category.objects.filter(id = action[13:])[0]
        measures = Measure.objects.filter(category = category).order_by('id')
        total = catUpdater.categoryTotal(request.user, 
                    category, [datetime.date.today()])[1]
        return render(
            request, 
            'dailystats/editfield.html',
            {'measures': measures,  
             'total': total, 
             'num': action[13:]})
    # Generates list of objects connected to current user to send to html
    measure = Measure.objects.filter(user_link = request.user).order_by('id')
    # Calculates daily total
    total_results = [mfUpdater.getTotal(request, [datetime.date.today()])]
    for category in categories:
        total_results.append(catUpdater.categoryTotal(request.user, 
            category, [datetime.date.today()]))
    # Rendering
    return render(
        request, 
        'dailystats/measurefields.html', 
        {'measures': measure, 
        'totals': total_results, 
        'categories': categories,
        'categories2': categories2})

def LoginView(request):
    #Logout user if required
    if(request.POST.get('action', False) == 'logout_button'):
        logout(request)
        return render(request, 'dailystats/login.html', 
            {'new_user':False, 'approval': "Logged out successfully"})
    #Redirect to new user registration
    if (request.POST.get('action', False)  == 'new_user'):
        return render(request, 'dailystats/login.html', {'new_user':True})
    #Login user if conditions are met
    elif(request.POST.get('action', False) == 'login'):
        #Authenticate credentials
        user = authenticate(request, username=request.POST.get('name', False), 
            password=request.POST.get('password', False))
        if (user is not None):
            login(request, user)
            request.session.set_expiry(100000)
            return HttpResponse('Success')
        #Attempted login with either wrong password or username
        elif (user is None):
            logout(request)
            return JsonResponse({'check':False, 'message': "Wrong username or password"})
    #Initial login screen
    else:
        return render(request, 'dailystats/login.html', {'new_user':False, 'approval': ""})

def registrateUser(request):
    #Checks username and password is available
    check_availability = credcheck.userCreateCheck(
        request.POST.get('name', False),
        request.POST.get('password', False),
        request.POST.get('confirmation'))
    if (not check_availability[0] or not check_availability[2]):
        return JsonResponse({
            'check': check_availability[0], 
            'message': check_availability[1],
            'pwcheck': check_availability[2],
            'pwmessage': check_availability[3]})
    #Creates and saves new user. Redirects to login screen
    user = User.objects.create_user(request.POST.get('name', False))
    user.set_password(request.POST.get('password', False))
    user.save()
    db = DBUserinfo(
        user_link  = user,
    )
    db.save()
    return render(
        request, 
        'dailystats/login.html', 
        {'new_user':False, 
        'approval':"Success"})

@login_required(login_url='/dailystats')
def ProfileView(request):
    action = request.POST.get('action', False)
    # Base profile view
    if (not action or action == 'profile'):
        return render(
            request, 
            'dailystats/profile.html', 
            {'user': request.user})
    # User deletion
    elif (action == 'delete_confirm'):
        request.user.delete()
        return JsonResponse({
            'check': True,
            'message': 'User successfully deleted'})
    # Username check and change
    elif (action == 'user_p_confirm'):
        new_name = request.POST.get('new_name', False)
        new_name_check = credcheck.usernameCheck(new_name)
        if (new_name_check[0]):
            request.user.username = new_name
            request.user.save()
        return JsonResponse(
            {'check': new_name_check[0], 
            'message': new_name_check[1],
            'name': new_name})
    # First name change
    elif (action == 'first_p_confirm'):
        new_name = request.POST.get('new_name', False)
        request.user.first_name = new_name
        request.user.save()
        return JsonResponse({
            'check': True, 
            'message': 'Success',
            'name': new_name})
    # Last name change
    elif (action == 'last_p_confirm'):
        new_name = request.POST.get('new_name', False)
        request.user.last_name = new_name
        request.user.save()
        return JsonResponse({
            'check': True, 
            'message': 'Success',
            'name': new_name})
    # Email check and change
    elif (action == 'mail_p_confirm'):
        new_email = request.POST.get('new_email', False)
        email_confirm = request.POST.get('repeat_new_email', False)
        email_check = credcheck.emailCheck(new_email, email_confirm)
        if (email_check[0]):
            request.user.email = new_email
            request.user.save()
        return JsonResponse({
            'check': email_check[0],
            'message': email_check[1],
            'name': new_email})
    # Password check and change
    elif (action == 'pass_p_confirm'):
        new_password = request.POST.get('new_password', False)
        confirm = request.POST.get('repeat_new_password')
        password_check = credcheck.passwordCheck(new_password, confirm)
        if(password_check[0]):
            request.user.set_password(new_password)
            request.user.save()
            logout(request)
        return JsonResponse({
            'check': password_check[0],
            'message': password_check[1]
        })
    else:
        return render(
            request, 
            'dailystats/profile.html', 
            {'user': request.user, 
            'action': action})

    