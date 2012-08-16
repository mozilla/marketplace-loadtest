import json
import re
import random
import unicodedata

from funkload.FunkLoadTestCase import FunkLoadTestCase


class MarketplaceTest(FunkLoadTestCase):

    def __init__(self, *args, **kwargs):
        super(MarketplaceTest, self).__init__(*args, **kwargs)

        self.root = self.conf_get('main', 'url')

        # on startup, select one language and a bunch of categories /
        # applications to use when running the test.
        languages = [
            'af', 'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'es',
            'eu', 'fa', 'fi', 'fr', 'ga-IE', 'he', 'hu', 'id', 'it', 'ja',
            'ko', 'mn', 'nl', 'pl', 'pt-BR', 'pt-PT', 'ro', 'ru', 'sk', 'sl',
            'sq', 'sv-SE', 'uk', 'vi', 'zh-CN', 'zh-TW']

        # consider that 50% of the traffic is english.
        languages.extend(('en-US',) * int(0.5 * (len(languages) + 1)))
        self.lang = random.choice(languages)
        self.logger.info('Language: "%s"' % self.lang)

        # select 4 categories and 4 applicatoins out of all of them.
        categories = ('entertainment-sports', u'business', u'games',
            u'music', u'news-weather', u'productivity', 'social',
            u'travel', u'books-reference', u'education', u'health-fitness',
            u'lifestyle', u'photos-media', u'utilities', u'shopping')

        self.categories = random.sample(categories, 4)

        self.logger.info('categories: "%s"' % ', '.join(self.categories))

        apps = self.get_apps()
        self.apps = random.sample(apps, 4)
        self.logger.info('apps: "%s"' % ', '.join(self.apps))

    def get(self, url, *args, **kwargs):
        """Do a GET request with the given URL.

        This call sets the Accept-Languages header and ask funkload to now
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

    def get_apps(self):
        """Get the list of apps from the marketplace API"""
        resp = self.get('/en-US/api/apps/search/')
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

    def test_marketplace(self):
        self.query_index()
        self.query_search()
        self.query_categories()
        self.query_apps_detail()


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
