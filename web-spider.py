from models import *
import time 
from setup import *

def main():
    start = time.time()
    res = Resources()
    for seed in SEEDS:
        res.url_queue.put(seed)

    try:
        for i in range(CRAWLER_NUMBER):
            crawler = Crawler(res)
            crawler.setDaemon(True)
            crawler.start()
        
        for i in range(PARSER_NUMBER):
            parser = Parser(res)
            parser.setDaemon(True)
            parser.start()
            
        for i in range(STORER_NUMBER):
            storer = Storer(res)
            storer.setDaemon(True)
            storer.start()
    
    except:
        pass   
    
    while time.time() - start < TIME_LIMIT:
        pass
        
    res.stop_event.set() # Fire the stop signal
    
    print "%s webpages were fetched in %s seconds." % (len(res.seen_url), time.time()-start)
    
main()