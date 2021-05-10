from .models import *
from django.db.models import Q,Count
from multiprocessing.dummy import Process as Thread
from multiprocessing import Process
from multiprocessing.dummy import Pool as ThreadP
#from celery_backend.celery_core import celery_core
from django import db

def get_excuable_tasks():
    qs = ExecutionTask.objects.filter(parent__status=ExecutionGraph.ExecutionStatus.RUNNING,
                                      status=ExecutionTask.ExecutionStatus.SCHEDULED)
    # qs = qs.filter(~Q(is_py_func=0))
    all_prev_complete = Q(incoming_edges__task_from__status=ExecutionTask.ExecutionStatus.COMPLETED)
    qs = qs.annotate(incomplete_preconditions=Count('incoming_edges', filter=~all_prev_complete))
    qs = qs.filter(incomplete_preconditions=0)
    return qs


# @celery_core.task
def execute_task_by_id(task_id):
    print("CHECKPOINT 6",task_id)
    db.connections.close_all()
    task = ExecutionTask.objects.filter(task_id=task_id,status=ExecutionTask.ExecutionStatus.SCHEDULED).first()
    print("CHECKPOINT 7", task)
    task.execute()
    print(f"{task} Executed")

def run_executions(qs):
    threads = []
    for task in qs:
        db.connections.close_all()
        print("CHECKPOINT 5")
        p = Process(target=execute_task_by_id,args=(task.task_id,))
        p.start()

def get_completed_running_graphs():
    task_complete = Q(tasks__status__in=[ExecutionTask.ExecutionStatus.COMPLETED,
                                         ExecutionTask.ExecutionStatus.FAILED])
    qs = ExecutionGraph.objects.filter(status=ExecutionGraph.ExecutionStatus.RUNNING)
    qs = qs.annotate(incomplete_children=Count('tasks', filter=~task_complete))
    qs = qs.filter(incomplete_children=0)
    return qs

def proceed():
    print("CHECKPOINT 1")
    #Set status of completed graphs
    db.connections.close_all()
    completed_graphs = get_completed_running_graphs()
    print("CHECKPOINT 2", completed_graphs)
    completed_graphs.update(status=ExecutionGraph.ExecutionStatus.COMPLETED)
    print("CHECKPOINT 3")
    #Execute Available Task
    excuable_tasks = get_excuable_tasks()
    print("CHECKPOINT 4", excuable_tasks)
    run_executions(excuable_tasks)
    # for task in excuable_tasks:
    #     execute_task_by_id(task.task_id)'

def run_proceed():
    db.connections.close_all()
    p = Process(target=proceed)
    p.start()
def execute_graph_by_id(execution_key):
    qs = DAG.objects.filter(execution_key=execution_key)
    for dag in qs:
        dag.execute()


def report_result(success,res,task_id=None):
    try:
        if not task_id:
            task_id = os.environ.get('SCHEDULER_TASK_ID')
        task_id = int(task_id)
        task = ExecutionTask.objects.filter(status=ExecutionTask.ExecutionStatus.RUNNING,task_id=task_id).first()
        assert task
        if success:
            task.handle_success(res)
        else:
            task.handle_error(res)
        return True
    except:
        return False
