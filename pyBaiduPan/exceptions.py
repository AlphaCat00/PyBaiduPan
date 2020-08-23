from requests.exceptions import HTTPError


class BdApiError(IOError):
    pass


def raise_for_errno(response):
    info = response.json()
    if 'errno' in info and info['errno'] != 0:
        raise BdApiError('url:' + response.url, info)
    return info


def covert_http_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            raise BdApiError(*e.args, e.response.json())

    return wrapper


def mute_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BdApiError:
            pass

    return wrapper


def log_error(func):
    import logging
    logger = logging.getLogger('BdPan')

    def wrapper(*args, **kwargs):
        try:
            return covert_http_error(func)(*args, **kwargs)
        except Exception as e:
            if not hasattr(e, 'is_logged'):
                logger.error(e)
                e.is_logged = True
            raise e

    return wrapper
