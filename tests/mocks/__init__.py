import json


def mocked_requests_post(*args, **kwargs):
    with open('tests/fixtures/bad_auth.json', 'r') as f:
        bad_auth = json.load(f)

    with open('tests/fixtures/list_sites.json', 'r') as f:
        list_sites = json.load(f)

    with open('tests/fixtures/site_status.json', 'r') as f:
        site_status = json.load(f)

    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/list' \
            and kwargs['data']['api_key'] == 'key' \
            and kwargs['data']['api_id'] == 'id':
        return MockResponse(bad_auth, 200)
    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/list' \
            and kwargs['data']['api_key'] == 'test_key' \
            and kwargs['data']['api_id'] == 'test_id':
        return MockResponse(list_sites, 200)
    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/status':
        return MockResponse(site_status, 200)
    if args[0] == 'https://my.incapsula.com/api/prov/v1/sites/configure/acl':
        kwargs['data']['res_message'] = 'OK'
        return MockResponse(kwargs['data'], 200)

