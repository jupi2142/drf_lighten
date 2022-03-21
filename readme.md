# DRF Lighten
[![PyPI version](https://badge.fury.io/py/drf_lighten.svg)](https://badge.fury.io/py/drf_lighten)
[![Maintainability](https://api.codeclimate.com/v1/badges/fb7592cf34907b7cb8d8/maintainability)](https://codeclimate.com/github/jupi2142/drf_lighten/maintainability)
![python3.x](https://img.shields.io/badge/python-3.x-brightgreen.svg)


DRF Lighten is a Django REST Framework package that lets you modify the structure of your DRF serializer, and nested serializers inside it.

Cool things
* Select a subset of the data returned per request using query parameters
* Option to define structure using one query parameter (`?struct`), or two parameters (`?fields=...&exclude`)
* Select a subset of the fields using arguments to the serializer, including nested serializers
* Parser API
  * Decouples schema definition language and schema definition API
  * Lets you define whatever custom syntax you want for the schema definition
* Select from various syntaxes for the query parameters
  * GraphQL-Like (Default)  (e.g., `?fields={id,picture,user{url,username}}`) 
  * JSON (e.g., `?fields=["id", "picture", {"user": ["url", "username"]}]`)
  * Dot (e.g., `?fields=id,picture,user.url,user.username`)
  * Custom (Using the Parser API)
* Nested serializers need not use DRF lighten for their fields to included or excluded


## Installation
`pip install drf_lighten`


## Examples
`https://localhost:8000/profiles/`
```json
[
  {
    "url": "https://localhost:8000/profiles/22/",
    "picture": "https://localhost:8000/media/22.jpg",
    "phone_number": "+251-911-11-11-11",
    "user": {
      "url": "https://localhost:8000/users/22/",
      "username": "jupi2142",
      "email": "test@gmail.com",
      "first_name": "Henock",
      "last_name": "Tesfaye"
    },
    "posts": [
      "https://localhost:8000/posts/77/",
      "https://localhost:8000/posts/78/",
      "https://localhost:8000/posts/79/",
      "https://localhost:8000/posts/79/",
      "https://localhost:8000/posts/99/"
    ]
  }
]
```

`https://localhost:8000/profiles/?struct={url,picture,-user{email}}`
```json
[
  {
    "url": "https://localhost:8000/profiles/22/",
    "picture": "https://localhost:8000/media/22.jpg",
    "user": {
      "url": "https://localhost:8000/users/22/",
      "username": "jupi2142",
      "first_name": "Henock",
      "last_name": "Tesfaye"
    }
  }
]
```

## Usage
```python
# models.py
from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='posts')
    content = models.TextField()


class Profile(models.Model):
    picture = models.FileField()
    phone_number = models.CharField(max_length=20)
    user = models.OneToOneField(User, on_delete=models.PROTECT)


# serializers.py
from app import models
from drf_lighten.serializers import DynamicFieldsMixin
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer)
    class Meta:
        model = models.User
        fields = "__all__"


class ProfileSerializer(DynamicFieldsMixin,
                        serializers.HyperlinkedModelSerializer)
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Profile
        fields = "__all__"


# views.py
from app import models
from drf_lighten.views import DynamicFieldsMixin
from rest_framework import viewsets


# …

class ProfileViewSet(DynamicFieldsMixin, viewsets.ModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

```



## Configuration
If you want to use different query params than the ones provided, you can go to your django project's settings and do that

```python
DRF_LIGHTEN_INCLUDE = 'fields'
DRF_LIGHTEN_EXCLUDE = 'exclude'
DRF_LIGHTEN_STRUCTURE = 'struct'
```
