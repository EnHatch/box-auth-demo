from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns(
    '',
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^box/', include('box_auth.boxusers.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
