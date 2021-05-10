from rest_framework.serializers import ModelSerializer,SerializerMethodField
from .models import *



class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'task_id',
            'parent',
            'name',
            'key',
            'description',
            'command',
            'is_py_func',
            'auto_report',
            'configs'
        ]


class DAGListSerializer(ModelSerializer):
    class Meta:
        model = DAG
        fields = [
            'graph_id',
            'name',
            'last_launched',
            'execution_key'
        ]
        extra_kwargs = {'last_launched': {'read_only': True}}






class TaskEdgeSerializer(ModelSerializer):
    class Meta:
        model = TaskEdge
        fields = [
            'task_from',
            'task_to',
        ]

class DAGSerializer(ModelSerializer):
    class Meta:
        model = DAG
        fields = [
            'graph_id',
            'name',
            'tasks',
            'execution_key',
            'edges',
            'last_launched'
        ]
        extra_kwargs = {'last_launched': {'read_only': True}}


    tasks = TaskSerializer(read_only=True,many=True)
    edges = TaskEdgeSerializer(read_only=True, many=True)







class ExecutionTaskSerializer(ModelSerializer):
    class Meta:
        model = ExecutionTask
        fields = [
            'task_id',
            'parent',
            'key',
            'name',
            'description',
            'command',
            'configs',
            'results',
            'cmd_log',
            'is_py_func',
            'auto_report',
            'errors',
            'status',
            'start_time',
            'end_time'
        ]


class ExecutionEdgeSerializer(ModelSerializer):
    class Meta:
        model = ExecutionEdge
        fields = [
            'task_from',
            'task_to',
        ]


class ExecutionGraphSerializer(ModelSerializer):
    class Meta:
        model = ExecutionGraph
        fields = [
            'graph_id',
            'name',
            'dag',
            'status',
            'tasks',
            'edges',
            'launch_time'
        ]
    tasks = ExecutionTaskSerializer(read_only=True, many=True)
    edges = ExecutionEdgeSerializer(read_only=True,many=True)


class ExecutionListSerializer(ModelSerializer):
    class Meta:
        model = ExecutionGraph
        fields = [
            'graph_id',
            'name',
            'dag',
            'status',
            'launch_time',
            'success_count',
            'fail_count',
            'task_count',
        ]

