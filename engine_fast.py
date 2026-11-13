import json,os,sys,time,urllib.request
sys.setrecursionlimit(6000)

U=os.environ["MAKEFUN_ENV_URL"]
V=(0,100,320,330,500,900,0)
KN=(-33,-31,-18,-14,14,18,31,33)
KG=(-17,-16,-15,-1,1,15,16,17)
BD=(-17,-15,15,17)
RD=(-16,-1,1,16)
QD=BD+RD

def tbls():
    T=[]
    for t in range(7):
        r=[]
        for i in range(64):
            f=i&7;g=i>>3;c=min(f,7-f)+min(g,7-g)
            if t==0:r.append((g*8-30 if g>1 else 0)+(5 if f in(3,4) else 0))
            elif t==1:r.append(6*c-20)
            elif t==2:r.append(4*c-8)
            elif t==3:r.append((15 if g==6 else 0)+(5 if g==0 and f in(3,4) else 0))
            elif t==4:r.append(2*c-6)
            elif t==5:r.append((20,25,10,0,0,10,25,20)[f] if g==0 else max(-50,-15*g))
            else:r.append(8*c-30)
        T.append(r)
    return T
P=tbls()
SE=[0,0]
NM=0
def pv(t,i):
    p=t if t>0 else -t
    return P[5 if p==6 else p-1][(i>>4)*8+(i&7) if t>0 else ((7-(i>>4))*8+(i&7))]
def put(i,t,k):
    global NM
    p=abs(t)
    SE[0 if t>0 else 1]+=k*(V[p]+pv(p,i))
    if 1<p<6:NM+=k*V[p]

KNT={}
KGT={}
for s in range(128):
    if s&0x88:continue
    KNT[s]=[n for n in (s+o for o in KN) if not n&0x88]
    KGT[s]=[n for n in (s+o for o in KG) if not n&0x88]

PC=[0]*128
W=[]
B=[]
KW=4
KB=116
side=1
epc=-1
cas=0
nodes=0
CAP=8000

def sq64(i):
    return (i>>4)*8+(i&7)

def fen(f):
    global PC,W,B,KW,KB,side,epc,cas,SE,NM
    PC=[0]*128;W=[];B=[]
    p=f.split()
    for r,row in enumerate(p[0].split("/")):
        c=0
        for ch in row:
            if ch.isdigit():c+=int(ch)
            else:
                s=(7-r)*16+c
                v="pnbrqk".index(ch.lower())+1
                if ch.isupper():
                    PC[s]=v;W.append(s)
                    if v==6:KW=s
                else:
                    PC[s]=-v;B.append(s)
                    if v==6:KB=s
                c+=1
    side=1 if p[1]=="w" else -1
    cas=("K" in p[2])*1|("Q" in p[2])*2|("k" in p[2])*4|("q" in p[2])*8
    epc=-1 if p[3]=="-" else (int(p[3][1])-1)*16+"abcdefgh".index(p[3][0])
    SE=[0,0];NM=0
    for i in W:
        q=PC[i];SE[0]+=V[q]+pv(q,i)
        if 1<q<6:NM+=V[q]
    for i in B:
        q=-PC[i];SE[1]+=V[q]+pv(q,i)
        if 1<q<6:NM+=V[q]

def att(s,by):
    b=PC
    p2=by*2
    for n in KNT[s]:
        if b[n]==p2:return 1
    p6=by*6
    for n in KGT[s]:
        if b[n]==p6:return 1
    if by>0:
        for o in (-15,-17):
            n=s+o
            if not n&0x88 and b[n]==1:return 1
    else:
        for o in (15,17):
            n=s+o
            if not n&0x88 and b[n]==-1:return 1
    p3=by*3;p5=by*5;p4=by*4
    for o in BD:
        n=s+o
        while not n&0x88:
            q=b[n]
            if q:
                if q==p3 or q==p5:return 1
                break
            n+=o
    for o in RD:
        n=s+o
        while not n&0x88:
            q=b[n]
            if q:
                if q==p4 or q==p5:return 1
                break
            n+=o
    return 0

def gen(cap=0):
    out=[]
    b=PC
    mine=W if side>0 else B
    for i in mine:
        p=b[i]
        t=p if p>0 else -p
        m=p>0
        if t==1:
            d=16 if m else -16
            n=i+d
            if not n&0x88 and b[n]==0:
                if n>111 or n<8:out.append((i<<7)|n|(5<<14))
                elif not cap:
                    out.append((i<<7)|n)
                    if i>>4==(1 if m else 6):
                        x=n+d
                        if b[x]==0:out.append((i<<7)|x)
            for o in (d-1,d+1):
                n=i+o
                if n&0x88:continue
                q=b[n]
                if q:
                    if (q>0)!=m:out.append((i<<7)|n|((5<<14) if (n>111 or n<8) else 0))
                elif n==epc:out.append((i<<7)|n)
        elif t==6:
            for n in KGT[i]:
                q=b[n]
                if q==0 or (q>0)!=m:out.append((i<<7)|n)
            if cap:continue
            if m and cas:
                if cas&1 and b[5]==0 and b[6]==0 and b[7]==4 and not att(4,-1) and not att(5,-1) and not att(6,-1):out.append((4<<7)|6)
                if cas&2 and b[3]==0 and b[2]==0 and b[1]==0 and b[0]==4 and not att(4,-1) and not att(3,-1) and not att(2,-1):out.append((4<<7)|2)
            if not m and cas:
                if cas&4 and b[117]==0 and b[118]==0 and b[119]==-4 and not att(116,1) and not att(117,1) and not att(118,1):out.append((116<<7)|118)
                if cas&8 and b[115]==0 and b[114]==0 and b[113]==0 and b[112]==-4 and not att(116,1) and not att(115,1) and not att(114,1):out.append((116<<7)|114)
        elif t==2:
            for n in KNT[i]:
                q=b[n]
                if q==0 or (q>0)!=m:out.append((i<<7)|n)
        else:
            for o in (BD if t==3 else RD if t==4 else QD):
                n=i+o
                while not n&0x88:
                    q=b[n]
                    if q:
                        if (q>0)!=m:out.append((i<<7)|n)
                        break
                    if not cap:out.append((i<<7)|n)
                    n+=o
    return out

def rm(L,s):
    for i in range(len(L)):
        if L[i]==s:
            L[i]=L[-1];L.pop();return

def mk(m):
    global epc,cas,KW,KB,side,SE,NM
    b=PC
    f=(m>>7)&127;t=m&127;pr=m>>14
    p=b[f];c=b[t]
    e=epc
    u=(f,t,c,epc,cas,0,SE[0],SE[1],NM)
    put(f,p,-1)
    if c:put(t,c,-1)
    epc=-1
    put(t,(pr if p>0 else -pr) if pr else p,1)
    b[t]=p if not pr else (pr if p>0 else -pr)
    b[f]=0
    L=W if p>0 else B
    rm(L,f)
    if c:
        rm(B if p>0 else W,t)
    elif t==e and e>=0:
        q=t+16 if p>0 else t-16
        u=(f,t,c,e,cas,q,SE[0],SE[1],NM)
        put(q,(1 if p>0 else -1),-1)
        b[q]=0
        rm(B if p>0 else W,q)
    L.append(t)
    if abs(p)==6:
        if p>0:KW=t;cas&=~3
        else:KB=t;cas&=~12
        if abs(t-f)==2:
            a=(6,5,7) if t==6 else (2,3,0) if t==2 else (118,117,119) if t==118 else (114,115,112)
            put(a[2],b[a[2]],-1);put(a[1],b[a[2]],1)
            b[a[1]]=b[a[2]];b[a[2]]=0
            rm(L,a[2]);L.append(a[1])
    if abs(p)==1 and abs(t-f)==32:epc=(f+t)//2
    if f in(0,112):cas&=~2 if f==0 else ~8
    if f in(7,119):cas&=~1 if f==7 else ~4
    if t in(0,112):cas&=~2 if t==0 else ~8
    if t in(7,119):cas&=~1 if t==7 else ~4
    side=-side
    return u

def um(u):
    global epc,cas,KW,KB,side,SE,NM
    b=PC
    f,t,c,e,k,q,s0,s1,n0=u
    SE[0]=s0;SE[1]=s1;NM=n0
    p=b[t]
    if abs(p)==6 and abs(t-f)==2:
        a=(6,5,7) if t==6 else (2,3,0) if t==2 else (118,117,119) if t==118 else (114,115,112)
        L=W if p>0 else B
        rm(L,a[1]);b[a[2]]=b[a[1]];b[a[1]]=0;L.append(a[2])
    L=W if p>0 else B
    rm(L,t)
    b[f]=p
    L.append(f)
    if c:
        b[t]=c
        (W if c>0 else B).append(t)
    else:b[t]=0
    if q:
        b[q]=-1 if p>0 else 1
        (W if p<0 else B).append(q)
    if p==6:KW=f
    if p==-6:KB=f
    epc=e;cas=k;side=-side

def chk():
    return att(KW if side>0 else KB,-side)

def il():
    return att(KB if side>0 else KW,side)

def nonpawn():
    for i in (W if side>0 else B):
        if 1<abs(PC[i])<6:return 1
    return 0

def null():
    global side,epc
    e=epc;epc=-1;side=-side
    return e

def unull(e):
    global side,epc
    epc=e;side=-side

def ev():
    s=SE[0]-SE[1]
    n=min(NM,7400)
    k=7400-n
    s+=(P[5][(KW>>4)*8+(KW&7)]*n+P[6][(KW>>4)*8+(KW&7)]*k)//7400
    s-=(P[5][(KB>>4)*8+(KB&7)]*n+P[6][(KB>>4)*8+(KB&7)]*k)//7400
    return s*side

class Stop(Exception):pass

KIL=[[0,0] for _ in range(64)]
HIS={}

def order(ms,d):
    r=[]
    b=PC
    k=KIL[d]
    for m in ms:
        p=b[(m>>7)&127];c=b[m&127]
        if c:v=V[c if c>0 else -c]*100-V[p if p>0 else -p]
        elif m>>14:v=9000
        elif m==k[0]:v=8000
        elif m==k[1]:v=7000
        else:v=HIS.get(m,0)
        r.append((v,m))
    r.sort(key=lambda a:-a[0])
    return [m for v,m in r]

def qs(a,bt,d=0):
    global nodes
    nodes+=1
    if d>12:return ev()
    if nodes>CAP:raise Stop
    if chk():
        if d>8:return ev()
        any=0
        for m in order(gen(),0)[:20]:
            u=mk(m)
            if not il():
                any=1
                v=-qs(-bt,-a,d+1)
                um(u)
                if v>a:
                    a=v
                    if a>=bt:break
            else:um(u)
        return -29990 if not any else a
    st=ev()
    if st>=bt:return st
    if st>a:a=st
    for m in order(gen(1),0)[:14]:
        u=mk(m)
        if not il():
            v=-qs(-bt,-a,d+1)
            um(u)
            if v>a:
                a=v
                if a>=bt:break
        else:um(u)
    return a

def srch(d,a,bt):
    global nodes
    nodes+=1
    if nodes>CAP:raise Stop
    if d<1:return qs(a,bt)
    ms=gen()
    if d>2 and not chk() and nonpawn() and bt<29000:
        e=null()
        v=-srch(d-3,-bt,-bt+1)
        unull(e)
        if v>=bt:return bt
    best=-99999;i=0;any=0
    for m in order(ms,d):
        cap=PC[m&127];qui=not cap and not m>>14
        u=mk(m)
        if il():
            um(u);continue
        any=1
        if i>3 and d>3 and qui:
            v=-srch(d-2,-a-1,-a)
            if v>a:v=-srch(d-1,-bt,-a)
        else:v=-srch(d-1,-bt,-a)
        um(u)
        i+=1
        if v>best:best=v
        if v>a:
            a=v
            if a>=bt:
                if qui and m not in KIL[d]:
                    KIL[d][1]=KIL[d][0];KIL[d][0]=m
                if qui:HIS[m]=HIS.get(m,0)+d*d
                break
    if not any:return -30000+d if chk() else 0
    return best

def uci(m):
    f=(m>>7)&127;t=m&127;pr=m>>14
    s="abcdefgh"[f&7]+str((f>>4)+1)+"abcdefgh"[t&7]+str((t>>4)+1)
    if pr:s+="nbrq"[pr-2]
    return s

def pick(fs,lm):
    global nodes
    fen(fs)
    o=[m for m in gen() if uci(m) in lm]
    if not o:o=gen()
    best=o[0]
    nodes=0
    for d in range(1,11):
        cur=None
        cb=-99999
        try:
            for m in [best]+[x for x in o if x!=best]:
                u=mk(m)
                v=-srch(d-1,-99999,-cb)
                um(u)
                if v>cb:cb=v;cur=m
        except Stop:
            break
        if cur is not None:best=cur
        if nodes*3>CAP*2:break
    return best

def post(p,a):
    r=urllib.request.Request(U+p,json.dumps(a).encode(),{"content-type":"application/json"})
    return json.load(urllib.request.urlopen(r))

def ask(p,a):
    for _ in range(3):
        try:return post(p,a)
        except Exception:time.sleep(0.2)
    raise SystemExit(0)

while True:
    g=ask("/game",{})
    if g["status"]=="done":break
    while g["status"]=="your_move":
        try:mv=uci(pick(g["fen"],set(g["legal_moves"])))
        except Exception:mv=g["legal_moves"][0]
        g=ask("/move",{"game":g["game"],"move":mv})
