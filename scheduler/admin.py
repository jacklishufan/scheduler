from django.contrib import admin
from .models import *

# Register your models here.
MODELS = [
    DAG,
    Task,
    ExecutionGraph,
    TaskEdge,
    ExecutionEdge,
    ExecutionTask
]
for model in MODELS:
    admin.register(model)(admin.ModelAdmin)
