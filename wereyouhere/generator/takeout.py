from collections import OrderedDict
from datetime import datetime
from enum import Enum
from html.parser import HTMLParser
from os.path import join
from typing import List, Dict, Any
from urllib.parse import unquote

from wereyouhere.common import Entry, History, Visit

# Mar 8, 2018, 5:14:40 PM
_TIME_FORMAT = "%b %d, %Y, %I:%M:%S %p"

class State(Enum):
    OUTSIDE = 0
    INSIDE = 1
    PARSING_LINK = 2
    PARSING_DATE = 3

# would be easier to use beautiful soup, but ends up in a big memory footprint..
class TakeoutHTMLParser(HTMLParser):
    state: State
    current: Dict[str, str]
    urls: History

    def __init__(self):
        super().__init__()
        self.state = State.OUTSIDE
        self.urls = History()
        self.current = {}

    def _reg(self, name, value):
        assert name not in self.current
        self.current[name] = value

    def _astate(self, s): assert self.state == s

    def _trans(self, f, t):
        self._astate(f)
        self.state = t

    # enter content cell -> scan link -> scan date -> finish till next content cell
    def handle_starttag(self, tag, attrs):
        if self.state == State.INSIDE and tag == 'a':
            self.state = State.PARSING_LINK
            attrs = OrderedDict(attrs)
            hr = attrs['href']

            # sometimes it's starts with this prefix, it's apparently clicks from google search? or visits from chrome address line? who knows...
            # TODO handle http?
            prefix = r'https://www.google.com/url?q='
            if hr.startswith(prefix + "http"):
                hr = hr[len(prefix):]
                hr = unquote(hr)
            self._reg('url', hr)

    def handle_endtag(self, tag):
        if tag == 'html':
            pass # ??

    def handle_data(self, data):
        if self.state == State.OUTSIDE:
            if data[:-1] == "Visited":
                self.state = State.INSIDE
                return

        if self.state == State.PARSING_LINK:
            # self._reg(Entry.link, data)
            self.state = State.PARSING_DATE
            return

        if self.state == State.PARSING_DATE:
            # TODO regex?
            years = [str(i) + "," for i in range(2000, 2030)]
            for y in years:
                if y in data:
                    self._reg('time', data)

                    url = self.current['url']
                    times = self.current['time']
                    time = datetime.strptime(times, _TIME_FORMAT)
                    visit = Visit(
                        dt=time,
                        tag="activity",
                    )
                    self.urls.register(url, visit)

                    self.current = {}
                    self.state = State.OUTSIDE
                    return

def read_google_activity(takeout_dir: str) -> History:
    myactivity_html = join(takeout_dir, "My Activity", "Chrome", "MyActivity.html")

    data: str
    with open(myactivity_html, 'r') as fo:
        data = fo.read()
    parser = TakeoutHTMLParser()
    parser.feed(data)
    return parser.urls

def get_takeout_histories(takeout_dir: str) -> List[History]:
    chrome_myactivity = read_google_activity(takeout_dir)
    return [chrome_myactivity]