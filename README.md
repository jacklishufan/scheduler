# Ccheduler
# Definitions
A directed acyclic graph(DAG) is a graph数学公式: $ G(V,E) $with no cycles
Constants
####is_py_func: 
0 offline,
1, python,
2 system
####job_status:
0 schuedled 

1 running 

2 completed 

3 failed

# Schema
## Graph
Representing a template/blueprint of data pipeline
```
{
    "graph_id": 1,
    "name": "test graph",
    "tasks": [
        {
            "task_id": 1,
            "parent": 1, #Foreign Key: Graph
            "name": "Test Task 1",
            "description": "",
            "command": "scheduler.tasks.example_func",
            "is_py_func": 1, 
            "configs": null 
            #Object, if present: {args:[..],kwargs:{key:value..}}
        }, #Task
        ...
    ],
    "execution_key": "default",
    "edges": [
        {
            "task_from": 1, #Foreign Key Task
            "task_to": 2
        } #Edge
    ],
    "last_launched": "2021-04-16T06:50:31.520896Z"
}
```
## Execution Graph
Representing an executable copy of Graph, with additional runtime information.
```
{
    "graph_id": 4,
    "name": "test graph",
    "dag": 1, #Foreign Key: Graph,
    "status": 2, 
    "tasks": [
        {
            "task_id": 6,
            "parent": 4,#Foreign Key: Execution Graph
            "name": "Test Task 1",
            "description": "",
            "command": "scheduler.tasks.example_func",
            "configs": null,#Object 
            "results": {
                "result": {
                    "res": "Test data"
                }
            }, #Object
            "is_py_func": 1,
            "errors": null, #Object 
            "status": 2, 
            "start_time": "2021-04-16T06:57:59.096423Z",
            "end_time": "2021-04-16T06:57:59.108513Z"
        },
        ...
    ],
    "edges": [
        {
            "task_from": 6,
            "task_to": 7
        }
    ],
    "launch_time": "2021-04-16T06:50:31.528477Z"
   }
```
##APIS

Examples and specs TBC.

### DAG

dag/list/ GET

dag/create/ POST

dag/<int:id>/ GET POST DELETE


### Edge

edge/create/ POST

edge/<int:id>/  GET POST DELETE

### Tasks

task/create/ POST

task/<int:id>/ GET POST DELETE

### Execution 

execution/list/ GET

execution/<int:pk>/ GET POST DELETE

execution/<int:pk>/cancel/ POST

execution/report-by-key/<str:key>/
```
EXAMPLE POST scheduler/execution/report-by-key/engagement_upload/'
{"success":True,
"result":{
    "number":10232
}
}
```

execution/tasks/<int:pk>/ GET

execution/tasks/<int:pk>/report/ POST

