from django.urls import path
from . import views

app_name    = "sns"
urlpatterns = [
    path('', views.index, name="index"),
    # single/1/ であればviews.singleを実行する。single/test/ などはviews.single実行しない
    path('single/<int:pk>/', views.single, name="single"),
    path('user_edit/', views.user_edit, name="user_edit"),
]

