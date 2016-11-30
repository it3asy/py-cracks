#coding: utf-8

import optparse
import urlparse
import Queue
import threading
import socket
import time,datetime
import sys,os,inspect

ROOT = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
sys.path.append(ROOT+'/modules')
sys.path.append(ROOT+'/midwares')

g_dictroot = ROOT + '/dict/'
g_queue = Queue.Queue()
g_retry = 2
g_nogreedy = False
g_count = 0
g_log = '/dev/null'

def load_targets(_file=None,_target=None):
	if _target:
		g_queue.put(_target)
	elif file:
		for a in [x.strip() for x in file(_file,'r')]:
			if len(a)>4:
				g_queue.put(a)
	return g_queue.qsize()

def load_dicts(_item=None,_dict=None):
	_dicts = []
	if _item == None:
		_file = g_dictroot + _dict
		for i in file(_file,'r').readlines():
			_dicts.append(i.strip())				
	else:
		_dicts.append(_item)
	return _dicts

def exist_dict(_dict):
	_file = g_dictroot + _dict
	try:
		file(_file,'r')
		return True
	except:
		return False

def load_module(_module):
	_login = None
	try:
		_login = getattr(__import__(_module), '_login')
	except:
		pass
	return _login



def scan_thread(_options):
	global g_count
	while g_queue.qsize()>0:
		_url = g_queue.get()
		if _options._midware:
			_module = _options._midware
		else:
			_module = urlparse.urlparse(_url).scheme
		check_login = load_module(_module)
		if not check_login:
			_places = ' ' * (35 - len(_url))
			_log = '{0}  {1} [-1]'.format(_url,_places)
			file(g_log,'a').write(_log+'\n')
			sys.stdout.write(_log+'\r')
			sys.stdout.flush()
			sys.stdout.write(' '*len(_log)+'\r')
			continue

		_dict = _options._login_dict
		if not _dict:
			_dict = '{0}_user'.format(_module)
		if not exist_dict(_dict):
			_dict = 'common_user'
		_user_list = load_dicts(_item=_options._login,_dict=_dict)

		_dict=_options._pass_dict
		if not _dict:
			_dict = '{0}_pass'.format(_module)
		if not exist_dict(_dict):
			_dict = 'common_pass'
		_pass_list = load_dicts(_item=_options._pass,_dict=_dict)

		_break = False
		_break_pass  = False
		_places = ' '
		for u in _user_list:
			if _break:
				break
			for p in _pass_list:
				if _break:
					break
				if _break_pass:
					break
				g_count = g_count + 1
				_retry = g_retry
				while _retry:
					p = p.replace('%user%',u)
					p = p.replace('%null%','')
					_places = ' ' * (35-len(_url))

					_status,_text = check_login(_url=_url,_user=u,_pass=p)
					#import random
					#time.sleep(random.choice([0.1,0.2,0.3,1,3,0.7,0.2,0.1]))
					#_status = random.choice([200,400,404,400,404,400,404,400,400,404,404,404])

					if _status == 400:
						_retry = _retry - 1
						if _retry == 0:
							_log = '{0} {1}  [{4}]'.format(_url,_places,u,p,_status)
							file(g_log,'a').write(_log+'\n')
							sys.stdout.write(_log+'\r')
							sys.stdout.flush()
							sys.stdout.write(' '*len(_log)+'\r')
							_break = True
						else:
							_log = '{0} {1}  [{4}] "{2}/{3}"\r'.format(_url,_places,u,p,_status)
							sys.stdout.write(_log)
							sys.stdout.flush()
							sys.stdout.write(' '*len(_log)+'\r')
							time.sleep(3)
					else:
						_retry = 0
						if _status == 200:
							_log = '{0} {1}  [{4}] "{2}/{3}"'.format(_url,_places,u,p,_status)
							file(g_log,'a').write(_log+'\n')
							sys.stdout.write(_log+'\n')
							sys.stdout.flush()
							if g_nogreedy:
								_break = True
							_break_pass = True
						else:
							_log = '{0} {1}  [{4}] "{2}/{3}"'.format(_url,_places,u,p,_status)
							sys.stdout.write(_log+'\r')
							sys.stdout.flush()
							sys.stdout.write(' '*len(_log)+'\r')



if __name__ == '__main__':
	parser = optparse.OptionParser('usage: %prog [options] url --go')
	parser.add_option('-t', metavar = 'THREAD NUMS', dest='_threads_num', default=10, type='int', help='Number of threads. default=1')
	parser.add_option('-m', metavar = 'MIDWARE', dest='_midware', default='', type='string', help='midware[weblogic|tomcat|jboss|...]')
	parser.add_option('-l', metavar='LOGIN', dest='_login', default=None, type='string', help='login with LOGIN name')
	parser.add_option('-p', metavar='PASS', dest='_pass', default=None, type='string', help='try password PASS')
	parser.add_option('-L', metavar='FILE', dest='_login_dict', default=None, type='string', help='load several logins from FILE')
	parser.add_option('-P', metavar='FILE', dest='_pass_dict', default=None, type='string', help='load several passwords from FILE')
	parser.add_option('--log', metavar='FILE', dest='_log', default=None, type='string', help='log to FILE')
	parser.add_option('--targets', metavar='FILE', dest='_targets', default=None, type='string', help='load targets from FILE')
	parser.add_option('--nogreedy', dest='_nogreedy', action="store_true", help='defalt greedy')
	parser.add_option('--timeout', metavar='SECOENDS', dest='_timeout', default=20, type='int', help='socket timeout')
	parser.add_option('--go', dest='_go', action="store_true", help='defalt False')
	(_options, _args) = parser.parse_args()

	_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	if _options._log:
		g_log = _options._log

	if _options._targets:
		_tars = load_targets(_file=_options._targets)
	else:
		_tars = load_targets(_target = _args[0])

	if _options._nogreedy:
		g_nogreedy = _options._nogreedy

	if _options._timeout:
		socket.setdefaulttimeout(_options._timeout)

	_log = '\n------------%s: start, %s targets ---------------------' % (_start,_tars)
	file(g_log,'a').write(_log+'\n')
	print _log

	if _options._go:
		_threads = []
		_thread_num = _options._threads_num
		for i in range(_thread_num):
			t = threading.Thread(target=scan_thread,args=(_options,))
			_threads.append(t)
		for t in _threads:
			t.start()
		for t in _threads:
			t.join()
	else:
		while g_queue.qsize()>0:
			print g_queue.get()

	_end = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	_log = '------------%s: done, %s scans ------------------------\n'%(_end, g_count)
	file(g_log,'a').write(_log)
	print _log

