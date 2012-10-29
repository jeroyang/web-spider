Web-spider Homework for NCKU-WRDU course, 2012
==========

Author:

* CSIE-P78011167-楊家融-HW3
* 楊家融, email: jeroyang@gmail.com

Introduction:

* This is a simple multiprocessing general web-crawler written in python.

Basic requirements:
   
* Python(http://www.python.org/): The programming language
* lxml(http://lxml.de/): The fastest XML/HTML parser in python

Installation:

* Currently, there is no installer, just grab the source code and run.
* Download for GIT: git clone https://github.com/jeroyang/web-spider.git
* Download zipball: https://github.com/jeroyang/web-spider/zipball/master

How to run:
	
1. Check the setting.py to see anything should be change.
2. Type "python web-spider.py" on command line.

Current problems:

1. Difficulty in gently shutting down the threads, it takes one more minutes to stop.
2. Primitive url seen test, I just put every seen url in memory, it will be explode after fetch a lot of websites.

	
