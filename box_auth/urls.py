from django.conf.urls import patterns, include, url
from django.contrib import admin
from box_auth.boxusers.views import HomeView, DownloadView

urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^download$', DownloadView.as_view(), name='download'),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^box/', include('box_auth.boxusers.urls', namespace='box')),
    url(r'^admin/', include(admin.site.urls)),
)
