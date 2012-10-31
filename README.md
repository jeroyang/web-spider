Web-spider Homework for NCKU-WRDU course, 2012
==========

Author:

* 資訊工程-P78011167-楊家融-HW3
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

執行的功能

1. 主程式讀取seeds.txt取得上次執行後留下的seeds，若無seeds則使用預設於settings.py的SEEDS。將seeds放入url_queue中。
2. 開始計時至TIME_LIMIT （於settings.py中設定）
3. 主程式啟始三種 threads: Crawler, Parser, and Storer，分別負責抓取網頁、解析網頁、及儲存網頁。
4. 三種 Queues 需要處理：url_queue, parse_queue, store_queue。Crawler由url_queue中取出目標url，並將抓取到的網頁放入parse_queue及store_queue; Parser由parse_queue中取出網頁，解析後取出其中可用之urls,將之置入url_queue; Storer由store_queue中取出網頁，並將其存入硬碟。
5. 計時時間到，開啟 Terminator：停止Parser工作，將url_queue中之剩餘url存入seeds.txt，終止所有的threads。
6. 顯示此執行相關數據。結束程式。
