import time 
import socket
import codecs
import re
import models as m
import datetime
from settings import *

def _load_seeds():
    """Load the seeds.txt"""
    try:
        with open('seeds.txt', 'r') as seed_file:
            seeds = [url for url in seed_file.read().split("\n") if url[0:4] == 'http']
    except:
        print "The seeds.txt cannot be loaded, use SEEDS in settings.py instead."
        seeds = SEEDS
    
    # check if seeds.txt is empty
    if len(seeds) == 0:
        print "There is no valid seed in seeds.txt, use default SEEDS in settings.py. "
        seeds = SEEDS
        
    for seed in seeds:
        m.url_queue.put(seed)

def _start_greeting():
    """Print some message about this crawler"""
    print "==========================================================="
    print "Web-spider Homework for NCKU-WRDU course, 2012"
    print "CSIE-P78011167-YangChiaJung-HW3"
    print "Yang Chia-Jung, email: jeroyang@gmail.com"
    print "==========================================================="
    print "Start fetching the web using %i threaded crawlers..." % CRAWLER_NUMBER

def _report(last_pages, last_bytes):
    current_pages = m.Profiler.page_counter
    current_bytes = m.Profiler.download_bytes
    print "%s REPORT: %i pages fetched. %.2f pages/s (%.2f KB/s)" % \
                    (str(datetime.datetime.now())[0:19], current_pages, float(current_pages-last_pages)/REPORT_INTERVAL, float(current_bytes-last_bytes)/1000/REPORT_INTERVAL)
    if not m.stop_event.is_set():
        next_report = m.threading.Timer(REPORT_INTERVAL, _report, [current_pages, current_bytes])
        next_report.daemon = True
        next_report.start()

def _summary(elapsed_time):
    """Print informations about this crawling task."""
    print "==========================================================="
    print "%s webpages (%i KB) were fetched in %.2f seconds." % (m.Profiler.page_counter, m.Profiler.download_bytes//1000, elapsed_time)
    print "Speed: %.2f pages/sec (%.2f KB/sec)." % (float(m.Profiler.page_counter)/elapsed_time, float(m.Profiler.download_bytes)/1000/elapsed_time)
    
def _error():
    """Print error reports"""
    print "Error Reports:\t", 
    print "\t".join(["%s: %i" % (re.sub(r'.*(\d\d\d).*', r'   \1', error_type, flags=re.S), number) \
                    for (error_type, number) in m.Profiler.crawler_errors.iteritems()\
                    if error_type[0:4]=='HTTP'])
    
def main():
    socket.setdefaulttimeout(SOCKET_TIMEOUT)
    start = time.time()
    crawler_pool = []
    _start_greeting()
    _load_seeds()
    try:
        # Create a periodic reporter to show crawling summaries
        m.threading.Timer(REPORT_INTERVAL, _report, [0, 0]).start()
    
        # Set stop_event later
        m.threading.Timer(TIME_LIMIT, m.stop_event.set).start()

        """Set a pool of three kinds of threads to run"""

        for i in range(CRAWLER_NUMBER):
            crawler = m.Crawler()
            crawler.daemon = True
            crawler.start()
            crawler_pool.append(crawler)

        for i in range(PARSER_NUMBER):
            parser = m.Parser()
            parser.daemon = True
            parser.start()
    
        for i in range(STORER_NUMBER):
            storer = m.Storer()
            storer.daemon = True
            storer.start()

        while not m.stop_event.is_set():
            time.sleep(0.1)
        
    except (KeyboardInterrupt, SystemExit):
        print "KeyboardIntterrupted, Stop the crawlers gracefully..."
    
    finally: 
        m.stop_event.set()
        terminator = m.Terminator()
        terminator.daemon = True
        terminator.start()
        for crawler in crawler_pool:
            crawler.join(0.1)
        m.url_queue.join()
        elapsed_time = time.time()-start
        _summary(elapsed_time)
        _error()
        print ''
    
main()