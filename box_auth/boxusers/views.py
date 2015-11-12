from django.views.generic.base import RedirectView

from boxsdk import OAuth2

from box_auth.boxusers.models import BoxUser


def store_tokens(self, access_token, refresh_token):
    count = BoxUser.objects.count()
    if count == 0:
        boxuser = BoxUser.objects.create(
            access_token=access_token, refresh_token=refresh_token)
    else:
        boxuser = BoxUser.objects.filter()[0]
        boxuser.access_token = access_token
        boxuser.refresh_token = refresh_token
        boxuser.save()


class BoxAuth(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):

        oauth = OAuth2(
            client_id='5dn98104cyf535v4581cbb1wxnag6e5y',
            client_secret='8z6ysMEnsrickMWBwpnysxYJ9SvqaNlY',
            store_tokens=store_tokens,
        )

        auth_url, csrf_token = oauth.get_authorization_url(
            'https://enhatch-box-auth-demo.herokuapp.com/box/auth-confirm/')
        self._store_csrf(csrf_token)

        return auth_url

    def _store_csrf(self, csrf_token):
        count = BoxUser.objects.count()
        if count == 0:
            boxuser = BoxUser.objects.create(
                csrf_token=csrf_token)
        else:
            boxuser = BoxUser.objects.filter()[0]
            boxuser.csrf_token = csrf_token
            boxuser.save()


class BoxAuthConfirm(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        state = self.request.GET.get('state')
        code = self.request.GET.get('code')

        oauth = OAuth2(
            client_id='5dn98104cyf535v4581cbb1wxnag6e5y',
            client_secret='8z6ysMEnsrickMWBwpnysxYJ9SvqaNlY'
        )

        csrf_token = BoxUser.objects.filter()[0].csrf_token
        assert state == csrf_token
        access_token, refresh_token = oauth.authenticate(code)
        store_tokens(access_token, refresh_token)

        return '/'
