#encoding=utf-8
import GetFileInfo
import time
from DownloadFile import DownloadThread
import csv
import sys
from log import logging, cf
import os
import codecs

try:
    import requests
    from bs4 import BeautifulSoup
except Exception:
    logging.error('import [requests] or [BeautifulSoup] error')
    os._exit()

def MainFunc():
    LoginUrl = cf['url']+'/accounts/login/'
    session = requests.session()
    try:
        login_page = session.get(LoginUrl)
    except Exception as e:
        logging.error(e)
        os._exit()
        
    login_soup = BeautifulSoup(login_page.text)
    csrf_token = login_soup.input['value']
    
    data = {
            'username':cf['user'],
            'password':cf['pwd'],
            'csrfmiddlewaretoken':csrf_token
            }
    session.post(LoginUrl,data);
#     
#     try:
#         login_page = session.get(cf['url']+'/sys/seafadmin/')
#     except Exception as e:
#         logging.error(e)
#         os._exit()
#         
#     login_soup = BeautifulSoup(login_page.text)
#     csrf_token = login_soup.input['value']
#     
    
    GetFileInfo.WorkThread.session = session
    GetFileInfo.WorkThread.UrlBase = cf['url']
    GetFileInfo.WorkThread.RepoListUrl = cf['url']+'/sys/seafadmin/'
    work = GetFileInfo.WorkThread()
    work.name = 10
    work.RepoListParser(GetFileInfo.WorkThread.RepoListUrl)
    workTask = []
    for i in range(10):
        newThread = GetFileInfo.WorkThread()
        newThread.name = i
        workTask.append(newThread)
        newThread.start()
    workTask.append(work)
    work.start()
    
    for task in workTask:
        task.join()
        
#     with open('file.csv', 'w') as csvFile:
#         filedNames = ['fileName', 'owner', 'previewPath', 'downloadPath', 'tags', 'level']
#         dictWriter = csv.DictWriter(csvFile, fieldnames=filedNames)
#         dictWriter.writeheader()
#         dictWriter.writerows(GetFileInfo.WorkThread.AllFiles)
#         csvFile.close()
    with open('file.txt', 'wb') as fp:
        fp.write(codecs.BOM_UTF8)
        for item in GetFileInfo.WorkThread.AllFiles:
            fp.write('%s\t%s\t%s\t%s\t%s\t%s\n' %(item['owner'].encode('utf-8'), item['fileName'].encode('utf-8'), 
                                              item['previewPath'].encode('utf-8'), item['downloadPath'].encode('utf-8'), 
                                              item['tags'].encode('utf-8'), item['level'].encode('utf-8')))
        fp.close()

    for fileInfo in GetFileInfo.WorkThread.AllFiles:
        filePath = 'fileDir/'+fileInfo['owner']
        if os.path.exists(filePath) == False:
            try:
                os.makedirs(filePath)
            except Exception as e:
                logging.error(e)
                return

    DownloadThread.AllFiles =  GetFileInfo.WorkThread.AllFiles 
    DownloadThread.session = session
    downloadTask = []
    for i in range(16):
        newTask = DownloadThread()
        newTask.name = i
        downloadTask.append(newTask)
        newTask.start()
         
    for task in downloadTask:
        task.join()
    
if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    
    logging.debug("--------------------start getting files-------------------------")
    time.clock()
    MainFunc()
    logging.debug("Get file data end time:%s" %time.clock())
    logging.debug("--------------------finish getting files-------------------------")
