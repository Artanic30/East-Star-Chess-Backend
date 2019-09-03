from django.urls import path


from . import views


urlpatterns = [
    path('<int:board_id>', views.init_game, name='init'),
    path('update/<int:board_id>', views.update, name='update'),
    path('login', views.account_login, name='login'),
    path('init', views.init_state, name='init'),
    path('logout', views.account_logout, name='logout'),
    path('register', views.register, name='register'),
    path('profile/<str:name>', views.profile, name='profile'),
    path('match/init', views.init_match, name='init_match'),
    path('players/<int:board_id>', views.players, name='players'),
]
