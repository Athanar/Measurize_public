from dailystats.models import Measure, AmountModel, Category, Goal
import datetime

def storeGoal(user):
    if (Goal.objects.filter(user=user).latest('creation_date').
                creation_date < datetime.date.today()):
        old_goal = Goal.objects.filter(user = user).latest('creation_date')
        new_goal = Goal(
            user = user,
            goal_value = old_goal.goal_value + old_goal.goal_value*old_goal.rate_of_change/100,
            rate_of_change = old_goal.rate_of_change
        )
        new_goal.save()

def makeGoal(request):        
    goal = Goal(
        user = request.user,
        goal_value = request.POST.get('result_goal', False),
        rate_of_change = request.POST.get('rate_change', False)
    )
    goal.save()

def updateGoal(request):
    goal = Goal.objects.filter(user = request.user).latest('creation_date')
    if (request.POST.get('result_goal', False)):
        goal.goal_value = request.POST.get('result_goal', False)
    if (request.POST.get('rate_goal', False)):
        goal.rate_of_change = request.POST.get('rate_goal', False)
    goal.save()

def getGoals(request, date_list):
    # Gets all measures for current user
    total_list = []
    # Iterates through each measure and dateinput to find matching storage
    # objects. These are then appended to a list and returned 
    for date in date_list:
        if(Goal.objects.filter(user=request.user, creation_date=date).exists()):
            total_list.append(Goal.objects.filter(user=request.user, 
                creation_date=date)[0].goal_value)
        else:
            total_list.append(0.0)
    return total_list

