#coding: utf-8

import optparse
import urlparse
import Queue
import threading
import socket
import time
import sys,os,inspect

ROOT = os.path.abspath(os.path.dirname(inspect.getfile(inspect.currentframe())))
sys.path.append(ROOT+'/modules')
sys.path.append(ROOT+'/midwares')

g_dictroot = ROOT + '/dict/'
g_queue = Queue.Queue()
g_retry = 2
g_nogreedy = False
g_count = 0

def load_targets(_file=None,_target=None):
	if _target:
		g_queue.put(_target)
	elif file:
		for a in [x.strip() for x in file(_file,'r')]:
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
			_clear = ' ' * 40
			sys.stdout.write('{0}  {1} [-1] {2}\n'.format(_url,_places,_clear))
			sys.stdout.flush()
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
		_clear = ' ' * 10
		_places = ' '
		for u in _user_list:
			if _break:
				break
			for p in _pass_list:
				if _break:
					break
				g_count = g_count + 1
				_retry = g_retry
				while _retry:
					p = p.replace('%user%',u)
					p = p.replace('%null%','')
					_places = ' ' * (35-len(_url))
					_status,_text = check_login(_url=_url,_user=u,_pass=p)
					#import random
					#_status = random.choice([200,400,404,400,404,400,404,400,400,404,404,404])
					_clear = ' ' * (50-len(u+'/'+p))
					if _status == 400:
						_retry = _retry - 1
						if _retry == 0:
							sys.stdout.write('{0} {1}  [{4}] {5}\n'.format(_url,_places,u,p,_status,_clear))
							sys.stdout.flush()
							_break = True
						else:
							sys.stdout.write('{0} {1}  [{4}] "{2}/{3}" {5}\r'.format(_url,_places,u,p,_status,_clear))
							sys.stdout.flush()
							time.sleep(3)
					else:
						_retry = 0
						if _status == 200:
							sys.stdout.write('{0} {1}  [{4}] "{2}/{3}" {5}\n'.format(_url,_places,u,p,_status,_clear))
							sys.stdout.flush()
							if g_nogreedy:
								_break = True
						else:
							sys.stdout.write('{0} {1}  [{4}] "{2}/{3}" {5}\r'.format(_url,_places,u,p,_status,_clear))
							sys.stdout.flush()



if __name__ == '__main__':
	parser = optparse.OptionParser('usage: %prog [options] url')
	parser.add_option('-t', metavar = 'THREAD NUMS', dest='_threads_num', default=10, type='int', help='Number of threads. default=1')
	parser.add_option('-m', metavar = 'MIDWARE', dest='_midware', default='', type='string', help='midware[weblogic|tomcat|jboss|...]')
	parser.add_option('-l', metavar='LOGIN', dest='_login', default=None, type='string', help='login with LOGIN name')
	parser.add_option('-p', metavar='PASS', dest='_pass', default=None, type='string', help='try password PASS')
	parser.add_option('-L', metavar='FILE', dest='_login_dict', default=None, type='string', help='load several logins from FILE')
	parser.add_option('-P', metavar='FILE', dest='_pass_dict', default=None, type='string', help='load several passwords from FILE')
	parser.add_option('--targets', metavar='FILE', dest='_targets', default=None, type='string', help='load targets from FILE')
	parser.add_option('--nogreedy', dest='_nogreedy', action="store_true", help='defalt greedy')
	parser.add_option('--timeout', metavar='SECOENDS', dest='_timeout', default=20, type='int', help='socket timeout')
	parser.add_option('--go', dest='_go', action="store_true", help='defalt False')
	(_options, _args) = parser.parse_args()

	if _options._targets:
		_tars = load_targets(_file=_options._targets)
	else:
		_tars = load_targets(_target = _args[0])

	if _options._nogreedy:
		g_nogreedy = _options._nogreedy

	if _options._timeout:
		socket.setdefaulttimeout(_options._timeout)

	print '---- %s targets -----' % (_tars)

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

	sys.stdout.write('\r' + '----%s scans done! ----'%g_count + ' '*60+'\n')

