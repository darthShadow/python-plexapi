# -*- coding: utf-8 -*-
# Running these tests requires a few things in your Plex Library.
# 1. A Movies section containing both movies: 16 Blocks, Die Hard.
# 2. A Music section containing the album: Infinite State - Unmastered Impulses
#    https://github.com/kennethreitz/unmastered-impulses
# 3. A Photos section containing the album Cats with photos named:
#    <to-be-determined>
# 4. A TV Shows section containing at least two seasons of The 100.
import plexapi, pytest, requests
from plexapi import compat
from plexapi.client import PlexClient
from datetime import datetime
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from functools import partial

SERVER_BASEURL = plexapi.CONFIG.get('auth.server_baseurl')
SERVER_TOKEN = plexapi.CONFIG.get('auth.server_token')
MYPLEX_USERNAME = plexapi.CONFIG.get('auth.myplex_username')
MYPLEX_PASSWORD = plexapi.CONFIG.get('auth.myplex_password')
CLIENT_BASEURL = plexapi.CONFIG.get('auth.client_baseurl')
CLIENT_TOKEN = plexapi.CONFIG.get('auth.client_token')

MIN_DATETIME = datetime(2014, 1, 1)
REGEX_EMAIL = r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
REGEX_IPADDR = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'

AUDIOCHANNELS = {2, 6}
AUDIOLAYOUTS = {'5.1', '5.1(side)', 'stereo'}
CODECS = {'aac', 'ac3', 'dca', 'h264', 'mp3', 'mpeg4'}
CONTAINERS = {'avi', 'mp4', 'mkv'}
CONTENTRATINGS = {'TV-14'}
FRAMERATES = {'24p', 'PAL'}
PROFILES = {'advanced simple', 'main'}
RESOLUTIONS = {'sd', '576', '720', '1080'}


def pytest_addoption(parser):
    parser.addoption('--client', action='store_true', default=False, help='Run client tests.')


def pytest_runtest_setup(item):
    if 'client' in item.keywords and not item.config.getvalue('client'):
        return pytest.skip('Need --client option to run.')


#---------------------------------
# Fixtures
#---------------------------------

@pytest.fixture()
def account():
    assert MYPLEX_USERNAME, 'Required MYPLEX_USERNAME not specified.'
    assert MYPLEX_PASSWORD, 'Required MYPLEX_PASSWORD not specified.'
    return MyPlexAccount(MYPLEX_USERNAME, MYPLEX_PASSWORD)


@pytest.fixture(scope='session')
def plex():
    assert SERVER_BASEURL, 'Required SERVER_BASEURL not specified.'
    assert SERVER_TOKEN, 'Requred SERVER_TOKEN not specified.'
    session = requests.Session()
    return PlexServer(SERVER_BASEURL, SERVER_TOKEN, session=session)


@pytest.fixture()
def plex2():
    return plex()


@pytest.fixture()
def client(request):
    return PlexClient(baseurl=CLIENT_BASEURL, token=CLIENT_TOKEN)


@pytest.fixture()
def tvshows(plex):
    return plex.library.section('TV Shows')


@pytest.fixture()
def movies(plex):
    return plex.library.section('Movies')


@pytest.fixture()
def music(plex):
    return plex.library.section('Music')


@pytest.fixture()
def photos(plex):
    return plex.library.section('Photos')


@pytest.fixture()
def movie(movies):
    return movies.get('16 blocks')


@pytest.fixture()
def artist(music):
    return music.get('Infinite State')


@pytest.fixture()
def album(artist):
    return artist.album('Unmastered Impulses')


@pytest.fixture()
def track(album):
    return album.track('Holy Moment')


@pytest.fixture()
def show(tvshows):
    return tvshows.get('The 100')


@pytest.fixture()
def episode(show):
    return show.get('Pilot')


@pytest.fixture()
def photoalbum(photos):
    try:
        return photos.get('Cats')
    except:
        return photos.get('photo_album1')


@pytest.fixture()
def monkeydownload(request, monkeypatch):
    monkeypatch.setattr('plexapi.utils.download', partial(plexapi.utils.download, mocked=True))
    yield
    monkeypatch.undo()


#---------------------------------
# Utility Functions
#---------------------------------

def is_datetime(value):
    return value > MIN_DATETIME


def is_int(value, gte=1):
    return int(value) >= gte


def is_float(value, gte=1.0):
    return float(value) >= gte


def is_metadata(key, prefix='/library/metadata/', contains='', suffix=''):
    try:
        assert key.startswith(prefix)
        assert contains in key
        assert key.endswith(suffix)
        return True
    except AssertionError:
        return False


def is_part(key):
    return is_metadata(key, prefix='/library/parts/')


def is_section(key):
    return is_metadata(key, prefix='/library/sections/')


def is_string(value, gte=1):
    return isinstance(value, compat.string_type) and len(value) >= gte


def is_thumb(key):
    return is_metadata(key, contains='/thumb/')
