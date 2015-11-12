from django.views.generic.base import RedirectView

from boxsdk import RedisManagedOAuth2

from box_auth.boxusers.models import BoxUser


def store_tokens(access_token, refresh_token, clear_csrf=False):
    count = BoxUser.objects.count()
    if count == 0:
        boxuser = BoxUser.objects.create(
            access_token=access_token, refresh_token=refresh_token)
    else:
        boxuser = BoxUser.objects.filter()[0]
        boxuser.access_token = access_token
        boxuser.refresh_token = refresh_token
        if clear_csrf:
            boxuser.csrf_token = ''
        boxuser.save()


class BoxAuth(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):

        oauth = RedisManagedOAuth2(
            client_id='5dn98104cyf535v4581cbb1wxnag6e5y',
            client_secret='8z6ysMEnsrickMWBwpnysxYJ9SvqaNlY'
        )

        auth_url, csrf_token = oauth.get_authorization_url(
            'https://enhatch-box-auth-demo.herokuapp.com/box/auth-confirm/')
        self._store_csrf(csrf_token, oauth.unique_id)

        return auth_url

    def _store_box_user(self, csrf_token, unique_id):
        count = BoxUser.objects.count()
        if count == 0:
            boxuser = BoxUser.objects.create(
                csrf_token=csrf_token,
                unique_id=unique_id)
        else:
            boxuser = BoxUser.objects.filter()[0]
            boxuser.csrf_token = csrf_token
            boxuser.unique_id = unique_id
            boxuser.save()


class BoxAuthConfirm(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        state = self.request.GET.get('state')
        code = self.request.GET.get('code')

        boxuser = BoxUser.objects.filter()[0]
        csrf_token = boxuser.csrf_token
        unique_id = boxuser.unique_id

        oauth = RedisManagedOAuth2(
            client_id='5dn98104cyf535v4581cbb1wxnag6e5y',
            client_secret='8z6ysMEnsrickMWBwpnysxYJ9SvqaNlY',
            unique_id=unique_id
        )

        assert state == csrf_token
        access_token, refresh_token = oauth.authenticate(code)

        # store_tokens(
        #     oauth.unique_id, access_token, refresh_token)

        return '/'
