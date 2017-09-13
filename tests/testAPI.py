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
        self.assertEqual(payload['ips'],
                         '198.51.100.0/32,198.51.100.2/31,198.51.100.4/30,'
                         '198.51.100.8/29,198.51.100.16/28,198.51.100.32/27,'
                         '198.51.100.64/26,198.51.100.128/25')

