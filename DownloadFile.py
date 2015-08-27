#encoding=utf-8
from log import logging
import threading
import os

class DownloadThread(threading.Thread):
    session = ''
    AllFiles = []
    FileLock = threading.Lock()
    
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        logging.debug('==============start new thread to download file==================')
        while True:
            if self.FileLock.acquire():
                if len(self.AllFiles) == 0:
                    self.FileLock.release()
                    break
                
                fileInfo = self.AllFiles[0]
                del self.AllFiles[0]
                self.FileLock.release()
                
                logging.debug('Thread[%s] start downloading another file[%s],left files[%d]' %(self.name, fileInfo['fileName'], len(self.AllFiles)))
                self.DownloadFunc(fileInfo)
                
        logging.debug("Thread[%s] exit" %(self.name))
        
    def DownloadFunc(self, fileInfo):
        filePath = 'fileDir/'+fileInfo['owner']
        if os.path.exists(filePath+'/'+fileInfo['fileName']):
            logging.debug("file[%s] has been downloaded" %fileInfo['fileName'])
            return
          
        try:
            fileData = self.session.get(fileInfo['downloadPath'])
        except Exception as e:
            logging.error(e)
            if self.FileLock.acquire() == True:
                self.AllFiles.append(fileInfo)
                self.FileLock.release()
            return
            
        with open(filePath+'/'+fileInfo['fileName'], "wb") as newfile:
            newfile.write(fileData.content)
            newfile.close()
            logging.debug('===download [%s] end====' %(fileInfo['fileName']))
            