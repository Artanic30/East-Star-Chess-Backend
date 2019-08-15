from django.urls import path


from . import views


urlpatterns = [
    path('', views.init_game, name='init'),
    path('update', views.update, name='update'),
    path('login', views.account_login, name='login'),
    path('logout', views.account_logout, name='logout'),
    path('register', views.register, name='register'),
    path('profile/<str:name>', views.profile, name='profile'),
]
