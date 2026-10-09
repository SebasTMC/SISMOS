import re, json, zipfile, os, collections
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
os.makedirs('site/docs/datos/std',exist_ok=True)
tiempo={}
for r in rows('02-dim_tiempo.sql'):
    a=parse(r); tiempo[int(a[0])]=(a[1],a[2],int(a[3]))   # hora, fecha, anio
sis={}
for r in rows('03-dim_sismos.sql'):
    a=parse(r); sis[int(a[0])]=a
by=collections.defaultdict(list)
for r in rows('05-fact_impacto_sismos_imputed.sql'):
    a=parse(r); s=sis[int(a[0])]; t=tiempo[int(a[3])]
    # [id, lat, lon, mag, prof, ref, fecha, pob, impacto]
    by[t[2]].append([int(a[0]),float(s[2]),float(s[3]),float(s[1]),float(s[4]),s[5],t[1],int(a[4]),float(a[5])])
for y,v in by.items():
    v.sort(key=lambda x:-x[3])
    json.dump(v,open(f'site/docs/datos/std/{y}.json','w'),separators=(',',':'),ensure_ascii=False)
print('años std',len(by),'max filas',max(len(v) for v in by.values()))
# zonas std2
zon=[]
for r in rows('01-dim_zonas.sql'):
    a=parse(r)
    if int(a[1])!=0: zon.append({'entidad':a[1],'nombre':a[2],'poblacion_total':a[3],'poblacion_femenina':a[4],'poblacion_masculina':a[5]})
zon.sort(key=lambda d:int(d['entidad']))
json.dump(zon,open('site/docs/datos/zonas_std2.json','w'),separators=(',',':'),ensure_ascii=False)
# economia std3
eco=[]
for r in rows('04-dim_economia.sql'):
    a=parse(r)
    f=lambda x: None if x in('NULL','') else x
    eco.append({'entidad':f(a[2]),'nombre':a[1],'produccion_total':f(a[3]),'consumo_intermedio':f(a[5]),'valor_agregado':f(a[6])})
json.dump(eco,open('site/docs/datos/economia.json','w'),separators=(',',':'),ensure_ascii=False)
print(len(zon),len(eco),eco[:2])
