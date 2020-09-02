from rest_framework import viewsets
from tests.testapp.models import Book, Course, Student
from tests.testapp.serializers import (BookSerializer,
                                       CourseSerializer,
                                       StudentSerializer)

from drf_lighten.views import DynamicFieldsMixin


class BookViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()


class CourseViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()


class StudentViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
