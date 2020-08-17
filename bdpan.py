import os
from DecryptLogin.login import Login
import requests
from DecryptLogin.utils.cookies import loadSessionCookies, saveSessionCookies
from config import config
import logging
from requests.exceptions import HTTPError


def log_error(func):
    logger = logging.getLogger('BdPan')

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            logger.error("%s %s" % (e, e.response.text))
            raise e
        except Exception as e:
            logger.error(e)
            raise e

    return wrapper


class BdPan:
    BASE_URL = 'https://pcs.baidu.com/rest/2.0/pcs/'

    def __init__(self):
        self.session = requests.Session()
        self._get_logger()

    @staticmethod
    def sizeof_fmt(num):
        for unit in ['B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if abs(num) < 1024.0:
                return "%3.1f%s" % (num, unit)
            num /= 1024.0
        return "%.1f%s" % (num, 'Y')

    def _get_logger(self):
        self.logger = logging.getLogger('BdPan')
        self.logger.setLevel(logging.INFO)
        ch = logging.FileHandler(config["log_file"]) if config.get("log_file") else logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        self.logger.addHandler(ch)

    def bd_get(self, method, path='file', params={}, **kwargs):
        params['app_id'] = config['app_id']
        params['method'] = method
        return self.session.get(BdPan.BASE_URL + path, params=params, **kwargs)

    @log_error
    def login(self):
        infos_return, self.session = loadSessionCookies(session=self.session, cookiespath=config['cookies'])
        if not infos_return['is_success'] or self.bd_get('info', 'quota').status_code != 200:
            infos_return, self.session = Login().baidupan(config['username'], config['password'], 'pc')
            if infos_return['errInfo']['no'] != '0':
                raise RuntimeError(infos_return)
        saveSessionCookies(session=self.session, cookiespath=config['cookies'])

    def download_file(self, path, r_path=''):
        f_name = os.path.split(path)[1]
        f_path = os.path.join(config['local_path'], r_path, f_name)
        if not config['overwrite'] and os.path.exists(f_path):
            return
        self.logger.info(os.path.join(r_path, f_name))
        headers = {}
        if os.path.exists(f_path + '.part'):
            headers['Range'] = 'bytes=%d-' % os.path.getsize(f_path + '.part')
        with self.bd_get('download', params={'path': path}, headers=headers, stream=True) as r:
            if r.status_code >= 400:
                _ = r.content
                r.raise_for_status()
            os.makedirs(os.path.join(config['local_path'], r_path), exist_ok=True)
            with open(f_path + '.part', 'ab') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        os.rename(f_path + '.part', f_path)

    def _list(self, path, known_dir=False):
        if not known_dir:
            res = self.bd_get('meta', params={'path': path})
            res.raise_for_status()
        if known_dir or res.json()['list'][0]['isdir'] == 1:
            res = self.bd_get('list', params={'path': path})
            res.raise_for_status()
        return res.json()['list']

    @log_error
    def list(self, path):
        for i in self._list(path):
            print(['F', 'D'][i['isdir']], '%6s' % self.sizeof_fmt(i['size']), os.path.split(i['path'])[1])

    @log_error
    def download(self, path, r_path='', known_dir=False):
        for i in self._list(path, known_dir):
            if i['isdir']:
                self.download(i['path'], os.path.join(r_path, os.path.split(i['path'])[1]), True)
            else:
                self.download_file(i['path'], r_path)


def main():
    try:
        pan = BdPan()
        pan.login()
        eval('pan.' + config['action'] + "('" + config['path'] + "')")
    except:
        pass


if __name__ == '__main__':
    main()
