import json
import re
import unicodedata

from funkload.FunkLoadTestCase import FunkLoadTestCase


class MarketplaceTest(FunkLoadTestCase):

    def __init__(self, *args, **kwargs):
        self.root = self.conf_get('main', 'url')

        self.languages = (
            'af', 'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'en-US', 'es',
            'eu', 'fa', 'fi', 'fr', 'ga-IE', 'he', 'hu', 'id', 'it', 'ja',
            'ko', 'mn', 'nl', 'pl', 'pt-BR', 'pt-PT', 'ro', 'ru', 'sk', 'sl',
            'sq', 'sv-SE', 'uk', 'vi', 'zh-CN', 'zh-TW',
        )

        self._apps = None
        self._categories = None

    def get(self, url, *args, **kwargs):
        return super(MarketplaceTest, self).get(self.root + url,
                                                load_auto_links=False,
                                                *args, **kwargs)

    def get_all(self, url, *args, **kwargs):
        # Do a request for each defined langauge rather than only one request,
        # and takes care about setting the Accept-Langauge header before
        # issuing the request.
        for lang in self.languages:
            self.setHeader('Accept-Languages', lang)
            self.get(url)

    @property
    def apps(self):
        """Gets the list of projects currently contained in the marketplace
        instance
        """
        if not self._apps:
            resp = self.get('/en-US/api/apps/search/')
            content = json.loads(resp.body)
            self._apps = [p['slug'] for p in content['objects']]
        return self._apps

    @property
    def categories(self):
        """Gets all the categories from the marketplace"""
        if not self._categories:
            resp = self.get('/en-US/api/apps/category/')
            cats = json.loads(resp.body)['objects']
            self._categories = [slugify(c['name']) for c in cats]
        return self._categories

    def test_index(self):
        self.get_all('/')

    def test_everything(self):
        self.test_index()
        self.test_search()
        self.test_category()
        self.test_app_detail()

    def test_search(self):
        # make a request that returning all the apps registered in the
        # marketplace.
        self.get_all('/search/?q=')

        self.get_all('/search/?q=%s' % self.apps[0])

    def test_app_detail(self):
        self.get_all('/app/{app}/'.format(app=self.apps[0]))

    def test_category(self):
        self.get_all('/apps/{category}'.format(category=self.categories[0]))


def slugify(value):
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
