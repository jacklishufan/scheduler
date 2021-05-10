"""airflow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .api import *

urlpatterns = [
    path('dag/list/', DAGListView.as_view()),
    path('dag/create/', DAGCreateView.as_view()),
    path('dag/<int:pk>/execute/',DAGExecuteView.as_view()),
    path('edge/create/', TaskEdgeCreateView.as_view()),
    path('dag/<int:pk>/', DAGUpdateView.as_view()),
    path('task/create/', TaskCreateView.as_view()),
    path('task/<int:pk>/', TaskUpdateView.as_view()),
    path('edge/<int:pk>/', TaskEdgeUpdateView.as_view()),
    path('execution/list/', ExecutionGraphListView.as_view()),
    path('execution/<int:pk>/cancel/', ExecutionCancelView.as_view()),
    path('execution/<int:pk>/', ExecutionRetrievelView.as_view()),
    path('execution/tasks/<int:pk>/', ExecutionTaskUpdateView.as_view()),
    path('execution/tasks/<int:pk>/report/', ExecutionTaskReportView.as_view()),
    path('execution/report-by-key/<str:key>/', ExecutionTaskReportByKeyView.as_view()),
    path('execution/key/', ExecuteTaskByKeyView.as_view()),
]
