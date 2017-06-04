import os

__all__ = ('DATABASE_PATH', 'BLUEHOUSE', 'USER_AGENTS', 'TWITTER')

DATABASE_PATH = os.path.join(
    '{0}/db'.format(os.path.dirname(__file__)
    ), 'preseoje.db')

BLUEHOUSE = {
    'url': 'http://www1.president.go.kr',
    'sub': 'news/schedule.php'
    }

USER_AGENTS = (
    'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
    'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101  Firefox/28.0',
    ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/41.0.2228.0 Safari/537.36'),
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) '
        'AppleWebKit/537.75.14 (KHTML, like Gecko) '
        'Version/7.0.3 Safari/7046A194A'),
    ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246')
    )

TWITTER = {
    'api_key': '',
    'api_secret': '',
    'token': '',
    'token_secret': ''
}

