import os
from DecryptLogin.login import Login
from config import config
import logging
from requests.exceptions import HTTPError
from itertools import count
import pickle
import shutil


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
    URL = {'PCS': 'https://pcs.baidu.com/rest/2.0/pcs/', 'XPAN': 'https://pan.baidu.com/rest/2.0/xpan/'}
    LIST_LIMIT = 5000

    def __init__(self):
        self.session = None
        self._get_logger()

    @staticmethod
    def load_session():
        try:
            with open(config['session'], 'rb') as f:
                return pickle.load(f)
        except:
            pass

    @staticmethod
    def save_session(session):
        with open(config['session'], 'wb') as f:
            pickle.dump(session, f)

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

    def bd_get(self, method, path='file', url='XPAN', params={}, **kwargs):
        params['app_id'] = config['app_id']
        params['method'] = method
        return self.session.get(BdPan.URL[url] + path, params=params, **kwargs)

    @log_error
    def login(self):
        self.session = self.load_session()
        if self.session is None or self.bd_get('uinfo', 'nas').json()["errno"] != 0:
            infos_return, self.session = Login().baidupan(config['username'], config['password'], 'pc')
            if infos_return['errInfo']['no'] != '0':
                raise RuntimeError(infos_return)
            self.save_session(self.session)
        self.session.get('https://pan.baidu.com/')

    def download_file(self, path, r_path=''):
        f_name = os.path.split(path)[1]
        f_path = os.path.join(config['local_path'], r_path, f_name)
        if not config['overwrite'] and os.path.exists(f_path):
            return
        self.logger.info(os.path.join(r_path, f_name))
        headers = {}
        if os.path.exists(f_path + '.part'):
            headers['Range'] = 'bytes=%d-' % os.path.getsize(f_path + '.part')
        with self.bd_get('download', url='PCS', params={'path': path}, headers=headers, stream=True) as r:
            if r.status_code >= 400:
                _ = r.content
                r.raise_for_status()
            os.makedirs(os.path.join(config['local_path'], r_path), exist_ok=True)
            with open(f_path + '.part', 'ab') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        shutil.move(f_path + '.part', f_path)

    def _list(self, path, known_dir=False):
        if not known_dir:
            res = self.bd_get('meta', url='PCS', params={'path': path})
            res.raise_for_status()
            ret = res.json()['list']
        if known_dir or res.json()['list'][0]['isdir'] == 1:
            ret = []
            for i in count(step=BdPan.LIST_LIMIT):
                res = self.bd_get('list', params={'dir': path, 'limit': BdPan.LIST_LIMIT, 'start': i})
                res.raise_for_status()
                ret += res.json()['list']
                if len(res.json()['list']) < BdPan.LIST_LIMIT:
                    break
        return ret

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
    except Exception as e:
        # raise e
        pass


if __name__ == '__main__':
    main()
