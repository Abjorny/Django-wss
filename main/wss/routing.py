from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"^ws/api/get_image$", consumers.Camera.as_asgi()),
]
