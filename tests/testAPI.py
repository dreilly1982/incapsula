import unittest
from incapsula import API
import mock
from tests.mocks import mocked_requests_post

config_yaml_one = """
url: https://your.incapsula.com/api/prov/v1
api_key: test_key
api_id: test_id
ssl:
    ignore_ssl: true
    ignore_ssl_warnings: true
"""

config_yaml_two = """
url: https://your.incapsula.com/api/prov/v1
api_key: test_key
api_id: test_id
"""


class TestAPI(unittest.TestCase):

    def test_get_url(self):
        incap = API(api_key='key', api_id='id')
        self.assertEqual(incap.get_url('/action'), 'https://my.incapsula.com/api/prov/v1/action')

    @mock.patch('os.path.isfile')
    @mock.patch('incapsula.open')
    def test_load_cfg(self, mock_open, mock_isfile):
        mock_isfile.return_value = True
        mock_open.side_effect = [
            mock.mock_open(read_data=config_yaml_one).return_value,
            mock.mock_open(read_data=config_yaml_two).return_value
        ]
        api = API()
        self.assertEqual(api.api_id, 'test_id')
        self.assertEqual(api.api_key, 'test_key')
        self.assertEqual(api.url, 'https://your.incapsula.com/api/prov/v1')
        self.assertTrue(api.ignore_ssl)
        self.assertTrue(api.ignore_ssl_warnings)
        mock_open.reset_mock()

        api = API()
        self.assertEqual(api.api_id, 'test_id')
        self.assertEqual(api.api_key, 'test_key')
        self.assertEqual(api.url, 'https://your.incapsula.com/api/prov/v1')
        self.assertFalse(api.ignore_ssl)
        self.assertFalse(api.ignore_ssl_warnings)

    def test_init(self):
        api = API(url='https://your.incapsula.com/apb/prov/v1',
                  api_id='test_id_a',
                  api_key='test_key_a',
                  ignore_ssl=True,
                  ignore_ssl_warnings=True)

        self.assertEqual(api.api_id, 'test_id_a')
        self.assertEqual(api.api_key, 'test_key_a')
        self.assertEqual(api.url, 'https://your.incapsula.com/apb/prov/v1')
        self.assertTrue(api.ignore_ssl)
        self.assertTrue(api.ignore_ssl_warnings)

    @mock.patch('requests.Session.post')
    def test_get_sites(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API(api_key='key', api_id='id')
        with self.assertRaisesRegexp(Exception,
                                     'Authentication missing or invalid'):
            api.get_sites()

        api = API(api_key='test_key', api_id='test_id')
        resp = api.get_sites()
        self.assertEqual(resp['res_message'], 'OK')
        self.assertEqual(resp['sites'][0]['site_id'], 1234567)

    @mock.patch('requests.Session.post')
    def test_add_ip_to_blacklist(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API()
        payload = api.add_ip_to_blacklist(1234567, '192.0.2.3')
        self.assertEqual(payload['ips'], '192.0.2.3/32,198.51.100.0/24')

    @mock.patch('requests.Session.post')
    def test_remove_ip_from_blacklist(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API()
        payload = api.remove_ip_from_blacklist(1234567, '198.51.100.1')
        self.assertEqual(payload['rule_id'], 'api.acl.blacklisted_ips')
        self.assertEqual(payload['site_id'], 1234567)
        self.assertEqual(payload['ips'],
                         '198.51.100.0/32,198.51.100.2/31,198.51.100.4/30,'
                         '198.51.100.8/29,198.51.100.16/28,198.51.100.32/27,'
                         '198.51.100.64/26,198.51.100.128/25')

    @mock.patch('requests.Session.post')
    def test_send_request(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API(url='https://superbeef.com')
        with self.assertRaisesRegexp(Exception, 'POST https://superbeef.com/sites/list/ 404'):
            api.get_sites()

    @mock.patch('requests.Session.post')
    def test_get_site_acl(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API(url='noacl')
        self.assertEqual(api.get_site_acl(1234567), None)

    @mock.patch('requests.Session.post')
    def test_add_ip_to_whitelist(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API()
        payload = api.add_ip_to_whitelist(1234567, '192.0.2.3')
        self.assertEqual(payload['ips'], '192.0.2.3/32,203.0.113.0/24')

    @mock.patch('requests.Session.post')
    def test_remove_ip_from_whitelist(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API()
        payload = api.remove_ip_from_whitelist(1234567, '203.0.113.1')
        self.assertEqual(payload['rule_id'], 'api.acl.whitelisted_ips')
        self.assertEqual(payload['site_id'], 1234567)
        self.assertEqual(payload['ips'],
                         '203.0.113.0/32,203.0.113.2/31,203.0.113.4/30,'
                         '203.0.113.8/29,203.0.113.16/28,203.0.113.32/27,'
                         '203.0.113.64/26,203.0.113.128/25')

    @mock.patch('requests.Session.post')
    def test_get_black_white_list(self, mock_post):
        mock_post.side_effect = mocked_requests_post
        api = API(url='nobwl')
        self.assertEqual(api.get_site_blacklisted_ips(1234567), None)
        self.assertEqual(api.get_site_blacklisted_urls(1234567), None)
        self.assertEqual(api.get_site_blacklisted_countries(1234567), None)
        self.assertEqual(api.get_site_whitelisted_ips(1234567), None)
