#encoding = utf-8

import logging
import ConfigParser
 
cf = {'url':'http:/10.3.31.114', 'user':'', 'pwd':'', 'debug':'False'}
def ReadConfig():
    
    config = ConfigParser.ConfigParser()
    
    try:
        config.read('ini')
    except Exception as e:
        logging.error(e)
        
    try:
        cf['url'] = config.get('general', 'url')
    except:
        pass
    try:
        cf['user'] = config.get('general', 'user')
    except Exception:
        pass
    try:
        cf['pwd'] = config.get('general', 'pwd')
    except Exception:
        pass
    try:
        cf['debug'] = config.get('general', 'debug')
    except Exception:
        pass

ReadConfig()
debug = cf['debug']
fmt = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s=====> %(message)s'

if debug == 'False':
    logging.basicConfig(level=logging.DEBUG,
                        format=fmt,
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='log.txt',
                        filemode='w')
else:
    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter(fmt))
    
    log.addHandler(ch)
    
    logging = log
     
    
