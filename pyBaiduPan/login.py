import re
from collections import OrderedDict
from flask import Flask, request, make_response, abort
import requests
from urllib.parse import urlparse

from werkzeug import run_simple

URL_MAPPING = OrderedDict((("/passport-baidu", "https://passport.baidu.com"),
                           ("/passport-bdimg", "https://passport.bdimg.com"),
                           ("/wappass0", "https://wappass.baidu.com"),
                           ("/wappass1", "https://ppui-static-pc.cdn.bcebos.com"),
                           ("", 'https://pan.baidu.com')))


def replace_url(content):
    for k, v in list(URL_MAPPING.items())[:-1]:
        content = re.sub(b"https?" + v[5:].encode("ascii"), k.encode("ascii"), content)
        content = re.sub(br"[a-zA-Z0-9_.]+\(?\)? *\+ *([\",'])/?/?" + v[8:].encode("ascii"), br"\1" + k.encode("ascii"),
                         content)
    return content


def replace_login_url(content):
    return re.sub(br"https?:\\?/\\?/pan.baidu.com", b"", content)


def baidu_pan_login(host="0.0.0.0", port=25000):
    app = Flask(__name__, static_url_path='/none')
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
        'Referer': 'https://pan.baidu.com/'
    })

    @app.route('/', defaults={'path': ''}, methods=['POST', 'GET'])
    @app.route('/<path:path>', methods=['POST', 'GET'])
    def login(path):
        url = urlparse(request.url)
        path = url.path + "?" + url.query
        for u_k, u_v in URL_MAPPING.items():
            if path[:len(u_k)] == u_k:
                data = dict(request.values.dicts[1])
                if path.find("/v2/api/?login") != -1 and request.method == 'POST':
                    data['u'] = "https://pan.baidu.com/disk/home"
                    data['staticpage'] = "https://pan.baidu.com/res/static/thirdparty/pass_v3_jump.html"
                try:
                    print(u_v + path[len(u_k):])
                    res = s.request(request.method, u_v + path[len(u_k):], data=data, timeout=20)
                except requests.Timeout:
                    abort(504)
                if urlparse(res.url).path == "/disk/home":
                    request.environ.get('werkzeug.server.shutdown')()
                    return "<h1>login successfully! server exited.</h1>"
                content = res.content
                if res.headers['Content-Type'].find("javascript") != -1:
                    content = replace_url(res.content)
                if path.find("/v2/api/?login") != -1 and request.method == 'POST':
                    content = replace_login_url(content)
                resp = make_response(content)
                for k, v in s.cookies.items():
                    if k not in request.cookies:
                        resp.set_cookie(k, v)
                resp.content_type = res.headers['Content-Type']
                return resp, res.status_code
        abort(404)

    run_simple(host, port, app)
    return s


if __name__ == '__main__':
    baidu_pan_login()
