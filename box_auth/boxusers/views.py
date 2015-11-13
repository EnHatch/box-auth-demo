from __future__ import unicode_literals
from redis import StrictRedis
from redis.lock import Lock
from uuid import uuid4
from boxsdk import OAuth2, Client


from django.views.generic.base import RedirectView, TemplateView

# from boxsdk import OAuth2
# from boxsdk.auth.redis_managed_oauth2 import RedisManagedOAuth2

from box_auth.boxusers.models import BoxUser


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, *args, **kwargs):
        if 'boxuser' not in kwargs and BoxUser.objects.count():
            boxuser = BoxUser.objects.filter()[0]
            oauth = RedisManagedOAuth2(
                client_id='5dn98104cyf535v4581cbb1wxnag6e5y',
                client_secret='8z6ysMEnsrickMWBwpnysxYJ9SvqaNlY',
                unique_id=boxuser.unique_id
            )
            client = Client(oauth)
            me = client.user(user_id='me').get()
            kwargs['boxuser'] = me

        super(HomeView, self).get_context_data(*args, **kwargs)


# def store_tokens(access_token, refresh_token, clear_csrf=False):
#     count = BoxUser.objects.count()
#     if count == 0:
#         boxuser = BoxUser.objects.create(
#             access_token=access_token, refresh_token=refresh_token)
#     else:
#         boxuser = BoxUser.objects.filter()[0]
#         boxuser.access_token = access_token
#         boxuser.refresh_token = refresh_token
#         if clear_csrf:
#             boxuser.csrf_token = ''
#         boxuser.save()


class BoxAuth(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):

        oauth = RedisManagedOAuth2(
            client_id='5dn98104cyf535v4581cbb1wxnag6e5y',
            client_secret='8z6ysMEnsrickMWBwpnysxYJ9SvqaNlY',
        )

        auth_url, csrf_token = oauth.get_authorization_url(
            'https://enhatch-box-auth-demo.herokuapp.com/box/auth-confirm/')
        self._create_box_user(csrf_token, oauth.unique_id)

        return auth_url

    def _create_box_user(self, csrf_token, unique_id):
        BoxUser.objects.create(
            csrf_token=csrf_token,
            unique_id=unique_id)

    # def _store_box_user(self, csrf_token, unique_id):
    #     count = BoxUser.objects.count()
    #     if count == 0:
    #         boxuser = BoxUser.objects.create(
    #             csrf_token=csrf_token,
    #             unique_id=unique_id)
    #     else:
    #         boxuser = BoxUser.objects.filter()[0]
    #         boxuser.csrf_token = csrf_token
    #         boxuser.unique_id = unique_id
    #         boxuser.save()


class BoxAuthConfirm(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        state = self.request.GET.get('state')
        code = self.request.GET.get('code')

        boxuser = BoxUser.objects.filter('-created')[0]
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

# TEMP


class RedisManagedOAuth2(OAuth2):
    """
    Box SDK OAuth2 subclass.
    Allows for storing auth tokens in redis.

    :param unique_id:
        An identifier for this auth object. Auth instances which wish to share
        tokens must use the same ID.
    :type unique_id:
        `unicode`
    :param redis_server:
        An instance of a Redis server, configured to talk to Redis.
    :type redis_server:
        :class:`Redis`
    """
    def __init__(self, unique_id=uuid4(), redis_server=None, *args, **kwargs):
        import os
        import urlparse
        self._unique_id = unique_id
        redis_url = urlparse.urlparse(
            os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'))
        self._redis_server = redis_server or StrictRedis(
            host=redis_url.hostname, port=redis_url.port,
            password=redis_url.password, db=0)
        refresh_lock = Lock(
            redis=self._redis_server,
            name='{0}_lock'.format(self._unique_id))
        super(RedisManagedOAuth2, self).__init__(
            *args, refresh_lock=refresh_lock, **kwargs)
        if self._access_token is None:
            self._update_current_tokens()

    def _update_current_tokens(self):
        """
        Get the latest tokens from redis and store them.
        """
        print self._redis_server
        self._access_token, self._refresh_token = self._redis_server.hvals(
            self._unique_id) or (None, None)

    @property
    def unique_id(self):
        """
        Get the unique ID used by this auth instance. Other instances can
        share tokens with this instance if they share the ID with this
        instance.
        """
        return self._unique_id

    def _get_tokens(self):
        """
        Base class override.
        Gets the latest tokens from redis before returning them.
        """
        self._update_current_tokens()
        return super(RedisManagedOAuth2, self)._get_tokens()

    def _store_tokens(self, access_token, refresh_token):
        """
        Base class override.
        Saves the refreshed tokens in redis.
        """
        super(RedisManagedOAuth2, self)._store_tokens(
            access_token, refresh_token)
        self._redis_server.hmset(
            self._unique_id,
            {'access': access_token, 'refresh': refresh_token})
