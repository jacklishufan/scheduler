from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from importlib import import_module
from datetime import datetime,timedelta
import subprocess
import os
# from .utils import *
# Create your models here.
# DAG
# Task

def run_function(func_name,*args,**kwargs):
    module_path, function_name = func_name.rsplit('.', 1)
    # import the module and get the function
    module = import_module(module_path)
    func = getattr(module, function_name)
    try:
        res = func(*args, **kwargs)
        return True,res
    except Exception as e:
        print(e)
        return False,e


def run_bash_command(cmd,task_id=None):
    env = os.environ.copy()
    if task_id:
        env['SCHEDULER_TASK_ID']=str(task_id)
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout = ''
    stderr = ''
    return_code = -1
    try:
        return_code = p.returncode
        stdout = p.stdout.decode()
        stderr = p.stderr.decode()
    except:
        pass
    if not return_code:
        return True, stdout
    else:
        return False, stderr


class DAG(models.Model):
    graph_id = models.AutoField(primary_key=True)
    name = models.TextField()
    execution_key = models.TextField(default='default',null=True,blank=True)
    last_launched = models.DateTimeField(null=True, blank=True)

    @property
    def edges(self):
        return TaskEdge.objects.filter(task_from__parent=self) or []

    @property
    def latest_execution(self):
        return self.executions.filter().order_by('-launch_time').first()

    def execute(self):
        self.last_launched = datetime.now()
        self.save()
        execution = ExecutionGraph.objects.create(name=self.name,dag=self)
        tasks = Task.objects.filter(parent=self)
        edges = TaskEdge.objects.filter(task_from__parent=self).prefetch_related('task_from','task_to')
        visited_ids = {}
        for edge in edges:
            from_id = edge.task_from.task_id
            to_id = edge.task_to.task_id
            from_e = visited_ids.get(from_id)
            tgt_e = visited_ids.get(to_id)
            if not from_e:
                from_e = edge.task_from.create_execution_copy(execution)
                visited_ids[from_id]=from_e
            if not tgt_e:
                tgt_e = edge.task_to.create_execution_copy(execution)
                visited_ids[to_id] = tgt_e
            ExecutionEdge.objects.get_or_create(task_from=from_e, task_to=tgt_e)
        tasks = [x for x in tasks if x.task_id not in visited_ids]
        for task in tasks:
            task.create_execution_copy(execution)

    def __str__(self):
        return self.name or ''

class CommandType(models.IntegerChoices):
        OFFLINE = 0, _('offline')
        PYTHON = 1, _('python')
        SYSTEM = 2, _('system')

class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(DAG,on_delete=models.CASCADE,related_name='tasks')
    name = models.TextField()
    key = models.TextField(null=True,blank=True)
    description = models.TextField(null=True, blank=True)
    command = models.TextField(null=True,blank=True)
    configs = models.JSONField(null=True, blank=True)
    auto_report = models.BooleanField(default=True)


    is_py_func = models.IntegerField(choices=CommandType.choices,default=1)

    def create_execution_copy(self,parent):
        return ExecutionTask.objects.create(name=self.name,
                       description=self.description,
                       command = self.command,
                                            configs = self.configs,
                       parent = parent,
                                            is_py_func=self.is_py_func,
                                            key=self.key,
                                            auto_report=self.auto_report
                       )

    def __str__(self):
        return self.name or ''

class TaskEdge(models.Model):
    task_from = models.ForeignKey(Task, related_name='outgoing_edges',on_delete=models.CASCADE)
    task_to = models.ForeignKey(Task,related_name='incoming_edges', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.task_from)+'--'+str(self.task_to)

class ExecutionGraph(models.Model):
    name = models.TextField()
    graph_id = models.AutoField(primary_key=True)
    dag = models.ForeignKey(DAG,null=True,on_delete=models.SET_NULL,related_name='executions')
    launch_time = models.DateTimeField(auto_now_add=True)
    # schedule_time = models.DateTimeField(null=True,blank=True)
    class ExecutionStatus(models.IntegerChoices):
        SCHEDULED = 0, _('scheduled')
        RUNNING = 1, _('running')
        COMPLETED = 2, _('completed')
        FAILED = 3, _('failed')
    status = models.IntegerField(choices=ExecutionStatus.choices,default=ExecutionStatus.RUNNING)

    @property
    def edges(self):
        return ExecutionEdge.objects.filter(task_from__parent=self) or []

    @property
    def success_count(self):
        return self.tasks.filter(status=ExecutionTask.ExecutionStatus.COMPLETED).count()

    @property
    def fail_count(self):
        return self.tasks.filter(status=ExecutionTask.ExecutionStatus.FAILED).count()

    @property
    def task_count(self):
        return self.tasks.filter().count()

    def cancel(self):
        return self.tasks.filter(~Q(status=ExecutionTask.ExecutionStatus.RUNNING)).update(status=ExecutionTask.ExecutionStatus.FAILED,
                                                                    errors={"reason":"cancelled"})
    def __str__(self):
        return f"{self.graph_id}:{self.name}" or ''

class ExecutionTask(models.Model):
    task_id = models.AutoField(primary_key=True)
    parent = models.ForeignKey(ExecutionGraph, on_delete=models.CASCADE, related_name='tasks')
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    command = models.TextField(null=True, blank=True)
    configs = models.JSONField(null=True, blank=True)
    results = models.JSONField(null=True,blank=True)
    cmd_log = models.TextField(null=True,blank=True)
    errors = models.JSONField(null=True, blank=True)
    key = models.TextField(null=True, blank=True)
    is_py_func = models.IntegerField(choices=CommandType.choices, default=1)
    auto_report = models.BooleanField(default=True)

    class ExecutionStatus(models.IntegerChoices):
        SCHEDULED = 0, _('scheduled')
        RUNNING = 1, _('running')
        COMPLETED = 2, _('completed')
        FAILED = 3, _('failed')
    # task = models.ForeignKey(Task,on_delete=models.CASCADE)
    status = models.IntegerField(choices=ExecutionStatus.choices,default=ExecutionStatus.SCHEDULED)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True,blank=True)

    def perform_auto_report(self,success,res):
        if success:
            self.handle_success(res)
        else:
            self.handle_error(res)
    def execute(self):
        self.start_time = datetime.now()
        self.status = self.ExecutionStatus.RUNNING
        self.save()
        if self.is_py_func == CommandType.PYTHON:
            command = self.command or "scheduler.tasks.example_func"
            configs = self.configs or {}
            args,kwargs = configs.get('args',()),configs.get('kwargs',{})
            success,res = run_function(command,*args,**kwargs)
            if self.auto_report:
                self.perform_auto_report(success,res)
        elif self.is_py_func == CommandType.SYSTEM:
            success, res = run_bash_command(self.command,self.task_id)
            if self.auto_report:
                self.perform_auto_report(success, res)
            self.cmd_log = res
            self.save()
        elif self.is_py_func == CommandType.OFFLINE:
            pass

    def handle_success(self,res):
        self.results = {"result":res}
        self.end_time = datetime.now()
        self.status = self.ExecutionStatus.COMPLETED
        self.save()

    def handle_error(self,e):
        exception_string = repr(e)
        self.errors = {"error": exception_string}
        self.end_time = datetime.now()
        self.status = self.ExecutionStatus.FAILED
        self.save()

    def __str__(self):
        return f"{self.parent}->{self.name}" or ''


class ExecutionEdge(models.Model):
    task_from = models.ForeignKey(ExecutionTask, related_name='outgoing_edges', on_delete=models.CASCADE)
    task_to = models.ForeignKey(ExecutionTask, related_name='incoming_edges', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.task_from) + '--' + str(self.task_to)
