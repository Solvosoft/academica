from async_notifications.models import NewsLetter, NewsLetterTask
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import NewsLetterTaskSerializer, NewsLetterTaskListSerializer


class NewsLetterTaskView(APIView):

    def post(self, request, pk, format=None):
        news_letter = get_object_or_404(NewsLetter, pk=pk)
        serializer = NewsLetterTaskSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(template=news_letter)
            serializer = NewsLetterTaskListSerializer(NewsLetterTask.objects.filter(template=news_letter), many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        news_letter = get_object_or_404(NewsLetter, pk=pk)
        if 'delitems[]' in request.data:
            del_items = request.data.getlist('delitems[]', [])
        else:
            del_items = []
        tipos = NewsLetterTask.objects.filter(template=news_letter, pk__in=del_items)
        tipos.delete()
        serializer = NewsLetterTaskListSerializer(NewsLetterTask.objects.filter(template=news_letter), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)