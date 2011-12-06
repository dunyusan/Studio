#!/usr/bin/python

#Multithreading Web Crawler.
#This crawler can be used to fetch the Qzone articles.
#But you can change the URL pattern to fetch other resource
#of other Websites.
#
#There are so many problems in this program.
#It should be improved later, for instance, store the data
#into Database.
#
#Author: Usin Y.S. Deng.

import urllib2,urlparse
import re,os
import threading,Queue

#QQid='394118384'#Fetch My Qzone.
QQid='622006057'#Fetch Steven Cheung's Qzone.
LOCATION='http://b.qzone.qq.com'
PATH='/cgi-bin/blognew/.*'
QUERY='hostuin=%s&r=0&idm=imgcache.qq.com&bdm=b.qzone.qq.com&mdm=m.qzone.qq.com'%QQid
FRAGMENT=''
START=LOCATION+'/cgi-bin/blognew/simpleqzone_blog_title'+'?'+QUERY

#You can define whatever pattern you'd like to match.
#But must specify both the <abs> part and <rel> part
#So you just can change RELPATH and ABSPATH
RELPATH=r'%s\?%s.*?(?=\1)'%(PATH,QUERY)
ABSPATH=r'%s%s'%(LOCATION,RELPATH)
PATTERN=r'href=(["\'])((?P<abs>%s)|(?P<rel>%s))\1'%(ABSPATH,RELPATH)


class Murl(object):
    def __init__(self,location,path,query,fragment,pattern):
        self.location=location
        self.path=path
        self.query=query
        self.fragment=fragment
        self.pattern=re.compile(pattern)


class Spider(threading.Thread):
    '''One Spider is one thread'''
    def __init__(self,match_url,global_things,url_queue,tid,mkname_func):
        threading.Thread.__init__(self)
        self.murl=match_url
        self.mkname=mkname_func
        self.gt=global_things
        self.urlqueue=url_queue
        self.tid=tid
        self.setDaemon(1)
        self.start()

    def store(self,data,name):
        #Change this method in order to store into DataBase later.
        try:
            op=open(name,"w")
            op.write(data)
            op.close()
        except:
            print "Something wrong while processing file: %s"%filename


    def geturl(self,url,filename):
        try:
            fp=urllib2.urlopen(url)
        except:
            print "Thread-%d:Can't open %s" %(self.tid,url)
            return
        s=fp.read()
        if s:
            if filename:
                self.store(s,filename)
            for mo in self.murl.pattern.finditer(s):
                murl=mo.group('abs')
                if not murl:
                    murl=self.murl.location+mo.group('rel')
                if (murl not in self.gt['pool']) and (murl not in \
                        self.gt['garbage']):
                    self.gt['lock'].acquire()
                    self.gt['pool'].append(murl)
                    self.urlqueue.put(murl)
                    self.gt['lock'].release()
        fp.close()

    def run(self):
        while 1:
            url=self.urlqueue.get()
            self.gt['pool'].pop(0)
            self.gt['garbage'].append(url)
            print "Thread-%d Try to get %s"% (self.tid,url)
            try:
                fl=self.mkname(url)
                self.geturl(url,fl)
                if fl:
                    self.gt['lock'].acquire()
                    self.gt['total']+=1
                    print "Thread-%d reports: %d downloaded! %d left"\
                            %(self.tid,self.gt['total'],len(self.gt['pool']))
                    self.gt['lock'].release()
            except:
                print "Bad URL!",len(self.gt['pool']),"URLs left in pool."
            finally:
                self.urlqueue.task_done()


class Spiders(object):
    '''Collect thread_num Spiders to form a Multithreading Web Crawler'''
    def __init__(self,start_url,match_url,thread_num):
        self.murl=match_url
        self.queue=Queue.Queue()
        self.queue.put(start_url)
        self.global_things={'pool':[start_url],'garbage':[],'lock':threading.Lock(),'total':0}
        self.thnum=thread_num

    def mkname(self,url):
        #Named the fetched objects.I use the blogid in the query of the URL.
        p=re.compile(r'blogid=(\d+)')
        ll=p.findall(url)
        if ll:
            return ll[0]
        else:
            return None

    def fetch(self):
        for i in range(self.thnum):
            Spider(self.murl,self.global_things,self.queue,i+1,self.mkname)
        self.queue.join()

if __name__ == "__main__":
    murl=Murl(LOCATION,PATH,QUERY,FRAGMENT,PATTERN)
    spiders=Spiders(START,murl,5)
    spiders.fetch()
