import json
import os
import re
from exceptions import *
from DecryptLogin.login import Login
from config import config
import logging
from itertools import count
import pickle
import shutil
import requests
from hashlib import md5
from functools import partial
from urllib.parse import quote
from base64 import b64encode


def log_error(func):
    logger = logging.getLogger('BdPan')

    def wrapper(*args, **kwargs):
        try:
            return covert_http_error(func)(*args, **kwargs)
        except BdApiError as e:
            logger.error(e)
            raise e

    return wrapper


class BdPan:
    URL = {'PCS': 'https://pcs.baidu.com/rest/2.0/pcs/', 'XPAN': 'https://pan.baidu.com/rest/2.0/xpan/'}
    LIST_LIMIT = 5000
    UPLOAD_SIZE = 4 << 20

    def __init__(self):
        self.bd_get = partial(self._bd_request, 'get')
        self.bd_post = partial(self._bd_request, 'post')
        self._get_logger()
        self.session = None
        self.bdstoken = None

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

    @staticmethod
    def _get_bdstoken(html):
        return re.search("'bdstoken', *'([0-9a-f]+)'", html).group(1)

    def _get_logger(self):
        self.logger = logging.getLogger('BdPan')
        self.logger.setLevel(logging.INFO)
        ch = logging.FileHandler(config["log_file"]) if config.get("log_file") else logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
        self.logger.addHandler(ch)

    def _bd_request(self, _method, method, path='file', api='XPAN', params={}, **kwargs):
        params['app_id'] = config['app_id']
        params['method'] = method
        if api == 'XPAN' and self.bdstoken:
            params['bdstoken'] = self.bdstoken
            params['logid'] = b64encode(self.session.cookies['BAIDUID'].encode('ascii'))
        return self.session.request(_method, BdPan.URL[api] + path, params=params, **kwargs)

    @log_error
    def login(self):
        self.session = self.load_session()
        if self.session is None or self.bd_get('uinfo', 'nas').json()["errno"] != 0:
            infos_return, self.session = Login().baidupan(config['username'], config['password'], 'pc')
            print(infos_return)
            if infos_return['errInfo']['no'] != '0':
                raise RuntimeError(infos_return)
            self.save_session(self.session)
        res = self.session.get('https://pan.baidu.com/disk/home')
        self.bdstoken = self._get_bdstoken(res.text)

    def download_file(self, path, r_path=''):
        f_name = os.path.split(path)[1]
        f_path = os.path.join(config['local_path'], r_path, f_name)
        if not config['overwrite'] and os.path.exists(f_path):
            return
        self.logger.info(os.path.join(r_path, f_name))
        headers = {}
        if os.path.exists(f_path + '.part'):
            headers['Range'] = 'bytes=%d-' % os.path.getsize(f_path + '.part')
        with self.bd_get('download', api='PCS', params={'path': path}, headers=headers, stream=True) as r:
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
            res = self.bd_get('meta', api='PCS', params={'path': path})
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

    @staticmethod
    def file_slice(file, size=UPLOAD_SIZE):
        with open(file, 'rb') as f:
            for c in iter(partial(f.read, size), b''):
                yield c

    def upload_file(self, bd_path, f_path):
        self.logger.info(f'upload {f_path} to {bd_path}')
        content_md5, block_list = md5(), []
        for x in self.file_slice(f_path):
            content_md5.update(x)
            block_list.append(md5(x).hexdigest())
        content_md5, block_list = content_md5.hexdigest(), json.dumps(block_list)
        slice_md5 = md5(next(self.file_slice(f_path, 256 << 10))).hexdigest()
        data = {'path': bd_path, 'size': os.path.getsize(f_path), 'isdir': "0", 'autoinit': 1, 'block_list': block_list,
                'rtype': 0, 'content-md5': content_md5, "slice-md5": slice_md5}
        res = self.bd_post('precreate', data=data)
        res = raise_for_errno(res)
        if res['return_type'] == 2:  # rapid upload
            return res['info']
        params = {'type': 'tmpfile', 'path': quote(bd_path, ''), 'uploadid': res.json()['uploadid']}
        for i, x in enumerate(self.file_slice(f_path)):
            params['partseq'] = i
            raise_for_errno(self.bd_post('upload', 'superfile2', api='PCS', params=params, files={'file': x}))
        data = {k: v for k, v in data if k in ('path', 'size', 'isdir', 'block_list', 'rtype')}
        data['uploadid'] = params['uploadid']
        res = self.bd_post('create', data=data)
        return raise_for_errno(res)


def main():
    try:
        pan = BdPan()
        pan.login()
        eval('pan.' + config['action'] + "('" + config['path'] + "')")
    except Exception as e:
        pass


if __name__ == '__main__':
    main()
