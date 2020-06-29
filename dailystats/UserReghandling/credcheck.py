from django.contrib.auth.models import User
import re

def userCreateCheck(name, pw, confirmation):
    return usernameCheck(name) + passwordCheck(pw, confirmation)    

def usernameCheck(user):
    approval = False
    message = ""
    if (user == ""):
        message = "Please input username"
    elif (len(user) < 5):
        message = "Username must be over 4 characters"
    elif (User.objects.filter(username = user)):
        message = "Username already taken"
    else:
        message = "Username approved"
        approval = True
    return approval, message


def passwordCheck(password, confirmation):
    message = ""
    rules = [lambda s: any(x.isupper() for x in s), # must have at least one uppercase
        lambda s: any(x.islower() for x in s),  # must have at least one lowercase
        lambda s: any(x.isdigit() for x in s),  # must have at least one digit
        lambda s: len(s) >= 7,                   # must be at least 7 characters
        lambda s: s == confirmation
        ]
    if (not rules[4](password)):
        message = "Passwords must match"
    elif (not rules[3](password)):
        message = "Password must be at least 7 characters"
    elif (not all(rule(password) for rule in rules[0:2])):
        message = "Password must contain uppercase, lowercase and digit"
    else:
        message = "Password approved"
    return all(rule(password) for rule in rules), message

def emailCheck(mail, confirm):
    message = ""
    check = re.match(r'(\w+@\w+.\w+)', mail)
    if (not check):
        message = "Email invalid"
    elif (mail != confirm):
        message = "Inputs mail not the same"
        check = False
    else:
        message = "Success"
    return bool(check), message
    