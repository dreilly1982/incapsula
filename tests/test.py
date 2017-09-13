from incapsula import API
import mock
import os
import yaml

incap = API(api_key='key', api_id='id')
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


def test_get_url():
    assert incap.get_url('/action') == 'https://my.incapsula.com/api/prov/v1/action'


@mock.patch('os.path.isfile')
@mock.patch('incapsula.open')
def test_load_cfg(mock_open, mock_isfile):
    mock_isfile.return_value = True
    mock_open.side_effect = [
        mock.mock_open(read_data=config_yaml_one).return_value,
        mock.mock_open(read_data=config_yaml_two).return_value
    ]
    api = API()
    assert api.api_id == 'test_id'
    assert api.api_key == 'test_key'
    assert api.url == 'https://your.incapsula.com/api/prov/v1'
    assert api.ignore_ssl is True
    assert api.ignore_ssl_warnings is True
    mock_open.reset_mock()

    api = API()
    assert api.api_id == 'test_id'
    assert api.api_key == 'test_key'
    assert api.url == 'https://your.incapsula.com/api/prov/v1'
    assert api.ignore_ssl is False
    assert api.ignore_ssl_warnings is False


def test_init():
    api = API(url='https://your.incapsula.com/apb/prov/v1',
              api_id='test_id_a',
              api_key='test_key_a',
              ignore_ssl=True,
              ignore_ssl_warnings=True)

    assert api.api_id == 'test_id_a'
    assert api.api_key == 'test_key_a'
    assert api.url == 'https://your.incapsula.com/apb/prov/v1'
    assert api.ignore_ssl is True
    assert api.ignore_ssl_warnings is True
