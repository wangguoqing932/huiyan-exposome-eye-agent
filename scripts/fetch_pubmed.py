#!/usr/bin/env python
import json,sys,time,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def fetch(pmid,key=""):
    url=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    if key: url+=f"&api_key={key}"
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"huiyan/1.0"})
        return urllib.request.urlopen(req,timeout=30).read().decode()
    except: return None
def main():
    print("[fetch] PubMed abstract fetcher for evidence expansion (C15)")
    return 0
if __name__=="__main__": sys.exit(main())
