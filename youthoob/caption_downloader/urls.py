from django.conf.urls import url
from . import views

#app_name = 'caption_downloader'

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^indexer', views.indexer, name = 'indexer'),
    url(r'^auth', views.build_token, name='auth'),
    url(r'^timestamp_return', views.timestamp_return, name='timestamp_return'),    
    url(r'^translate', views.translate, name='translate'),    
]
