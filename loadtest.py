import base64
import json
import random
import re
import unicodedata

from funkload.FunkLoadTestCase import FunkLoadTestCase

from util import read_password

USER_AGENT = 'Mozilla/5.0 (Android; Mobile; rv:18.0) Gecko/18.0 Firefox/18.0'
CSRF_REGEX = re.compile(r'.*csrfmiddlewaretoken\' value=\'(.*)\'')
WEBAPP = 'http://mozilla-services.github.com/ha-test-web-app/manifest.webapp'


class MarketplaceTest(FunkLoadTestCase):

    def __init__(self, *args, **kwargs):
        super(MarketplaceTest, self).__init__(*args, **kwargs)

        self.root = self.conf_get('main', 'url')
        self.lang = 'en-US'

        # on startup, select a bunch of categories /
        # applications to use when running the test.
        # select 4 categories and 4 applications out of all of them.
        categories = ('entertainment-sports', u'business', u'games',
            u'music', u'news-weather', u'productivity', 'social',
            u'travel', u'books-reference', u'education', u'health-fitness',
            u'lifestyle', u'photos-media', u'utilities', u'shopping')

        self.categories = random.sample(categories, 4)
        self._apps = None

    def setBasicAuth(self, username, password):
        '''Set the Basic authentication information to the given username
        and password.
        '''
        self._browser.authinfo = base64.b64encode('%s:%s' % (username,
            password)).strip()
        self._authinfo = '%s:%s@' % (username, password)

    def get(self, url, *args, **kwargs):
        """Do a GET request with the given URL.

        This call sets the Accept-Languages header and ask funkload to not
        follow img/css/js links.
        """
        # when GETing an URL, we don't want to follow the links (img, css etc)
        # as they could be done on the fly by javascript in an obstrusive way.
        # we also prepend the domain (self.root) to the get calls in this
        # method.
        self.setHeader('Accept-Languages', self.lang)
        self.setHeader('User-Agent', USER_AGENT)
        return super(MarketplaceTest, self).get(self.root + url,
                                                load_auto_links=False,
                                                *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return super(MarketplaceTest, self).post(self.root + url,
            load_auto_links=False, *args, **kwargs)

    @property
    def apps(self):
        if self._apps is None:
            self._apps = random.sample(self.get_apps(), 4)
        return self._apps

    def get_apps(self):
        """Get the list of apps from the marketplace API"""
        resp = self.get('/api/apps/search/')
        content = json.loads(resp.body)
        return [p['slug'] for p in content['objects']]

    def get_categories(self):
        """Get all the categories from the marketplace API"""
        resp = self.get('/en-US/api/apps/category/')
        cats = json.loads(resp.body)['objects']
        return [slugify(c['name']) for c in cats]

    def query_search(self):
        # do a search with the name of the selected apps
        for app in self.apps:
            self.search_app(query=app)

    def query_apps_detail(self):
        for app in self.apps:
            self.get('/app/{app}/'.format(app=app))

    def query_categories(self):
        for category in self.categories:
            self.get('/apps/{category}'.format(category=category))

    def view_homepage(self):
        ret = self.get('/')
        self.assertTrue('Categories' in ret.body)
        self.assertTrue('Games' in ret.body)

    def search_app(self, query='twi'):
        # search for some non-empty string, to make a realistic and not
        # too expensive query
        ret = self.get('/search/?q=%s' % query, ok_codes=[200, 503])
        if ret.code == 503:
            self.assertTrue('Search Unavailable' in ret.body)
        else:
            self.assertTrue('Search Results' in ret.body)
        self.assertEqual(ret.code, 200)

    def install_free_app(self):
        # all the logic for free apps is client side - as long as the
        # manifest url is in the page, the process should succeed
        ret = self.get('/app/twitter')
        self.assertTrue('data-manifest_url='
            '"https://mobile.twitter.com/cache/twitter.webapp"' in ret.body)

    def submit_app(self):
        self.setBasicAuth('developer@mozilla.com', read_password())
        # check logged-in view
        ret = self.get('/')
        # try to submit an app
        ret = self.get('/developers/submit/app', ok_codes=[200, 302])

        # we need to accept the TOS once per user
        if 'read_dev_agreement' in ret.body:
            params = [['read_dev_agreement', 'True']]
            add_csrf_token(ret, params)
            ret = self.post(ret.url, params=params)
        # submit the manifest
        params = [['manifest', WEBAPP]]
        add_csrf_token(ret, params)
        ret = self.post('/developers/upload-manifest', params=params)
        data = json.loads(ret.body)
        self.assertEqual(data['validation']['errors'], 0, data)
        # now we can submit the app basics, first load the form again
        ret = self.get('/developers/submit/app/manifest')
        params = [['upload', data['upload']],
                  ['free', 'free-os'],
                  ['free', 'free-desktop'],
                  ['free', 'free-phone'],
                  ['free', 'free-tablet']]
        add_csrf_token(ret, params)
        ret = self.post('/developers/submit/app/manifest', params=params)
        self.assertTrue('/mozilla-ha-test-web-app' in ret.url, ret.url)

    def test_marketplace(self):
        self.view_homepage()
        self.search_app()
        self.install_free_app()
        try:
            self.submit_app()
        finally:
            self.clearBasicAuth()

        # generate some more random load
        self.query_search()
        self.query_categories()
        self.query_apps_detail()


def add_csrf_token(response, params):
    token = CSRF_REGEX.findall(response.body)
    if token:
        params.append(['csrfmiddlewaretoken', token[0]])


def slugify(value):
    """This is the slugify from django, minus an hardcoded workaround"""
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    slugified = re.sub('[-\s]+', '-', value)

    # workaround for now
    if slugified == 'social-communications':
        return 'social'
    return slugified


if __name__ == '__main__':
    import unittest
    unittest.main()
