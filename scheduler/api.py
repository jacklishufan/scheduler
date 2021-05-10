from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import mixins
from rest_framework.response import Response
from .serializers import *
from .utils import *

class DAGCreateView(generics.CreateAPIView):
    serializer_class = DAGSerializer
    queryset = DAG.objects.all()

class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

class TaskEdgeCreateView(generics.CreateAPIView):
    serializer_class = TaskEdgeSerializer
    queryset = TaskEdge.objects.all()

class CRUDMixin(mixins.UpdateModelMixin, mixins.RetrieveModelMixin,):
    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.partial_update(self, request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.delete()
        return Response("Success")


class RetriveMixin(mixins.RetrieveModelMixin):
    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)


class DAGUpdateView(CRUDMixin,generics.GenericAPIView):
    serializer_class = DAGSerializer
    queryset = DAG.objects.all()

class TaskUpdateView(CRUDMixin, generics.GenericAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


class TaskEdgeUpdateView(CRUDMixin, generics.GenericAPIView):
    serializer_class = TaskEdgeSerializer
    queryset = TaskEdge.objects.all()

class DAGExecuteView(generics.GenericAPIView):
    serializer_class = DAGSerializer
    queryset = DAG.objects.all()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.execute()
        return Response("Success")

class DAGListView(generics.ListAPIView):
    serializer_class = DAGListSerializer
    queryset = DAG.objects.all()

    def get_queryset(self):
        return DAG.objects.all()


class ExecutionGraphListView(generics.ListAPIView):
    serializer_class = ExecutionListSerializer
    queryset = ExecutionGraph.objects.all()

    def get_queryset(self):
        return ExecutionGraph.objects.all()


class ExecutionRetrievelView(RetriveMixin,generics.GenericAPIView):
    serializer_class = ExecutionGraphSerializer
    queryset = ExecutionGraph.objects.all()



class ExecutionCancelView(generics.GenericAPIView):
    serializer_class = ExecutionGraphSerializer
    queryset = ExecutionGraph.objects.all()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        obj.cancel()
        return Response("Success")


class ExecutionTaskUpdateView(CRUDMixin,generics.GenericAPIView):
    serializer_class = ExecutionTaskSerializer
    queryset = ExecutionTask.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.partial_update(self, request, *args, **kwargs)

class ExecutionTaskReportView(CRUDMixin, generics.GenericAPIView):
    serializer_class = ExecutionTaskSerializer
    queryset = ExecutionTask.objects.all()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        success = request.data.get('success') or False
        result = request.data.get('result') or {}
        if success:
            obj.handle_success(result)
        else:
            obj.handle_error(result)
        return Response("Success")


class ExecutionTaskReportByKeyView(CRUDMixin, generics.GenericAPIView):
    serializer_class = ExecutionTaskSerializer
    queryset = ExecutionTask.objects.all()

    def get_object(self):
        kwargs = self.kwargs
        key = kwargs.get('key','')
        if not key:
            raise generics.Http404
        qs = ExecutionTask.objects.filter(status=ExecutionTask.ExecutionStatus.RUNNING,key=key)
        qs = qs.order_by('-start_time')
        obj = qs.first()
        if not obj:
            raise generics.Http404
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        success = request.data.get('success') or False
        result = request.data.get('result') or {}
        if success:
            obj.handle_success(result)
        else:
            obj.handle_error(result)
        return Response("Success")

class ExecuteTaskByKeyView(APIView):

    def post(self, request, *args, **kwargs):
        key = request.data.get('key')
        if key:
            execute_graph_by_id(key)
            return Response("Success")
        else:
            return Response("No Key Provided")
        # return self.partial_update(self, request, *args, **kwargs)
