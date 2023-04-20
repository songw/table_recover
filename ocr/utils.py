import os
import errno
from urllib import parse
from wsgiref.handlers import format_date_time
from time import mktime
from datetime import datetime
import hmac
import hashlib
import base64
from urllib.parse import urlencode


def get_file_cnt(fd):
    """
    根据文件路径获取二进制数据
    fd:文件路径
    返回二进制数据
    """
    if os.path.exists(fd):
        with open(fd, "rb") as f:
            f_data = f.read()
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), fd)

    return f_data


def build_auth_request_url(request_url, method, api_key, api_secret):
    """
    生成鉴权的url
    """
    url = parse.urlparse(request_url)
    date = format_date_time(mktime(datetime.now().timetuple()))

    signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(url.hostname, date, method, url.path)
    signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                             digestmod=hashlib.sha256).digest()
    signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
    authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
        api_key, "hmac-sha256", "host date request-line", signature_sha)
    authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
    values = {
        "host": url.hostname,
        "date": date,
        "authorization": authorization
    }
    return request_url + "?" + urlencode(values)
