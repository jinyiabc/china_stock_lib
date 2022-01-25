
import io, os, sys, config
cfg = config.Config('test_config0.cfg')

cfg['b']
cfg['c.d']

cfg['christmas_morning']

cfg['error']


cfg = config.Config('main.cfg')

cfg['redirects.freeotp.url']
cfg['logging.root.level']
cfg['logging.handlers.error.filename']
cfg['logging.handlers.error.mode']

import configparser
config = configparser.ConfigParser()
config.read('wind.cfg')
config.sections()
config['bitbucket.org']['User']
int(config['topsecret.server.com']['port'])