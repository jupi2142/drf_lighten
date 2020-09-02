from rest_framework import serializers
from tests.testapp.models import Book, Course, Phone, Student

from drf_lighten.serializers import DynamicFieldsMixin


class BookSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class CourseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class PhoneSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = '__all__'


class StudentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    course = CourseSerializer(many=False, read_only=True)
    phone_numbers = PhoneSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = '__all__'
