from funkload.FunkLoadTestCase import FunkLoadTestCase


class MarketplaceTest(FunkLoadTestCase):

    def setUp(self):
        self.root = self.conf_get('main', 'root')

    def test_index_page(self):
        self.get(self.root, load_auto_links=False)

if __name__ == '__main__':
    import unittest
    unittest.main()
