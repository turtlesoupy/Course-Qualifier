from fabric.api import *

env.roledefs = {'dev': ['dev.fs.uwaterloo.ca'], 'prod': ['www-app.fs.uwaterloo.ca']}
deploy_to = {'dev': '/srv/python-apps/dev-course.feds.ca', 'prod': '/srv/course.feds.ca' }

repository = 'https://github.com/feds-sdn/Course-Qualifier.git'
source_dir = 'Course-Qualifier' # Must be the app name

def _annotate_hosts_with_ssh_config_info(): #{{{
	from os.path import expanduser
	from paramiko.config import SSHConfig

	def hostinfo(host, config):
		hive = config.lookup(host)
		if 'hostname' in hive:
			host = hive['hostname']
		if 'user' in hive:
			host = '%s@%s' % (hive['user'], host)
		if 'port' in hive:
			host = '%s:%s' % (host, hive['port'])
		return host

	try:
		config_file = file(expanduser('~/.ssh/config'))
	except IOError:
		pass
	else:
		config = SSHConfig()
		config.parse(config_file)
		keys = [config.lookup(host).get('identityfile', None)
			for host in env.hosts]
		env.key_filename = [expanduser(key) for key in keys if key is not None]
		env.hosts = [hostinfo(host, config) for host in env.hosts]

		for role, rolehosts in env.roledefs.items():
			env.roledefs[role] = [hostinfo(host, config) for host in rolehosts]

_annotate_hosts_with_ssh_config_info() #}}}


def pull():
	git_dir = deploy_to[env.roles[0]] + '/' + source_dir
	with settings(warn_only=True):
		result = sudo('cd ' + git_dir + ' && git pull')
	if result.failed:
		with cd(deploy_to[env.roles[0]]):
			sudo('git clone ' + repository + ' ' + git_dir)


def install():
	with cd(deploy_to[env.roles[0]]):
		sudo('bin/pip install --upgrade ' + source_dir)

def restart():
	with cd(deploy_to[env.roles[0]]):
		sudo('touch dispatch.wsgi')

def deploy():
	pull()
	install()
	restart()

def setup():
	with cd(deploy_to[env.roles[0]]):
		sudo('bin/pip install -r ' + source_dir + '/requirements.txt')
		sudo('bin/paster setup-app config.ini')
