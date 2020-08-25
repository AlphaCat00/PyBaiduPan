class BdApiError(IOError):
    pass


def mute_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            pass

    return wrapper


def log_error(func):
    import logging
    logger = logging.getLogger('BdPan')

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not hasattr(e, 'is_logged'):
                logger.error(e)
                e.is_logged = True
            raise e

    return wrapper
