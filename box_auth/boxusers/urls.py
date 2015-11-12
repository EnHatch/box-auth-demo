from django.conf.urls import patterns, url

from box_auth.boxusers.views import BoxAuth, BoxAuthConfirm

urlpatterns = patterns(
    '',
    # Examples:
    url(regex=r'^auth/$',
        view=BoxAuth.as_view(),
        name='auth'),
    url(regex=r'^auth-confirm/$',
        view=BoxAuthConfirm.as_view(),
        name='auth-confirm'),
)
