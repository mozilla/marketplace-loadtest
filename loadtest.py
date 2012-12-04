import json
import re
import random
import unicodedata

from funkload.FunkLoadTestCase import FunkLoadTestCase

USER_AGENT = 'Mozilla/5.0 (Android; Mobile; rv:18.0) Gecko/18.0 Firefox/18.0'


class MarketplaceTest(FunkLoadTestCase):

    def __init__(self, *args, **kwargs):
        super(MarketplaceTest, self).__init__(*args, **kwargs)

        self.root = self.conf_get('main', 'url')

        # on startup, select one language and a bunch of categories /
        # applications to use when running the test.
        languages = ['en-US', 'pt-BR']
        self.lang = random.choice(languages)

        # select 4 categories and 4 applications out of all of them.
        categories = ('entertainment-sports', u'business', u'games',
            u'music', u'news-weather', u'productivity', 'social',
            u'travel', u'books-reference', u'education', u'health-fitness',
            u'lifestyle', u'photos-media', u'utilities', u'shopping')

        self.categories = random.sample(categories, 4)
        self._apps = None

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
        return super(MarketplaceTest, self).get(self.root + url,
                                                load_auto_links=False,
                                                *args, **kwargs)

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

    def query_index(self):
        self.get('/')

    def query_search(self):
        # make a request that returning all the apps registered in the
        # marketplace.
        self.get('/search/?q=')

        # and then do a search with the name of the selected apps
        for app in self.apps:
            self.get('/search/?q=%s' % app)

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

    def search_app(self):
        # search for some non-empty string, to make a realistic and not
        # too expensive query
        ret = self.get('/search/?q=twi', ok_codes=[200, 503])
        if ret.code == 503:
            self.assertTrue('Search Unavailable' in ret.body)
        else:
            self.assertTrue('Search Results' in ret.body)

    def install_free_app(self):
        # all the logic for free apps is client side - as long as the
        # manifest url is in the page, the process should succeed
        ret = self.get('/app/twitter')
        self.assertTrue('data-manifest_url='
            '"https://mobile.twitter.com/cache/twitter.webapp"' in ret.body)

    def test_marketplace(self):
        if self.in_bench_mode:
            self.query_index()
            self.query_search()
            self.query_categories()
            self.query_apps_detail()
        else:
            self.setHeader('User-Agent', USER_AGENT)
            self.view_homepage()
            self.search_app()
            self.install_free_app()


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
