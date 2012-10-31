# Settings
SOCKET_TIMEOUT = 10
CRAWLER_NUMBER = 100
PARSER_NUMBER = 2
STORER_NUMBER = 2
REPORT_INTERVAL = 20
EXCLUDE = r'.*?/.*?\.(gz|tar|tgz|z|zip|exe|ps|doc|pdf|xplot|java|c|h|txt|ppt|gif|tiff|tif|png|jpeg|jpg|jpe|xls|map)$'
SEEDS = ['http://www.dmoz.org/'] # will be used whenever the seeds.txt is not exist or empty
TIME_LIMIT = 30*60 # in seconds


