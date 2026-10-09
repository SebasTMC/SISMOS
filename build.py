import re, json, os, shutil
SRC='/tmp/Seismic-Data-Visualization-System-main/src/'
OUT='site/docs/'
def rd(f): return open(SRC+f,encoding='utf-8').read()
def wr(f,t): open(OUT+f,'w',encoding='utf-8').write(t)
def top_block(t):
    return re.sub(r'<\?php.*?\?>','',t,count=1,flags=re.S)
def to_plain(t):
    # el último <script> sin src se vuelve texto que el loader inyecta cuando ya hay datos
    i=t.rfind('<script>')
    assert i>0
    return t[:i]+'<script type="text/plain" id="main-src">'+t[i+len('<script>'):]
LOADER_COMMON='''
<script>
function inyectarPrincipal(){var s=document.createElement('script');s.textContent=document.getElementById('main-src').textContent;document.body.appendChild(s);}
function nf(n,d){return Number(n).toLocaleString('en-US',{minimumFractionDigits:d||0,maximumFractionDigits:d||0});}
function errorCarga(e){document.body.insertAdjacentHTML('afterbegin','<div style="color:red;padding:20px;background:#fee;border:1px solid #f00;margin:10px"><h3>Error</h3><p>No se pudieron cargar los datos: '+e.message+'<br>Si abriste el archivo con doble clic, sírvelo con un servidor (python -m http.server) o ábrelo desde GitHub Pages.</p></div>');}
</script>
'''
# ---------------- std.php ----------------
t=top_block(rd('std.php'))
t=re.sub(r'<select name="anio" id="anio">.*?</select>','<select name="anio" id="anio"></select>',t,flags=re.S)
t=t.replace('value="<?php echo $magnitudMinima; ?>"','value="5"')
t=t.replace('<?php echo $totalSismos; ?>','<span id="m-total">0</span>')
t=t.replace('<?php echo number_format($poblacionTotalAfectada); ?>','<span id="m-pob">0</span>')
n=[0]
def sub_mayor(m):
    n[0]+=1
    return '<span id="m-mag">N/A</span>' if n[0]==1 else '<span id="m-desc">No hay datos disponibles</span>'
t=re.sub(r'<\?php\s*\n?\s*if \(\$sismoConMayorImpacto\).*?\?>',sub_mayor,t,flags=re.S)
t=t.replace("<?php echo date('Y'); ?>",'<span id="anio-actual"></span>')
t=to_plain(t)
assert '<?php' not in t, re.findall(r'<\?php.{0,80}',t)
loader=LOADER_COMMON+'''
<script>
(function(){
  var q=new URLSearchParams(location.search);
  var anio=q.get('anio')||'2020';
  var mag=q.get('magnitud')!==null&&q.get('magnitud')!==''?parseFloat(q.get('magnitud')):5.0; if(isNaN(mag))mag=0;
  var sel=document.getElementById('anio');
  for(var a=2025;a>=1900;a--){var o=document.createElement('option');o.value=a;o.textContent=a;if(String(a)===String(anio))o.selected=true;sel.appendChild(o);}
  document.getElementById('magnitud').value=mag;
  document.getElementById('anio-actual').textContent=new Date().getFullYear();
  fetch('datos/std/'+parseInt(anio)+'.json').then(function(r){return r.ok?r.json():[];}).catch(function(){return [];}).then(function(rows){
    var datos=[],total=0,pobTot=0,mayor=null,maxImp=0;
    rows.forEach(function(r){
      if(r[3]<mag)return;             // WHERE magnitud >= $1 (ya viene ORDER BY magnitud DESC)
      total++; pobTot+=r[7];
      if(r[8]>maxImp){maxImp=r[8];mayor=r;}
      datos.push({lat:r[1],lng:r[2],magnitude:r[3],depth:r[4],location:r[5],date:r[6],population:r[7],impactFactor:r[8]});
    });
    window.sismoData=datos;
    document.getElementById('m-total').textContent=total;
    document.getElementById('m-pob').textContent=nf(pobTot);
    if(mayor){document.getElementById('m-mag').textContent=mayor[3].toFixed(1);
      var f=mayor[6].split('-');document.getElementById('m-desc').textContent=f[2]+'/'+f[1]+'/'+f[0]+' - '+mayor[5];}
    inyectarPrincipal();
  });
})();
</script>'''
t=t.replace('</body>',loader+'\n</body>')
wr('std.html',t)
# ---------------- std2.php ----------------
t=top_block(rd('std2.php'))
t=t.replace('<?php echo number_format($poblacionTotal); ?>','<span id="m-tot"></span>')
t=t.replace('<?php echo number_format($poblacionFemenina); ?>','<span id="m-fem"></span>')
t=t.replace('<?php echo number_format($poblacionMasculina); ?>','<span id="m-mas"></span>')
t=re.sub(r'\s*var datosEntidades = <\?php.*?\?>;','',t)
t=re.sub(r'\s*var datosMunicipios = <\?php.*?\?>;','',t)
t=to_plain(t)
assert '<?php' not in t, re.findall(r'<\?php.{0,80}',t)
loader=LOADER_COMMON+'''
<script>
fetch('datos/zonas_std2.json').then(function(r){return r.json();}).then(function(d){
  window.datosEntidades=d; window.datosMunicipios=[];
  var s=function(k){return d.reduce(function(a,x){return a+parseInt(x[k]);},0);};
  document.getElementById('m-tot').textContent=nf(s('poblacion_total'));
  document.getElementById('m-fem').textContent=nf(s('poblacion_femenina'));
  document.getElementById('m-mas').textContent=nf(s('poblacion_masculina'));
  inyectarPrincipal();
}).catch(errorCarga);
</script>'''
t=t.replace('</body>',loader+'\n</body>')
wr('std2.html',t)
# ---------------- std3.php ----------------
t=top_block(rd('std3.php'))
t=t.replace('<?php echo number_format($produccionTotalNacional, 2); ?>','<span id="m-prod"></span>')
t=t.replace('<?php echo number_format($consumoIntermedioTotal, 2); ?>','<span id="m-cons"></span>')
t=t.replace('<?php echo number_format($valorAgregadoTotal, 2); ?>','<span id="m-val"></span>')
ent_php=re.search(r'\$entidades = (array\(.*?\n\));',rd('std3.php'),re.S).group(1)
mapeo_php=re.search(r'\$mapeoGeoJson = (array\(.*?\n\));',rd('std3.php'),re.S).group(1)
def php_arr_to_json(a):
    pairs=re.findall(r'"([^"]+)"\s*=>\s*"([^"]+)"',a)
    return json.dumps(dict(pairs),ensure_ascii=False)
ENT=php_arr_to_json(ent_php); MAP=php_arr_to_json(mapeo_php)
t=re.sub(r'\s*var datosEconomicos = <\?php.*?\?>;','',t)
t=re.sub(r'\s*var entidadesMap = <\?php.*?\?>;','',t)
t=re.sub(r'\s*var mapeoGeoJson = <\?php.*?\?>;','',t)
t=to_plain(t)
assert '<?php' not in t, re.findall(r'<\?php.{0,80}',t)
loader=LOADER_COMMON+'''
<script>
var ENTIDADES=%s;
var MAPEO_GEOJSON=%s;
// nombre en dim_economia -> nombre en el catálogo de entidades
var ALIAS={'Coahuila de Zaragoza':'Coahuila','Michoacán de Ocampo':'Michoacán','México':'Estado de México','Veracruz de Ignacio de la Llave':'Veracruz','Querétaro de Arteaga':'Querétaro'};
function normalizarPHP(n){
  var m={'á':'a','é':'e','í':'i','ó':'o','ú':'u','ü':'u','ñ':'n',' de ':'',' del ':'',' la ':'',' y ':''};
  var s=n; Object.keys(m).sort(function(a,b){return b.length-a.length;}).forEach(function(k){s=s.split(k).join(m[k]);});
  return s.replace(/\\s+/g,'').toLowerCase();
}
fetch('datos/economia.json').then(function(r){return r.json();}).then(function(rows){
  var porNombre={}; Object.keys(ENTIDADES).forEach(function(c){porNombre[ENTIDADES[c]]=c;});
  var datos=[],P=0,C=0,V=0;
  rows.forEach(function(r){
    var nom=ALIAS[r.nombre]||r.nombre, cod=porNombre[nom]; if(!cod)return;
    var o={entidad:cod,nombre:r.nombre,codigo_entidad:cod,nombre_entidad:ENTIDADES[cod],nombre_normalizado:normalizarPHP(ENTIDADES[cod]),
      produccion_total:parseFloat(r.produccion_total)||0,consumo_intermedio:parseFloat(r.consumo_intermedio)||0,valor_agregado:parseFloat(r.valor_agregado)||0};
    datos.push(o);P+=o.produccion_total;C+=o.consumo_intermedio;V+=o.valor_agregado;
  });
  datos.sort(function(a,b){return b.produccion_total-a.produccion_total;});
  window.datosEconomicos=datos; window.entidadesMap=ENTIDADES; window.mapeoGeoJson=MAPEO_GEOJSON;
  document.getElementById('m-prod').textContent=nf(P,2);
  document.getElementById('m-cons').textContent=nf(C,2);
  document.getElementById('m-val').textContent=nf(V,2);
  inyectarPrincipal();
}).catch(errorCarga);
</script>''' % (ENT,MAP)
t=t.replace('</body>',loader+'\n</body>')
wr('std3.html',t)
# ---------------- vista.html -> index.html ----------------
v=rd('vista.html')
for p in ('std','std2','std3'): v=v.replace("'%s.php'"%p,"'%s.html'"%p)
wr('index.html',v)
print('ok')
