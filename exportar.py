import re, json, zipfile, sys
Z='/mnt/user-data/uploads/Seismic-Data-Visualization-System-main.zip'
P='Seismic-Data-Visualization-System-main/sql/'
z=zipfile.ZipFile(Z)
def rows(name):
    with z.open(P+name) as f:
        for line in f:
            m=re.search(rb'VALUES \((.*)\);\s*$',line)
            if m: yield m.group(1).decode()
def parse(s):
    out=[];cur='';q=False
    for ch in s:
        if ch=="'": q=not q; continue
        if ch==',' and not q: out.append(cur.strip());cur='';continue
        cur+=ch
    out.append(cur.strip());return out
zonas={}
for r in rows('01-dim_zonas.sql'):
    a=parse(r); zonas[int(a[0])]=(a[2],int(a[3]))
tiempo={}
for r in rows('02-dim_tiempo.sql'):
    a=parse(r); tiempo[int(a[0])]=(a[1],a[2])
sis={}
for r in rows('03-dim_sismos.sql'):
    a=parse(r); sis[int(a[0])]=(float(a[1]),float(a[2]),float(a[3]),float(a[4]),a[5])
print(len(zonas),len(tiempo),len(sis))
zl=sorted(zonas); zidx={k:i for i,k in enumerate(zl)}
n=0;miss=0
lat=[];lon=[];mag=[];dep=[];fec=[];hor=[];zon=[];ref=[]
refs={};
for r in rows('05-fact_impacto_sismos_imputed.sql'):
    a=parse(r)
    s=sis.get(int(a[0])); t=tiempo.get(int(a[3]))
    if not s or not t: miss+=1; continue
    lat.append(round(s[1],3));lon.append(round(s[2],3));mag.append(s[0]);dep.append(round(s[3]))
    fec.append(int(t[1].replace('-','')));hor.append(t[0]);zon.append(zidx[int(a[1])])
    refs.setdefault(s[4],len(refs)); ref.append(refs[s[4]])
print('hechos',len(mag),'sin join',miss)
reflist=[None]*len(refs)
for k,v in refs.items(): reflist[v]=k
json.dump({'n':len(mag),'lat':lat,'lon':lon,'mag':mag,'prof':dep,'fecha':fec,'hora':hor,'zona':zon,'ref':ref,'refs':reflist},
  open('site/docs/datos/sismos.json','w'),separators=(',',':'))
json.dump([{'nombre':zonas[k][0],'poblacion_total':zonas[k][1]} for k in zl],open('site/docs/datos/zonas.json','w'),separators=(',',':'),ensure_ascii=False)
print(min(fec),max(fec),min(mag),max(mag))
