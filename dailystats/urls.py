from django.urls import path


from . import views

app_name = 'dailystats'
urlpatterns = [
    path('login/', views.LoginView, name='login'),
    path('', views.IndexView, name='index'),
    path('profile/', views.ProfileView, name='profile'),
    path('info/<str:site>/', views.infoHandler, name='info'),
    path('overview/', views.OverView, name='overview'),
    path('home/', views.HomeView, name='home'),
    path('goals/', views.goalView, name='goal'),
    path('registrateUser/', views.registrateUser, name='registrateUser'),
]