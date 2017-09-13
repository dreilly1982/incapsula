import requests
import yaml
import urllib3
from collections import Iterable
from netaddr import IPSet
import os


class API(object):

    url = 'https://my.incapsula.com/api/prov/v1'
    api_key = None
    api_id = None
    ignore_ssl = False
    ignore_ssl_warnings = False

    def __init__(self, **kwargs):
        cfg_file = os.path.join(os.curdir, 'incapsula.yaml')
        if os.path.isfile(cfg_file):
            self.load_cfg(cfg_file)

        for key, value in kwargs.items():
            if key == 'url':
                self.url = value
            if key == 'api_key':
                self.api_key = value
            if key == 'api_id':
                self.api_id = value
            if key == 'ignore_ssl':
                self.ignore_ssl = value
            if key == 'ignore_ssl_warnings':
                self.ignore_ssl_warnings = value

        self.session = requests.session()

        if self.ignore_ssl:
            self.session.verify = False

        if self.ignore_ssl_warnings:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.payload = {'api_id': self.api_id,
                        'api_key': self.api_key}

    def load_cfg(self, cfg_file):
        with open(cfg_file, 'r') as f:
            cfg = yaml.load(f)

            for key, value in cfg.items():
                if key == 'url':
                    self.url = value
                if key == 'api_key':
                    self.api_key = value
                if key == 'api_id':
                    self.api_id = value
                if key == 'ssl':
                    if value is not None:
                        for ssl_key, ssl_value in value.items():
                            if ssl_key == 'ignore_ssl':
                                self.ignore_ssl = ssl_value
                            if ssl_key == 'ignore_ssl_warnings':
                                self.ignore_ssl_warnings = ssl_value

    def get_url(self, path):
        ret_url = self.url[:-1] if self.url.endswith('/') else self.url
        return ret_url + path

    def update_acl(self, payload):
        resp = self.send_request(self.get_url('/sites/configure/acl'),
                                 data=payload)
        return resp

    def send_request(self, url, data):
        resp = self.session.post(url, data=data)
        if resp.status_code != 200:
            raise Exception('POST {}/ {}'.format(resp.url, resp.status_code))
        if resp.json()['res_message'] != 'OK':
            raise Exception('{}'.format(resp.json()['res_message']))
        return resp.json()

    def get_site_acl(self, site_id):
        pass
        status = self.get_site_status(site_id)
        try:
            return status['security']['acls']['rules']
        except KeyError:
            return None

    def get_sites(self):
        resp = self.send_request(self.get_url('/sites/list'),
                                 data=self.payload)
        return resp

    def get_site_status(self, site_id):
        payload = self.payload
        payload.update({'site_id': site_id})
        resp = self.send_request(self.get_url('/sites/status'), data=payload)
        return resp

    def overwrite_ip_blacklist_acl(self, site_id, ips=[]):
        ip_string = ','.join(ips)
        payload = self.payload
        payload.update({'site_id': site_id,
                        'rule_id': 'api.acl.blacklisted_ips',
                        'ips': ip_string})
        return self.update_acl(payload)

    def overwrite_ip_whitelist_acl(self, site_id, ips=[]):
        ip_string = ','.join(ips)
        payload = self.payload
        payload.update({'site_id': site_id,
                        'rule_id': 'api.acl.whitelisted_ips',
                        'ips': ip_string})
        return self.update_acl(payload)

    def get_site_blacklisted_ips(self, site_id):
        rules = self.get_site_acl(site_id)
        for rule in rules:
            if rule['id'] == 'api.acl.blacklisted_ips':
                return rule['ips']
        return None

    def get_site_whitelisted_ips(self, site_id):
        rules = self.get_site_acl(site_id)
        for rule in rules:
            if rule['id'] == 'api.acl.whitelisted_ips':
                return rule['ips']
        return None

    def get_site_blacklisted_urls(self, site_id):
        rules = self.get_site_acl(site_id)
        for rule in rules:
            if rule['id'] == 'api.acl.blacklisted_urls':
                return rule['urls']
        return None

    def get_site_blacklisted_countries(self, site_id):
        rules = self.get_site_acl(site_id)
        for rule in rules:
            if rule['id'] == 'api.acl.blacklisted_countries':
                return rule['geo']
        return None

    def add_ip_to_blacklist(self, site_id, ips):
        if not isinstance(ips, Iterable) or isinstance(ips, str):
            ips = [ips]
        existing_blacklist_str = self.get_site_blacklisted_ips(site_id) if not None else []
        blacklist_ips = IPSet(existing_blacklist_str)
        for ip in ips:
            blacklist_ips.add(ip)
        return self.overwrite_ip_blacklist_acl(site_id=site_id,
                                               ips=list(map(str, blacklist_ips.iter_cidrs())))

    def remove_ip_from_blacklist(self, site_id, ips):
        if not isinstance(ips, Iterable) or isinstance(ips, str):
            ips = [ips]
        existing_blacklist_str = self.get_site_blacklisted_ips(site_id) if not None else []
        blacklist_ips = IPSet(existing_blacklist_str)
        for ip in ips:
            blacklist_ips.remove(ip)
        return self.overwrite_ip_blacklist_acl(site_id=site_id,
                                               ips=list(map(str, blacklist_ips.iter_cidrs())))

    def add_ip_to_whitelist(self, site_id, ips):
        if not isinstance(ips, Iterable) or isinstance(ips, str):
            ips = [ips]
        existing_whitelist_str = self.get_site_whitelisted_ips(site_id) if not None else []
        whitelist_ips = IPSet(existing_whitelist_str)
        for ip in ips:
            whitelist_ips.add(ip)
        return self.overwrite_ip_whitelist_acl(site_id=site_id,
                                               ips=list(map(str, whitelist_ips.iter_cidrs())))

    def remove_ip_from_whitelist(self, site_id, ips):
        if not isinstance(ips, Iterable) or isinstance(ips, str):
            ips = [ips]
        existing_whitelist_str = self.get_site_whitelisted_ips(site_id) if not None else []
        whitelist_ips = IPSet(existing_whitelist_str)
        for ip in ips:
            whitelist_ips.remove(ip)
        return self.overwrite_ip_whitelist_acl(site_id=site_id,
                                               ips=list(map(str, whitelist_ips.iter_cidrs())))

