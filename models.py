import Queue
import threading
import urllib2
import time, datetime
import re
import random
import codecs
import os
from hashlib import md5
from collections import Counter
from lxml import etree
from urlparse import urljoin, urlparse
from settings import *

# Global variables in this module

url_queue = Queue.Queue(maxsize=800)
parse_queue = Queue.Queue()
store_queue = Queue.Queue()
go_event = threading.Event()
stop_event = threading.Event()
sample_size = 5

class Crawler(threading.Thread):
    """A threaded web crawler, comsumming the url_queue and push to parse_ store_queue"""
    global url_queue, parse_queue, store_queue, go_event

    def run(self):
        while True:
            try:
                if go_event.is_set():            
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
                else:
                    stop_event.set()
                    go_event.wait()
                    

            except AttributeError:
                pass
                   
class Parser(threading.Thread):
    """A threaded html parser, find possibly good url and push to url_queue"""
    global url_queue, parse_queue, sample_size

    def _is_seen(self, url):
        """The is seen test of url, return ture if the url is seen, else return false, 
           if the url is not seen, update this url into repository"""
        if url in Profiler.seen_url:
            return True
        else:
            Profiler.seen_url.add(url)
            return False

    def run(self):
        while True:
            base, html, r = parse_queue.get() # Get html page from the parse_queue, r is response_time
            urls = []
            try:
                tree = etree.fromstring(html, etree.HTMLParser())
                urls = [urljoin(base, url) for url in tree.xpath('//a/@href') \
                            if re.match(r'^http.{,80}$', urljoin(base, url))]
                urls = random.sample(urls, min(sample_size, len(urls)))
            except Exception as inst:
                Profiler.parser_errors[inst.__str__()] += 1
                parse_queue.task_done()
                
            # do the url_is_seen test
            for url in urls:
                if not self._is_seen(url):
                    url_queue.put(url)
            parse_queue.task_done()

    
class Storer(threading.Thread):
    """A threaded page storer, save the html page in chunck"""
    def run(self):
        while True:
            # Get html page from the store_queue
            url, html, time = store_queue.get()
            Profiler.download_bytes += len(html)
            url_parts = urlparse(url)
            path = '/'.join(re.split(r'[.:]', url_parts.netloc)[::-1])
            path = os.path.join('archives/', path)
            
            file_namer = md5()
            file_namer.update(url_parts.path)
            file_namer.update(url_parts.query)
            file_namer.update(url_parts.fragment)
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                with open(os.path.join(path, file_namer.hexdigest()), 'wb') as output_file:
                    output_file.write(html)
                Profiler.page_counter += 1
            except Exception as inst:
                Profiler.parser_errors[inst.__str__()] += 1
            store_queue.task_done()

class Terminator(threading.Thread):
    def run(self):
        global url_queue
        print "%s **********Terminate the %i working threads gentally" % (str(datetime.datetime.now())[0:19], CRAWLER_NUMBER)
        with codecs.open('seeds.txt', 'w', 'utf-8') as seed_file:
            for i in range(500): # Save the queuing urls to seeds.txt
                try:
                    seed_file.write("%s\n" % url_queue.get())
                except:
                    pass
                finally:
                    url_queue.task_done()
            while True:
                url_queue.get()
                url_queue.task_done()
    
class Logger(object):
    pass
    
class Profiler(object):
    crawler_errors = Counter()
    parser_errors = Counter()
    storer_errors = Counter()
    seen_url = set()
    page_counter = 0
    download_bytes = 0
    
    