#!/usr/bin/python

#This program implements n-order Markov Algorthms.
#Input some text(English or Chinese) and it generates random text. 
#If process Chinese text, you have to separate the words firstly.
#ICTCLAS can serve this purpose. andy' and 'cheung' are test files
#for English and Chinese. The result is meaningless, so it's just
#for fun. 

import string
import collections
import random

noword="\n" #sentinel
npref=2 #number of prefixes.Try 3 if generae Chinese
rand_max=10000 #max random number
filename="cheung" #the input file

def init_pref(pref):
    for i in xrange(npref):
        pref.append(noword)

def addsuf(prefixs,pref_suf_map,suf):
    if not pref_suf_map.has_key(prefixs):
        pref_suf_map[prefixs]=[suf]
    else:
        if suf not in pref_suf_map[prefixs]:
            pref_suf_map[prefixs].append(suf)

def genmap(src):
    pref=collections.deque()
    init_pref(pref)
    pref_suf_map={" ".join(pref):[]}
    for fl in src:
        li=string.split(fl)
        for suf in li:
            addsuf(" ".join(pref),pref_suf_map,suf)
            pref.popleft()
            pref.append(suf)
    addsuf(" ".join(pref),pref_suf_map,noword)
    return pref_suf_map

def generate(nwords,pref_suf_map):
    pref=collections.deque()
    init_pref(pref)
    prefix=" ".join(pref)
    wol=0
    while True:
        suf=pref_suf_map[prefix][random.randint(0,rand_max)%len(pref_suf_map[prefix])]
        if suf == noword or wol >nwords:
            break
        print suf,
        wol+=1
        pref.popleft()
        pref.append(suf)
        prefix=" ".join(pref)
        if not wol%16:print

def main():
    try:
        src=open(filename,"r")
    except:
        print "Can not open file %s" %filename
    pref_suf_map=genmap(src)
    generate(1000,pref_suf_map) #generate at most 100 words.
    src.close()

if __name__ == "__main__":
    main()
