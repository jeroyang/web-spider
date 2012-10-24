import Queue
import threading
import urllib2
import datetime
import re
import random
from lxml import etree
from urlparse import urljoin

class Crawler(threading.Thread):
    """A threaded web crawler, comsumming the url_queue and push to parse_ store_queue"""
    def __init__(self, resources):
        threading.Thread.__init__(self)
        self.url_queue = resources.url_queue
        self.parse_queue = resources.parse_queue
        self.store_queue = resources.store_queue
        self.stop_event = resources.stop_event
        
    def run(self):
        while not self.stop_event.is_set():
            # Get url from the url_queue
            url = self.url_queue.get()
            try:
                html = urllib2.urlopen(url, timeout=5).read()
                print "%s Crawler: %s" % (datetime.datetime.now(), url)
                self.parse_queue.put((url, html))
                self.store_queue.put((url, html, datetime.datetime.now()))
            except:
                pass

            self.url_queue.task_done()
            
        
class Parser(threading.Thread):
    """A threaded html parser, find possibly good url and push to url_queue"""
    def __init__(self, resources):
        threading.Thread.__init__(self)
        self.url_queue = resources.url_queue
        self.parse_queue = resources.parse_queue
        self.seen_url = resources.seen_url
        self.stop_event = resources.stop_event
    
    def _is_seen(self, url):
        """The is seen test of url, return ture if the url is seen, else return false, 
           if the url is not seen, update this url into repository"""
        if url in self.seen_url:
            return True
        else:
            self.seen_url.add(url)
            return False

    def run(self):
        while not self.stop_event.is_set():
            # Get html page from the parse_queue
            base, html = self.parse_queue.get()
            try:
                tree = etree.fromstring(html, etree.HTMLParser())
                urls = [urljoin(base, url) for url in tree.xpath('//a/@href') \
                                if re.match(r'^http', urljoin(base, url))]
                urls = random.sample(urls, min(5, len(urls)))
                # do the url_is_seen test
                for url in urls:
                    if not self._is_seen(url):
                        self.url_queue.put(url)
            except:
                pass
                
            self.parse_queue.task_done()
    
    
class Storer(threading.Thread):
    """A threaded page storer, save the html page in chunck"""
    def __init__(self, resources):
        threading.Thread.__init__(self)
        self.store_queue = resources.store_queue
        self.stop_event = resources.stop_event

    def run(self):
        while not self.stop_event.is_set():
            # Get html page from the store_queue
            url, html, time = self.store_queue.get()
            self.store_queue.task_done()

            
class Resources(object):
    """The class hold the shared resources"""
    def __init__(self):
        self.seen_url = set()
        self.url_queue = Queue.Queue()
        self.parse_queue = Queue.Queue()
        self.store_queue = Queue.Queue()
        self.stop_event = threading.Event()
        self.log = open('web_crawler.log', 'a')
            