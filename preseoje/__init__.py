import pathlib
import time
import html
import random
import requests
import lxml.html
import tweepy
import datetime
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func

from preseoje.config import DATABASE_PATH, BLUEHOUSE, USER_AGENTS, TWITTER
from preseoje.db import db
from preseoje.db.db import session, Schedules

__all__ = ('preseoje', 'first_run', 'run')

auth = tweepy.OAuthHandler(TWITTER['api_key'], TWITTER['api_secret'])
auth.set_access_token(TWITTER['token'], TWITTER['token_secret'])
twitter = tweepy.API(auth)


def tweet_schedule(tweet):
    for t in tweet:
        twitter.update_status(t)


def tweet_slicer(tweet):
    """
    split tweet string for 140 character limit
    """
    result = []
    pool = ''
    count = 0
    for t in tweet[:-1]:
        if count + len(t) < 140:
            count += len(t)
            pool += t
        else:
            result.append(pool)
            pool = ''
            count = len(t)
            pool += t
    if count + len(tweet[-1]) < 140:
        count += len(tweet[-1])
        pool += tweet[-1]
        result.append(pool)
    else:
        result.append(pool)
        pool = ''
        count = 0
        pool += tweet[-1]
        result.append(pool)
    return result


def tweet_builder(date, source):
    """
    build tweet string from source records
    """
    if source == None:
        result = ['error']
        return result
    
    tweet = []
    tweet.append('{0}년 {1}월 {2}일 대통령 일정\n\n'.format(
        date.year, date.month, date.day))

    for s in source:
        tweet.append('[{0}:{1}] {2}\n'.format(
            s.datetime.hour, s.datetime.minute, s.content))
    
    if sum(len(t) for t in tweet) > 140:
        result = tweet_slicer(tweet)
    else:
        result = [''.join(tweet)]
    
    return result


def get_pres_schedule(date):
    """
    get president schedule somewhere and return content.
    """
    data = get_schedule_from_db(date)
    if len(data) == 0:
        data = get_schedule_from_web(date)
        return tweet_builder(date, data)
    else:
        return tweet_builder(date, data)        


def get_schedule_from_db(date):
    """
    get president schedule from internal db.
    if schedule not exist, return NoResultFound exception.
    """
    starttime = datetime.datetime.strptime(
        '{0}/{1}/{2}'.format(
            date.year,
            date.month,
            date.day,
            ),
        '%Y/%m/%d'
        )

    endtime = datetime.datetime.strptime(
        '{0}/{1}/{2} 23:59:59'.format(
            date.year,
            date.month,
            date.day,
            ),
        '%Y/%m/%d %H:%M:%S'
        )

    result = session.query(Schedules).filter(
        Schedules.datetime.between(
            starttime, endtime)).all()

    return result

def get_schedule_from_web(date):
    """
    get president schedule from bluehouse web.

    srh[period_type] - use for 'day'(1), 'weekly'(2), 'monthly'(3)

    .. todo:: remove lxml dependancy
    """
    payload = {
        'srh[year]': date.year,
        'srh[month]': date.month,
        'srh[day]': date.day
        }

    try:
        r = requests.get(
            '{0}/{1}'.format(
                BLUEHOUSE['url'],
                BLUEHOUSE['sub']),
            headers={'User-Agent': random.choice(USER_AGENTS)},
            params=payload
            )
    except BaseException:
        return None
    
    data = lxml.html.fromstring(r.text).\
            xpath(".//div[contains(@class, 'scheduleList')]")

    try:
        sched_chunk = lxml.html.fromstring(
            html.unescape(lxml.html.tostring(data[0]).decode('cp949')))
    except IndexError:
        return None

    sched_elements = sched_chunk.findall(".//dl/dd")
    
    sched_list = []

    if len(sched_elements) == 0:
        _datetime = datetime.datetime.strptime(
            '{0}/{1}/{2} 00:00:00'.format(
                date.year,
                date.month,
                date.day),
            '%Y/%m/%d %H:%M:%S'
            ) 
        _content = '일정 없음'
        new_sched = Schedules(
            datetime=_datetime, content=_content)
        sched_list.append(new_sched)
    else:
        for s in sched_elements:
            _time = s.xpath(".//span[contains(@class, 'spleft')]")[0].text
            _content = s.xpath(".//span[contains(@class, 'spright')]")[0].text
            _datetime = datetime.datetime.strptime(
                '{0}/{1}/{2} {3}:00'.format(
                    date.year,
                    date.month,
                    date.day,
                    _time),
                '%Y/%m/%d %H:%M:%S'
                )
            with session.begin():
                new_sched = Schedules(
                    datetime=_datetime, content=_content)
                session.add(new_sched)
                sched_list.append(new_sched)
    return sched_list


def preseoje(date):
    tweet_schedule(get_pres_schedule(date))


def initialize():
    db.initialize()


def first_run():
    try:
        pathlib.Path(DATABASE_PATH).resolve()
    except FileNotFoundError:
        initialize()

    start_date = datetime.date(2017, 5, 9)
    current_date = datetime.date.today()
    delta = current_date - start_date

    for i in reversed(range(delta.days)):
        preseoje(datetime.datetime.now() - datetime.timedelta(i))
        time.sleep(10)


def run():
    try:
        pathlib.Path(DATABASE_PATH).resolve()
    except FileNotFoundError:
        initialize()

    preseoje(datetime.datetime.now() - datetime.timedelta(days=1))
