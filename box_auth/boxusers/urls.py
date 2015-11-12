from django.conf.urls import patterns, url

from box_auth.boxusers import views

urlpatterns = patterns(
    '',
    # Examples:
    url(regex=r'^auth$',
        view=views.BoxAuth.as_view(),
        name='auth'),
    url(regex=r'^auth-confirm$',
        view=views.BoxAuthConfirm.as_view(),
        name='auth-confirm'),
)
