from django.urls import path
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()

router.register(r'game', views.GameViewSet, base_name='game')
router.register(r'account', views.AccountViewSet, base_name='account')


urlpatterns = [
    path('init', views.init_state, name='init'),
]

urlpatterns += router.urls

