# DRF Lighten
[![PyPI version](https://badge.fury.io/py/drf_lighten.svg)](https://badge.fury.io/py/drf_lighten)
[![Maintainability](https://api.codeclimate.com/v1/badges/fb7592cf34907b7cb8d8/maintainability)](https://codeclimate.com/github/jupi2142/drf_lighten/maintainability)
![python3.x](https://img.shields.io/badge/python-3.x-brightgreen.svg)
![python2.x](https://img.shields.io/badge/python-2.x-brightgreen.svg)

## Purpose
Even if we call the same end point at multiple places, the information we want
from the response varies greatly. DRF Lighten makes it possible to specify and
get only the data you want.


## Installation
`pip install drf_lighten`


## Usage
```python
# serializers.py
from app import models
from drf_lighten.serializers import DynamicFieldsMixin
from rest_framework import serializers


class UserSerializer(DynamicFieldsMixin,
                     serializers.HyperlinkedModelSerializer)
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
      "user_name": "jupi2142",
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

`https://localhost:8000/profiles/?fields=["url", "picture", {"user": ["url", "username"]}]`
```json
[
  {
    "url": "https://localhost:8000/profiles/22/",
    "picture": "https://localhost:8000/media/22.jpg",
    "user": {
      "url": "https://localhost:8000/users/22/",
      "user_name": "jupi2142"
    }
  }
]
```


## Configuration
If you want to use different query params than the ones provided, you can go to your django project's settings and do that

```python
DRF_LIGHTEN_INCLUDE = 'fields'
DRF_LIGHTEN_EXCLUDE = 'exclude'
```
