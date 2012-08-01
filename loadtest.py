import json
import random

from funkload.FunkLoadTestCase import FunkLoadTestCase


class MarketplaceTest(FunkLoadTestCase):

    def setUp(self):
        self.root = self.conf_get('main', 'root')

        self.languages = ('fr', 'en-US')
        (
            'af', 'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en-US', 'es',
            'eu', 'fa', 'fi', 'fr', 'ga-IE', 'he', 'hu', 'id', 'it', 'ja',
            'ko', 'mn', 'nl', 'pl', 'pt-BR', 'pt-PT', 'ro', 'ru', 'sk', 'sl',
            'sq', 'sv-SE', 'uk', 'vi', 'zh-CN', 'zh-TW',
        )

        self._apps = None

    def get(self, url, *args, **kwargs):
        return super(MarketplaceTest, self).get(self.root + url,
                                                *args, **kwargs)

    def get_all(self, url, *args, **kwargs):
        # Do a request for each defined langauge rather than only one request,
        # and takes care about setting the Accept-Langauge header before
        # issuing the request.
        for lang in self.languages:
            self.setHeader('Accept-Languages', lang)
            self.get(url, load_auto_links=False)

    @property
    def apps(self):
        """Gets the list of projects currently contained in the marketplace
        instance
        """
        if self._apps == None:
            resp = self.get('/en-US/api/apps/search/')
            content = json.loads(resp.body)
            self._apps = [p['slug'] for p in content['objects']]
        return self._apps

    def test_index_page(self):
        self.get_all('/')

    def test_search(self):
        # make a request that returning all the apps registered in the
        # marketplace.
        self.get_all('/search/?q=')

        # get a project randomly from the marketplace and make a research on
        # it.
        self.get_all('/search/?q=%s' % random.choice(self.apps))

    def test_app_detail(self):
        self.get_all('/app/{app}/'.format(app=random.choice(self.apps)))


if __name__ == '__main__':
    import unittest
    unittest.main()
