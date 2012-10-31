import Queue
import threading
import urllib2
import time, datetime
import re
import random
import codecs
import os
from hashlib import md5
from collections import Counter, deque
from lxml import etree
from urlparse import urljoin, urlparse
from urllib import quote
from settings import *

# Global variables in this module

url_queue = Queue.Queue(maxsize=1000)
parse_queue = Queue.Queue()
store_queue = Queue.Queue()
stop_event = threading.Event()

def filename_from_url(url):
    """Return the tuple of path name and filename from a url"""
    url_parts = urlparse(url.encode("utf-8", 'replace'))
    path = '/'.join(re.split(r'[.:]', url_parts.netloc)[::-1])
    path = os.path.join('archives/', path)
    
    file_namer = md5()
    file_namer.update(url_parts.path)
    file_namer.update(url_parts.query)
    file_namer.update(url_parts.fragment)
    
    return (path, file_namer.hexdigest())
    

class Crawler(threading.Thread):
    """A threaded web crawler, comsumming the url_queue and push to parse_ store_queue"""
    global url_queue, parse_queue, store_queue, stop_event
        
    def run(self):
        while True:
            try:          
                url = url_queue.get(True) # Get url from the url_queue
                start = time.time()
                try:
                    html = urllib2.urlopen(url, timeout=5).read()
                except Exception as inst:
                    Profiler.crawler_errors[inst.__str__()] += 1
                    url_queue.task_done()
                    break                
                response_time = time.time() - start
                print "%s INFO: %s" % (str(datetime.datetime.now())[0:19], re.sub(r'(.{48}).*', r'\1...', url))
                parse_queue.put((url, html, response_time))
                store_queue.put((url, html, datetime.datetime.now()))
                url_queue.task_done()
                    
            except AttributeError:
                pass
                   
class Parser(threading.Thread):
    """A threaded html parser, find possibly good url and push to url_queue"""
    global url_queue, parse_queue, stop_event

    def _is_seen(self, url):
        """The is seen test of url, return ture if the url is seen, else return false, 
           if the url is not seen, update this url into repository"""
        if url in Profiler.seen_url:
            return True
        elif os.path.isfile(os.path.join(*filename_from_url(url))):
            Profiler.seen_url.appendleft(url)
            return True
        else:
            Profiler.seen_url.appendleft(url)
            return False

    def _is_excluded(self, url):
        if re.match(EXCLUDE, url):
            return True
        else:
            return False
        
    def run(self):
        while not stop_event.is_set():
            base, html, r = parse_queue.get() # Get html page from the parse_queue, r is response_time
            urls = []
            try:
                tree = etree.fromstring(html, etree.HTMLParser())
                urls = [urljoin(base, url) for url in tree.xpath('//a/@href') \
                            if re.match(r'^http.{,80}$', urljoin(base, url))]
                urls = random.sample(urls, min(SAMPLING_SIZE, len(urls)))
            except Exception as inst:
                Profiler.parser_errors[inst.__str__()] += 1
                
            # do the url_is_seen test, and exclude urls in EXCLUDE pattern
            for url in urls:
                if not self._is_excluded(url) or not self._is_seen(url):
                    url_queue.put(url)
                    
            parse_queue.task_done()

class Storer(threading.Thread):
    """A threaded page storer, save the html page in chunck"""
    def run(self):
        while True:
            # Get html page from the store_queue
            url, html, time = store_queue.get()
            Profiler.download_bytes += len(html)
            path, filename = filename_from_url(url)
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(os.path.join(path, filename), 'wb') as output_file:
                    output_file.write(html)
                Profiler.page_counter += 1
            except Exception as inst:
                Profiler.parser_errors[inst.__str__()] += 1
                
            store_queue.task_done()

class Terminator(threading.Thread):
    def run(self):
        global url_queue, stop_event
        print "%s CRAWLER: Terminate the %i working threads gently..." % (str(datetime.datetime.now())[0:19], CRAWLER_NUMBER)
        remained_urls = deque()
        
        while True: # Save the queuing urls to seeds.txt
            try:
                url = url_queue.get_nowait()
            except Queue.Empty:
                break
            remained_urls.append(url.encode("utf-8", 'replace'))
            url_queue.task_done()
        
        with open('seeds.txt', 'w') as seed_file:
            for url in remained_urls:
                try:
                    seed_file.write("%s\n" % url)
                except Exception as inst:
                    print inst
                
        while True:
            url_queue.get()
            url_queue.task_done()
    
class Logger(object):
    pass
    
class Profiler(object):
    crawler_errors = Counter()
    parser_errors = Counter()
    storer_errors = Counter()
    seen_url = deque(maxlen=1000)
    page_counter = 0
    download_bytes = 0
    
    