# encoding: utf-8
# author: 

def _login(_url, _user='weblogic', _pass='weblogic'):
	import requests
	url = _url + '/console/j_security_check'
	data = {"j_username":_user, "j_password":_pass}
	try:
		resp = requests.post(url=url, data=data, verify=False, timeout=10)
		if resp.url.endswith('LoginForm.jsp'):
			return (404, '')
		elif 'console.portal' in resp.url:
			return (200, '')
		else:
			return (400, '')
	except Exception as e:
		return (400, str(e))
