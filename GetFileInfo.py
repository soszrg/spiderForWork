#encoding=utf-8
import threading
from log import logging
import os

try:
    from bs4 import BeautifulSoup
except Exception:
    logging.error('import [BeautifulSoup] error')
    os._exit()
    
class WorkThread(threading.Thread):
    session = ''
    AllRepos = []
    AllFiles = []
    UrlBase = ''
    RepoListUrl = '' #UrlBase+'/sys/seafadmin/'
    
    FileLock = threading.Lock()
    RepoLock = threading.Lock()
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            if self.RepoLock.acquire():
                if len(self.AllRepos) == 0:
                    self.RepoLock.release()
                    break
                
                oneRepo = self.AllRepos[0]
                del self.AllRepos[0]
                self.RepoLock.release()
                
                logging.debug("========================thread[%s] begin to get another Repo file;left Repo num[%d]=====================" %(self.name, len(self.AllRepos)))
                self.FileListParser(oneRepo['path'], oneRepo['owner'])
        
        logging.debug("*****thread[%s] exit" %(self.name))
    
    def RepoListParser(self, url):
        try:
            repoListHtml = self.session.get(url)
        except Exception as e:
            logging.error(e)
            return
        repoListHtmlSoup = BeautifulSoup(repoListHtml.text, 'html5lib')
        repoListTables = repoListHtmlSoup.table
        
        if repoListTables == None:
            return
        
        for oneTr in repoListTables.select('tr'):
            tds = oneTr.find_all('td')
            if len(tds) == 0:
                continue
            
            repoPathTd = tds[0]
            repoOwnerTd = tds[2]
            newRepo = {}
            newRepo['path'] = self.UrlBase+repoPathTd.a['href']
            newRepo['owner'] = repoOwnerTd.a.get_text()
            
            self.AllRepos.append(newRepo)
            
        nextPage = repoListHtmlSoup.find('div', id="paginator")
        if len(nextPage) == 0:
            return 0
        
        page_a = nextPage.select('a')
        for one_a in page_a:
            if repr(one_a.get_text()) == repr(u'下一页'):
                pageUrl = one_a['href'] 
                self.RepoListParser(self.RepoListUrl+pageUrl)
            
    def FileListParser(self, url, fileOwner):
        try:
            fileListHtml = self.session.get(url)
        except Exception as e:
            logging.error(e)
            newRepo = {}
            newRepo['path'] = url
            newRepo['owner'] = fileOwner
            if self.FileLock.acquire() == True:
                self.AllRepos.append(newRepo)
                self.FileLock.release()
            
        fileListHtmlSoup = BeautifulSoup(fileListHtml.text, 'html5lib')

        fileListTables = fileListHtmlSoup.table
        if fileListTables == None:
            return 0
        fileListTrs = fileListTables.select('tr')
        if len(fileListTrs) == 0:
            return 0
        
        for oneTr in fileListTrs[1:]:
#             print "level--->%s" %oneTr.select('select[class="file-level-type-select"]')[0].option['value']#.select('option["selected="selected"]')
            previewA = oneTr.select('span[class="dirent-name"]')[0].select('a')[0]
            previewPath = previewA['href']
            pathList = repr(previewPath).split('/')
            if len(pathList) < 4:
                continue
            path = pathList[1]+'/'+pathList[2]+'/'+pathList[3]
            
            if path == 'sys/seafadmin/repo':
#                 print 'this is a dir'
                self.FileListParser(self.UrlBase+previewPath, fileOwner)
            else:
#                 print 'find a new file'
                fileName = previewA.get_text()
                downloadPath = oneTr.select('a')[2]['href']
                newFile = {}
                newFile['fileName'] = fileName
                newFile['owner'] = fileOwner
                newFile['previewPath'] = self.UrlBase+previewPath
                newFile['downloadPath'] = self.UrlBase+downloadPath
                tagSpan = oneTr.select('span[class="file-tags"]')
                level = oneTr.select('select[class="file-level-type-select"]')[0].select('option[selected="selected"]')[0]['value']
                newFile['level'] = level
                if len(tagSpan) > 0:
                    newFile['tags'] = tagSpan[0].get_text()
                else:
                    newFile['tags'] = ''
                    
                if self.FileLock.acquire():
                    self.AllFiles.append(newFile)
                    self.FileLock.release()
