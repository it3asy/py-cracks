# encoding: utf-8
# mssql login function
# author: 


def _login(_url, _user='sa', _pass=''):
	import pymssql,urlparse
	_up = urlparse.urlparse(_url)
	_netlocs = _up.netloc.split(':')
	_host = _netlocs[0]
	_port = int(_netlocs[1])
	_path = _up.path.strip('/')
	_server = '%s:%s' % (_host,_port)
	try:
		pymssql.connect(server=_server, user=_user, password=_pass, database=_path)
		return (200,'')
	except Exception as e:
		if e[0][0] == 18456:
			return (404, e[0][1])
		else:
			return (400, e[0][1])
