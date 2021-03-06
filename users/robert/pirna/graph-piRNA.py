#!/usr/bin/env python
import os
import sys
import inspect
import re
import argparse
import random
import math
import collections
import fileinput
prog = re.compile(r"(\d+)([MISDHN])")




parser = argparse.ArgumentParser(description="""           
Description
-----------
Summary statistics
""",formatter_class=argparse.RawDescriptionHelpFormatter,
epilog="""
miRNA: 21-23nt
piRNA: 23-28nt


Authors
-------
    Robert Kofler
""")
parser.add_argument('--sam', type=argparse.FileType('r'), default=None,dest="sam", required=True, help="A sam file")
parser.add_argument("--min-mq", type=int, required=False, dest="minmq", default=0, help="min mapping quality")
parser.add_argument("--max-mm", type=int, required=False, dest="maxmm", default=10, help="max mismatches")
parser.add_argument("--sample-id", type=str, required=True, dest="sid", default=10, help="the sample id")
args = parser.parse_args()
minmq=args.minmq
maxmm=args.maxmm


mistart=21
miend=23
pistart=23
piend=28

tecount=collections.defaultdict(lambda:0)
tesum=0
mirnacount=0
trnacount=0
rrnacount=0


ps=collections.defaultdict(lambda:0)
pas=collections.defaultdict(lambda:0)

def get_end(start,cig):
     
     result = re.findall(prog,cig)
     alignmentleng=0
     for count,cigchar in result:
          count=int(count)
          if cigchar=="M" or cigchar=="D":
               alignmentleng+=count
     
     end=start+alignmentleng-1
     return end
          


for line in args.sam:
     """
0         1         2              3    4         5    6         7      8            9                        10                  11
r1	16	M14653_te	172	70	23M	*	0	0	ATGTCGAGTTTCGTGCCGAATAA	FFFFFFFFFFFFFFFFFFBBBBB	PG:Z:novoalign	AS:i:0	UQ:i:0	NM:i:0	MD:Z:23
r2	0	M14653_te	240	70	27M	*	0	0	AACAGCTGCGGAATCGCACCGAATGCT	BBBBBFFFFFBFFFFFFFFFFFFFFFF	PG:Z:novoalign	AS:i:0	UQ:i:0	NM:i:0	MD:Z:27
     """
     a=line.rstrip("\n").split("\t")
     
     # discard unmapped
     flag=int(a[1])
     if flag & 0x004 > 0:
          continue
     
     # discard low mapping quality
     mq=int(a[4])
     if mq< minmq:
          continue
     
     # discard mismatch
     mm=0
     tmp=a[11]
     b=tmp.split(" ")
     for bt in b:
          if bt.startswith("NM:i:"):
               mm=int(bt[5:])
     if(mm>maxmm):
          continue  
     
     
     ref=a[2]
     readlen=len(a[9])
     if ref.endswith("_te"):
          teseq=ref[:-3]
          if readlen<pistart or readlen>piend:
               continue
          if teseq=="PPI251":
               start=int(a[3])
               if flag& 0x10:
                    # reverse complement if flag 0x10 is set
                    end=get_end(start,a[5]) # for reverse complements get the end
                    pas[end]+=1
               else:
                    ps[start]+=1
                    
     elif ref.endswith("_miRNA"):
          if readlen<mistart or readlen>mistart:
               continue
          mirnacount+=1
     elif ref.endswith("_rRNA") or  ref.endswith("_rRNA;"):
          rrnacount+=1
     elif ref.endswith("_tRNA"):
          trnacount+=1
     elif  ref.endswith("_snoRNA;") or ref.endswith("_snoRNA") or ref.endswith("_snRNA;") or ref.endswith("_snRNA") or ref.endswith("_mRNA"):
          pass
     else:
          raise Exception("Unknown sequence end "+ ref)

# normalize
for start in ps.keys():
     count= ps[start]
     normcount=float(count)/float(mirnacount)
     normcount*=1000000
     ps[start]=normcount


for start in pas.keys():
     count=pas[start]
     normcount=float(count)/float(mirnacount)
     normcount*=1000000
     pas[start]=normcount


ppsig=collections.defaultdict(lambda:0)

# compute ping-pong signatures
for start in pas.keys():
     # start with antisense:
     assig=pas[start]
     sensestart=start-9 # sift of Ago3
     sensesig=0.0
     if(sensestart in ps):
          sensesig=ps[sensestart]
     pps=assig*sensesig
     if pps>0.0:
          ppsig[start]=pps



sid=args.sid
for start,count in ps.items():
     normcount=float(count)/float(mirnacount)
     normcount*=1000000
     print "{0}\t{1}\t{2}\t{3}".format(sid,"s",start,normcount)

for start,count in pas.items():
     print "{0}\t{1}\t{2}\t{3}".format(sid,"s",start,-count)

for start,count in ppsig.items():
     print "{0}\t{1}\t{2}\t{3}".format(sid,"pp",start,count)


#tecount=collections.defaultdict(lambda:0)
#tesum=0
#mirnacount=0
#trnacount=0
#rrnacount=0
#teld=collections.defaultdict(lambda:0)
#mirnald=collections.defaultdict(lambda:0)
#trnald=collections.defaultdict(lambda:0)
#rrnald=collections.defaultdict(lambda:0)

