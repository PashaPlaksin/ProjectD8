from django.urls import path
from django.conf.urls import url
from .views import IndexView

urlpatterns = [
  path('', IndexView.as_view()),

]