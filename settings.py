# Settings
SOCKET_TIMEOUT = 10 # Avoid bad network connections

CRAWLER_NUMBER = 70 # If there is free network bandwidth and free CPU, increase this number.
PARSER_NUMBER = 1 # One should be enough
STORER_NUMBER = 1 # One should be enough

URL_QUEUE_SIZE = 20000
SEEN_URL_SIZE = 20000
REPORT_INTERVAL = 20 # The interval between two reports about fetched pages, and fetching speed.
EXCLUDE = r'(?i).*?/.*?\.(gz|tar|tgz|z|zip|exe|ps|doc|pdf|xplot|java|c|h|txt|ppt|gif|tiff|tif|png|jpeg|jpg|jpe|xls|map)$'
SEEDS = ['http://www.dmoz.org/', 
        'http://web.ncku.edu.tw/bin/home.php', 
        'http://dir.yahoo.com/', 
        'http://www.usa.gov/',
        'http://australia.gov.au/',
        'http://vlib.org/'] # will be used whenever the seeds.txt is not exist or empty
SAMPLING_SIZE = 20 # greater the number, more memmory will be used, lesser the number, increase the possibility of out_of_url
TIME_LIMIT = 30*60 # in seconds


