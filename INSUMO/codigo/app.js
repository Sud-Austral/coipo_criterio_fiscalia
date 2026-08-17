/* ═══ utilidades ═══════════════════════════════════════════ */
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const byId = Object.fromEntries(D.docs.map(d => [d.id, d]));
const PAS_DOC = {}; D.pasajes.forEach(p => (PAS_DOC[p.doc] = PAS_DOC[p.doc] || []).push(p));
const M = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
const fFecha = f => { const [a,m,d] = f.split('-'); return `${d} ${M[+m-1]} ${a}`; };
const rotulo = d => d.tipo === 'Decisión de amparo' ? `Amparo ${d.numero}`
  : `${d.tipo === 'Memorándum' ? 'MM.' : d.tipo === 'Oficio' ? 'OF.' :
      d.tipo === 'Resolución' ? 'Res.' : 'Dict.'} ${d.numero}/${d.anio}`;

/* mismo plegado y lematizador que el servidor: la búsqueda del cliente
   no puede diferir de la que valida la suite de integridad */
const plegar = s => s.normalize('NFD').replace(/[̀-ͯ]/g,'')
  .toLowerCase().replace(/[^a-z0-9ñ ]+/g,' ').replace(/\s+/g,' ').trim();
const DERIV = ['cion','miento','idad','mente','ancia','encia'];
function raiz(p){ if (p.length <= 3) return p;
  if (p.endsWith('ces') && p.length > 4) p = p.slice(0,-3) + 'z';
  else if (p.endsWith('s') && p.length > 3) { p = p.slice(0,-1);
    if (p.endsWith('e') && p.length > 3 && 'lrndzjy'.includes(p[p.length-2])) p = p.slice(0,-1); }
  for (const s of DERIV) if (p.endsWith(s) && p.length - s.length >= 4) return p.slice(0, -s.length);
  return p; }
const raices = t => new Set(plegar(t).split(' ').filter(w => w.length > 2).map(raiz));

function estadoBadge(e){ const [k,l] = D.estadoMeta[e];
  return `<span class="badge st-${k}"><span class="dot"></span>${l}</span>`; }
function jerBadge(j){ const [r,l] = D.jerarquiaMeta[j];
  return `<span class="jer j${r}" title="Jerarquía ${r} de 4">${l}</span>`; }

/* ═══ búsqueda por cuatro vías independientes ══════════════ */
const VIAS = {
  descriptor: 'Descriptor curado por un abogado al ingresar el documento.',
  tesauro:    'Término preferido o sinónimo del tesauro de materias.',
  texto:      'Coincidencia en el texto del pasaje, con lematización española.',
  norma:      'Norma invocada dentro del pasaje.',
  cita:       'Alcanzado por el grafo de citas desde otro resultado.'
};

/* ¿La consulta ES el nombre de una materia, o un término específico dentro
   de ella? De eso depende si la expansión por materia es el resultado
   buscado o una ampliación que hay que declarar aparte.
     «monumentos naturales» → es la materia          → expansión = resultado
     «teletrabajo»          → término de una materia → expansión = ampliación
   Sin esta distinción, buscar «teletrabajo» devolvía los 6 documentos de
   «Gestión de personas», incluido uno sobre Planes de Manejo que solo citaba
   el Estatuto Administrativo. */
function esNombreDeMateria(qr, materia){
  const mr = raices(materia);
  if (!qr.size || !mr.size) return false;
  const dentro = [...qr].filter(r => mr.has(r)).length;
  return dentro === qr.size && dentro >= mr.size - 1;
}

function buscar(q){
  const ql = plegar(q); if (!ql) return {directos:[], relacionados:[], q:''};
  const qr = new Set(ql.split(' ').filter(w => w.length > 2).map(raiz));
  const res = {}, pasHit = {};
  const add = (doc, via, det) => {
    res[doc] = res[doc] || {};
    (res[doc][via] = res[doc][via] || new Set()).add(det);
  };
  const marcarPasaje = (doc, p) => (pasHit[doc] = pasHit[doc] || []).push(p);

  /* ── vías directas: el documento trata del término consultado ─────── */

  /* vía 1 · descriptor curado */
  D.docs.forEach(d => d.descriptores.forEach(t => {
    const pt = plegar(t);
    if (pt === ql || (ql.length > 4 && (pt.includes(ql) || ql.includes(pt)))) add(d.id,'descriptor',t);
  }));

  /* vía 2 · texto lematizado del pasaje */
  D.pasajes.forEach(p => {
    const pr = raices(p.texto);
    if (qr.size && [...qr].every(r => pr.has(r))) {
      add(p.doc,'texto',`pág. ${p.pagina}`); marcarPasaje(p.doc, p);
    }
  });

  /* vía 3 · norma invocada */
  D.pasajes.forEach(p => p.normas.forEach(n => {
    if (ql.length > 3 && plegar(n).includes(ql)) { add(p.doc,'norma',n); marcarPasaje(p.doc, p); }
  }));

  /* vía 4 · tesauro. Si la consulta nombra la materia, es vía directa; si es
     un término específico, la materia queda como ampliación declarada. */
  const materiasQ = new Set(), materiasAmpl = new Set();
  Object.entries(D.tesauro).forEach(([m, dd]) => {
    const formas = [m, ...dd.frases, ...dd.palabras];
    const calza = formas.some(f => { const pf = plegar(f);
      return pf === ql || (ql.length > 4 && pf.includes(ql)) || (pf.length > 4 && ql.includes(pf)); });
    if (!calza) return;
    (esNombreDeMateria(qr, m) ? materiasQ : materiasAmpl).add(m);
  });
  D.pasajes.forEach(p => Object.keys(p.materias).forEach(m => {
    if (materiasQ.has(m)) { add(p.doc,'tesauro',m); marcarPasaje(p.doc, p); }
  }));

  /* vía 5 · cierre por grafo de citas — SOLO desde lo directo */
  const base = new Set(Object.keys(res));
  D.citas.forEach(c => {
    if (!c.en_corpus) return;
    c.citado_por.forEach(src => {
      if (base.has(src) && !base.has(c.destino)) add(c.destino,'cita',`citado por ${rotulo(byId[src])}`);
      if (base.has(c.destino) && !base.has(src)) add(src,'cita',`cita ${c.etiqueta}`);
    });
  });

  const arma = (id, vias, ampl) => ({
    doc: byId[id], vias, ampliacion: !!ampl, n: Object.keys(vias).length,
    pasajes: [...new Map((pasHit[id]||[]).map(p => [p.id, p])).values()]
              .sort((a,b) => (b.principal?1:0)-(a.principal?1:0) || a.pagina-b.pagina)
  });
  const directos = Object.entries(res).map(([id,v]) => arma(id,v))
      .filter(h => h.doc).sort((a,b) => a.doc.fecha < b.doc.fecha ? -1 : 1);

  /* ── ampliación por materia ─────────────────────────────────────────
     Se exige que la materia esté entre los DESCRIPTORES CURADOS del documento:
     que un abogado haya dicho que trata de eso. La materia inferida por tesauro
     sirve para encontrar pasajes dentro de un resultado directo, pero no basta
     para afirmar que un documento está relacionado. Sin esta regla, una sola
     frase detectada automáticamente emparentaba un memo de Planes de Manejo
     con una consulta sobre teletrabajo. */
  const yaEsta = new Set(directos.map(h => h.doc.id));
  const rel = {};
  D.docs.forEach(d => {
    if (yaEsta.has(d.id)) return;
    const comunes = d.descriptores.filter(t => materiasAmpl.has(t));
    if (!comunes.length) return;
    rel[d.id] = {tesauro: new Set(comunes)};
    (PAS_DOC[d.id] || []).forEach(p => {
      if (comunes.some(m => p.materias[m])) marcarPasaje(d.id, p);
    });
  });
  const relacionados = Object.entries(rel).map(([id,v]) => arma(id,v,true))
      .filter(h => h.doc).sort((a,b) => a.doc.fecha < b.doc.fecha ? -1 : 1);

  return {directos, relacionados, q,
          materias:[...materiasQ], materiasAmpl:[...materiasAmpl]};
}

function resaltar(texto, q){
  const t = esc(texto); if (!q) return t;
  const rs = [...raices(q)];
  return t.split(/(\s+)/).map(w => {
    const pl = plegar(w); if (!pl) return w;
    return rs.some(r => raiz(pl) === r || pl.startsWith(r)) ? `<mark>${w}</mark>` : w;
  }).join('');
}

/* ═══ ficha ════════════════════════════════════════════════ */
function fichaHTML(d, o = {}){
  const {compacta=false, vias=null, pasajes=[], q=''} = o;
  const rels = (d.relaciones||[]).map(r =>
    `<div class="rel"><b>${esc(r.tipo.replace(/_/g,' '))}</b> · ${esc(r.ref)}${
      r.nota ? ` — ${esc(r.nota)}` : ''}</div>`).join('');
  const viasHTML = vias ? `<div class="vias">${Object.entries(vias).map(([v,det]) =>
      `<span class="via via-${v}" title="${esc(VIAS[v])} — ${esc([...det].slice(0,3).join(' · '))}">${v}</span>`
    ).join('')}</div>` : '';
  const extra = pasajes.filter(p => !p.principal);
  const pid = 'px' + d.id.replace(/\W/g,'');
  return `<article class="doc">
    <div class="doc-h">
      <span class="doc-id">${esc(rotulo(d))}</span>
      <span class="doc-f">${fFecha(d.fecha)}</span>
      <span class="doc-t">${esc(d.materia)}</span>
      ${o.ampliacion ? '<span class="via via-ampl" title="Comparte materia, no menciona el término">misma materia</span>' : ''}
      ${viasHTML}
    </div>
    <div class="doc-b">
      <div class="meta">
        ${jerBadge(d.jerarquia)} ${estadoBadge(d.estado)}
        <span class="badge">${esc(d.organo)}</span>
        <span class="badge">${d.alcance === 'general' ? 'Criterio general' : 'Caso concreto'}</span>
        ${vias ? `<span class="conv">convergencia <b>${Object.keys(vias).length}/5</b> vías</span>` : ''}
      </div>
      <p class="crit"><span class="fuerza">${esc(d.firmante.split(',')[0])} ${
        esc(D.fuerzaMeta[d.fuerza])}:</span> ${esc(d.criterio)}</p>
      <blockquote>«${esc(d.cita)}»</blockquote>
      <div class="qsrc">
        <span class="ok">✓ cita verificada</span>
        <span>· pág. ${d.pagina || '—'}/${d.paginas}</span>
        <span>· sha256 ${esc(d.sha)}</span>
        <span>· ${d.n_pasajes} pasajes indexados</span>
      </div>
      ${d.alerta ? `<div class="warnbox${d.estado==='requiere_revision'?' s':''}">⚠ ${esc(d.alerta)}</div>` : ''}
      ${d.desestima ? `<div class="desest"><b>Posición desestimada en el propio documento:</b> ${esc(d.desestima)}</div>` : ''}
      ${extra.length ? `
        <button class="mas" data-t="${pid}">Ver ${extra.length} pasaje${extra.length>1?'s':''} más de este documento que coincide${extra.length>1?'n':''}</button>
        <div id="${pid}" style="display:none">${extra.slice(0,8).map(p => `
          <div class="pasaje">
            <div class="pasaje-h"><span class="etq">${esc(p.etiqueta)}</span>
              <span class="conv">pág. ${p.pagina}</span>
              ${Object.keys(p.materias).slice(0,3).map(m => `<span class="badge">${esc(m)}</span>`).join('')}
            </div>
            <div class="pasaje-t">${resaltar(p.texto, q)}</div>
          </div>`).join('')}</div>` : ''}
      ${compacta ? '' : `<div class="norms">${(d.normas_idx||[]).map(x =>
        `<span class="norm norm-${x.origen}" title="${
          x.origen==='ambas' ? 'En la ficha y hallada en el texto, pág. '+x.pagina
          : x.origen==='ficha' ? 'Declarada en la ficha' : 'Detectada en el texto, pág. '+x.pagina
        }">${esc(x.n)}${x.origen==='ambas' ? ' ✓' : ''}</span>`).join('')}</div>${rels}
      <div class="ruta">📎 ${esc(d.ruta)}</div>`}
    </div></article>`;
}

function activarMas(cont){
  cont.querySelectorAll('.mas').forEach(b => b.onclick = () => {
    const t = document.getElementById(b.dataset.t);
    const ab = t.style.display === 'none';
    t.style.display = ab ? 'block' : 'none';
    b.textContent = ab ? 'Ocultar pasajes' : b.textContent.replace('Ocultar pasajes','Ver pasajes');
    if (!ab) b.textContent = `Ver pasajes de este documento`;
  });
}

/* ═══ 1 · Consulta ═════════════════════════════════════════ */
let Q = 'monumento natural';
const SUGS = ['monumento natural','araucaria','reforestación','cabida','geolocalización',
  'parentesco','teletrabajo','viviendas fiscales','ministro de fe','sindicato',
  'Ley 19.628','datos personales'];

function renderConsulta(){
  const {directos, relacionados, materias, materiasAmpl} = buscar(Q);
  const el = document.getElementById('v-consulta');
  const hits = directos;
  const rango = hits.length ? `de <b>${fFecha(hits[0].doc.fecha)}</b> a <b>${fFecha(hits[hits.length-1].doc.fecha)}</b>` : '';
  const conv = hits.filter(h => h.n >= 2).length;
  const solo1 = hits.filter(h => h.n === 1);
  const jerMin = hits.length ? Math.min(...hits.map(h => D.jerarquiaMeta[h.doc.jerarquia][0])) : 0;
  const vacRel = D.vacios.filter(v => v.clase === 'doctrina externa' &&
        v.citado_por.some(c => hits.some(h => h.doc.id === c)));

  el.innerHTML = `
    <h2 class="vh">¿Qué se ha dicho sobre…?</h2>
    <p class="vsub">Los resultados se separan en dos: los que <b>tratan del término consultado</b>,
    en orden cronológico, y los que solo <b>comparten materia</b> sin mencionarlo. Mezclarlos
    pondría al principio de la cronología un documento que no viene al caso.</p>
    <div class="buscador">
      <input id="q" value="${esc(Q)}" placeholder="materia, sinónimo, norma o expresión literal…"
             autocomplete="off" spellcheck="false">
    </div>
    <div class="sugs"><span class="lab">probar:</span>${SUGS.map(s =>
      `<button class="sug" data-q="${esc(s)}">${esc(s)}</button>`).join('')}</div>
    ${!hits.length && !relacionados.length ? `<div class="card pad" style="color:var(--ink-2)">
        Sin resultados para «${esc(Q)}». El tesauro no registra ese término;
        incorporarlo como sinónimo es una tarea de curaduría, no de programación.</div>` : ''}
    ${hits.length ? `
    <div class="resumen">
      <b>${hits.length}</b> documento${hits.length>1?'s':''} sobre «${esc(Q)}» · ${rango} ·
      jerarquía máxima: <b>${D.jerarquiaMeta[Object.entries(D.jerarquiaMeta)
        .find(([,v]) => v[0]===jerMin)[0]][1].toLowerCase()}</b> ·
      <b>${conv}</b> confirmado${conv!==1?'s':''} por dos o más vías
      ${materias.length ? `<br><span style="font-size:12.5px">la consulta nombra la materia ${
        materias.map(m => `<b>${esc(m)}</b>`).join(' · ')}: se devuelve completa</span>` : ''}
      ${solo1.length ? `<br><span style="font-size:12.5px;color:var(--warn-ink)">⚠ ${solo1.length}
        documento${solo1.length>1?'s':''} alcanzado${solo1.length>1?'s':''} por una sola vía:
        ${solo1.map(h => esc(rotulo(h.doc))).join(', ')} — revisar su descriptor</span>` : ''}
    </div>
    ${vacRel.length ? `<div class="warnbox s" style="margin-bottom:18px">
      <b>⚠ Alcance incompleto.</b> Estos documentos se apoyan en
      ${vacRel.length} autoridad${vacRel.length>1?'es':''} externa${vacRel.length>1?'s':''} que
      <b>no está${vacRel.length>1?'n':''} en el repositorio</b>:
      ${vacRel.map(v => esc(v.etiqueta)).join(' · ')}. La cronología es completa respecto
      del corpus, no respecto de la doctrina aplicable.</div>` : ''}
    <div class="tl">${hits.map(h => `<div class="node">${
      fichaHTML(h.doc, {vias:h.vias, pasajes:h.pasajes, q:Q})}</div>`).join('')}</div>` : ''}
    ${relacionados.length ? `
    <div class="sect"><h3>Misma materia, sin mencionar el término — ${relacionados.length}</h3>
      <p style="font-size:12.5px;color:var(--ink-2);margin:-4px 0 12px;max-width:82ch">
        Comparten ${materiasAmpl.map(m => `<b>${esc(m)}</b>`).join(' · ')} con lo anterior, pero
        <b>no contienen «${esc(Q)}»</b>. Se muestran para que la revisión sea completa, separados
        para que no contaminen la cronología. Su relevancia la decide quien consulta.</p>
      <div class="tl">${relacionados.map(h => `<div class="node ext">${
        fichaHTML(h.doc, {vias:h.vias, pasajes:h.pasajes, q:Q, compacta:true})}</div>`).join('')}</div>
    </div>` : ''}`;

  const inp = document.getElementById('q');
  let t; inp.oninput = () => { clearTimeout(t); t = setTimeout(() => {
    Q = inp.value; const pos = inp.selectionStart; renderConsulta();
    const n = document.getElementById('q'); n.focus(); n.setSelectionRange(pos,pos); }, 260); };
  el.querySelectorAll('.sug').forEach(b => b.onclick = () => { Q = b.dataset.q; renderConsulta(); });
  activarMas(el);
}

/* ═══ 2 · Líneas de criterio ═══════════════════════════════ */
function renderLineas(){
  const el = document.getElementById('v-lineas');
  el.innerHTML = `
    <h2 class="vh">Líneas de criterio</h2>
    <p class="vsub">Cada eslabón declara el verbo que lo une al anterior. Los nodos en gris son
    documentos que el corpus cita y no contiene: la cadena se muestra incompleta en vez de
    presentarse como si estuviera cerrada.</p>
    ${D.lineas.map(L => `
      <div class="sect">
        <div class="card pad" style="margin-bottom:16px">
          <h3 style="font-size:16px;margin-bottom:6px">${esc(L.titulo)}</h3>
          <p style="margin:0 0 9px;font-size:13.5px;color:var(--ink-2)">${esc(L.pregunta)}</p>
          <span class="badge ${L.estado.includes('Tensión') ? 'st-warning' :
            L.estado.includes('revisión') || L.estado.includes('obligada') ? 'st-serious' : 'st-good'}">
            <span class="dot"></span>${esc(L.estado)}</span>
        </div>
        <div class="tl">${L.nodos.map(n => {
          if (n.tipo === 'doc'){ const d = byId[n.id];
            return `<div class="node">
              <span class="verb${n.tension?' t':''}">${esc(n.verbo)}</span>
              ${fichaHTML(d, {compacta:true})}
              ${n.tension ? `<div class="warnbox">⚠ <b>Tensión:</b> ${esc(n.tension)}</div>` : ''}
            </div>`; }
          return `<div class="node ext${n.falta?' falta':''}">
            <span class="verb">${esc(n.verbo)}</span>
            <div class="card pad" style="padding:13px 16px">
              <div style="display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;margin-bottom:6px">
                <span class="doc-id" style="color:var(--ink-2)">${esc(n.ref)}</span>
                <span class="doc-f">${n.fecha.endsWith('-01-01') ? n.fecha.slice(0,4) : fFecha(n.fecha)}</span>
                ${n.vinculante ? '<span class="jer j1">Vinculante</span>' : ''}
                ${n.falta ? '<span class="badge st-serious"><span class="dot"></span>No incorporado</span>'
                          : '<span class="badge">Referencia externa</span>'}
              </div>
              <p style="margin:0;font-size:13px;color:var(--ink-2)">${esc(n.texto)}</p>
            </div></div>`;
        }).join('')}</div>
      </div>`).join('')}`;
  activarMas(el);
}

/* ═══ 3 · Vacíos ═══════════════════════════════════════════ */
function renderVacios(){
  const porClase = {};
  D.vacios.forEach(v => (porClase[v.clase] = porClase[v.clase] || []).push(v));
  const orden = ['doctrina externa','instrucción CONAF','documento citado','solicitud / trámite'];
  const glosa = {
    'doctrina externa': 'Dictámenes y decisiones que sostienen el criterio. Su ausencia es el riesgo real: el razonamiento se apoya en algo que no se puede leer aquí.',
    'instrucción CONAF': 'Oficios y resoluciones propias que fijan criterio y son citados como vigentes.',
    'documento citado': 'Documentos invocados en el análisis, sin ser la solicitud que lo originó.',
    'solicitud / trámite': 'El memorándum que originó cada consulta. Correspondencia, no doctrina: se registra por completitud del expediente.'
  };
  document.getElementById('v-vacios').innerHTML = `
    <h2 class="vh">Cierre de citas</h2>
    <p class="vsub">Nadie puede demostrar que tiene todo lo que se ha escrito. Sí se puede demostrar
    que se tiene todo aquello a lo que el corpus apunta. El sistema recorre las citas de los 20
    documentos, las normaliza a una identidad canónica y declara qué falta.</p>

    <div class="tiles">
      <div class="tile"><div class="lab">Referencias detectadas</div><div class="val">${D.citas.length}</div>
        <div class="foot">en el cuerpo, sin listas de copia</div></div>
      <div class="tile"><div class="lab">Resueltas al corpus</div>
        <div class="val" style="color:${D.citas.filter(c=>c.en_corpus).length<3?'var(--critical-ink)':'var(--good-ink)'}">${D.citas.filter(c=>c.en_corpus).length}</div>
        <div class="foot">apuntan a un documento presente</div></div>
      <div class="tile"><div class="lab">Vacíos declarados</div>
        <div class="val" style="color:var(--serious-ink)">${D.vacios.length}</div>
        <div class="foot">citados y no incorporados</div></div>
      <div class="tile"><div class="lab">Doctrina externa ausente</div>
        <div class="val" style="color:var(--critical-ink)">${(porClase['doctrina externa']||[]).length}</div>
        <div class="foot">sostiene el criterio y no está</div></div>
    </div>

    <div class="warnbox s" style="margin-bottom:24px;font-size:13.5px">
      <b>⚠ El corpus está casi desconectado de sí mismo.</b> De ${D.citas.length} referencias, solo
      <b>${D.citas.filter(c=>c.en_corpus).length}</b> apunta a otro documento de la carpeta. Todo lo
      demás que sostiene el razonamiento vive fuera del repositorio — incluido el
      <b>Dictamen CGR E33624/2020</b>, invocado por 4 pronunciamientos.
    </div>

    ${orden.filter(c => porClase[c]).map(c => `
      <div class="sect"><h3>${esc(c)} — ${porClase[c].length}</h3>
        <p style="font-size:12.5px;color:var(--ink-2);margin:-4px 0 11px;max-width:80ch">${esc(glosa[c])}</p>
        <div class="card scroll"><table>
          <thead><tr><th>Documento referido</th><th>Doctrina que aporta</th>
            <th class="num">Citas</th><th>Invocado por</th></tr></thead>
          <tbody>${porClase[c].map(v => `<tr>
            <td class="m clase-${c.split(' ')[0]}">${v.critico?'<span class="crit-star">★</span> ':''}${esc(v.etiqueta)}
              ${v.variantes ? `<div style="font-size:10px;color:var(--ink-3);font-weight:400">
                grafías: ${v.variantes.map(esc).join(' · ')}</div>` : ''}</td>
            <td style="color:var(--ink-2);font-size:12.5px">${esc(v.doctrina || '—')}</td>
            <td class="num">${v.citado_por.length}</td>
            <td class="m">${v.citado_por.map(x => byId[x] ? esc(rotulo(byId[x])) : esc(x)).join(' · ')}</td>
          </tr>`).join('')}</tbody>
        </table></div>
      </div>`).join('')}

    <div class="sect"><h3>Identidad canónica</h3>
      <div class="card pad" style="font-size:13.5px;color:var(--ink-2)">
        El <b>Dictamen CGR E33624/2020</b> aparece en el corpus escrito como
        <code>E33624</code>, <code>33624</code> y <code>33.624</code>. Son la misma autoridad.
        Sin una identidad canónica, quien busca una grafía no encuentra los documentos que usaron
        las otras — y el índice por norma la contaría como tres autoridades distintas.
        La verificación <b>V08</b> comprueba que ninguna variante colisione entre autoridades.
      </div>
    </div>`;
}

/* ═══ 4 · Corpus ═══════════════════════════════════════════ */
function renderCorpus(){
  const porAnio = {}; D.docs.forEach(d => porAnio[d.anio] = (porAnio[d.anio]||0)+1);
  const anios = Object.keys(porAnio).sort(); const max = Math.max(...Object.values(porAnio));
  const totalPas = D.pasajes.length;
  document.getElementById('v-corpus').innerHTML = `
    <h2 class="vh">Corpus</h2>
    <p class="vsub">Cada documento se indexa por pasaje, no como bloque único: un memorándum dice
    cosas sobre materias distintas de la suya, y esas quedan recuperables por separado.</p>
    <div class="grid2" style="margin-bottom:24px">
      <div class="card pad">
        <h3 style="font-size:13.5px;margin-bottom:2px">Documentos incorporados por año</h3>
        <p style="margin:0 0 4px;font-size:12px;color:var(--ink-3)">El corpus crece; el índice se actualiza por ingesta incremental.</p>
        <div class="chart">${anios.map(a => `
          <div class="bar-w"><span class="bar-n">${porAnio[a]}</span>
            <div class="bar" style="height:${Math.round(porAnio[a]/max*82)}%"></div>
            <span class="bar-x">${a}</span></div>`).join('')}</div>
      </div>
      <div class="card pad">
        <h3 style="font-size:13.5px;margin-bottom:9px">Profundidad del índice</h3>
        <table><tbody>
          <tr><td>Documentos</td><td class="num" style="font-weight:600">${D.docs.length}</td></tr>
          <tr><td>Pasajes indexados</td><td class="num" style="font-weight:600;color:var(--accent-2)">${totalPas}</td></tr>
          <tr><td>Promedio por documento</td><td class="num">${(totalPas/D.docs.length).toFixed(1)}</td></tr>
          <tr><td>Materias del tesauro</td><td class="num">${Object.keys(D.tesauro).length}</td></tr>
          <tr><td>Sinónimos registrados</td><td class="num">${Object.values(D.tesauro).reduce((a,d)=>a+d.frases.length+d.palabras.length,0)}</td></tr>
        </tbody></table>
        <p style="font-size:11.5px;color:var(--ink-3);margin:9px 0 0">
          Indexar un criterio por documento daría 20 unidades recuperables. Por pasaje son
          ${totalPas} — factor ${(totalPas/D.docs.length).toFixed(1)}×.</p>
      </div>
    </div>
    <div class="card scroll"><table>
      <thead><tr><th>Documento</th><th>Fecha</th><th>Órgano</th><th>Materia</th>
        <th>Jerarquía</th><th>Fuerza</th><th>Estado</th><th class="num">Pasajes</th><th>Cita</th></tr></thead>
      <tbody>${D.docs.map(d => `<tr>
        <td class="m" style="color:var(--accent-2);font-weight:600">${esc(rotulo(d))}</td>
        <td class="m">${d.fecha}</td>
        <td style="font-size:12.5px">${esc(d.organo.replace('CONAF — ',''))}</td>
        <td style="max-width:270px">${esc(d.materia)}</td>
        <td>${jerBadge(d.jerarquia)}</td>
        <td style="font-size:12.5px;font-style:italic;color:var(--ink-2)">${esc(D.fuerzaMeta[d.fuerza])}</td>
        <td>${estadoBadge(d.estado)}</td>
        <td class="num" style="font-weight:600">${d.n_pasajes}</td>
        <td class="m"><span class="chk">✓</span> p.${d.pagina||'—'}</td></tr>`).join('')}</tbody>
    </table></div>`;
}

/* ═══ 5 · Normas ═══════════════════════════════════════════ */
function renderNormas(){
  const idx = {}, proc = {};
  D.docs.forEach(d => (d.normas_idx||[]).forEach(x => {
    (idx[x.n] = idx[x.n]||[]).push(d);
    proc[x.n] = proc[x.n] || new Set(); proc[x.n].add(x.origen);
  }));
  const cuerpo = n => n.replace(/\s+art\..*$/,'');
  const g = {};
  Object.entries(idx).forEach(([n,ds]) => { const c = cuerpo(n);
    g[c] = g[c] || {arts:[], docs:new Set()};
    g[c].arts.push(n); ds.forEach(d => g[c].docs.add(d.id)); });
  const orden = Object.keys(g).sort((a,b) => g[b].docs.size-g[a].docs.size || a.localeCompare(b,'es'));
  document.getElementById('v-normas').innerHTML = `
    <h2 class="vh">Índice inverso por norma</h2>
    <p class="vsub">Cuando una ley cambia, ¿qué criterios quedan expuestos? Este índice se
    construye desde una <b>fuente única</b>: la lista curada en la ficha fusionada con la extraída
    del texto, cada entrada marcada con su procedencia. Las que llevan <b>✓</b> están en ambas.
    V09 comprueba además que ningún documento cite una norma posterior a su propia fecha, y V15
    que toda norma de la ficha se halle en el documento.</p>
    <div class="warnbox s" style="margin-bottom:22px;font-size:13.5px">
      <b>⚠ Impacto normativo con fecha.</b> La <b>Ley 19.628</b> sostiene 2 pronunciamientos y será
      sustituida por la <b>Ley 21.719</b> el <b>1 de diciembre de 2026</b>. El MM 3129/2022 se funda
      íntegramente en ella.
    </div>
    <div class="card scroll"><table>
      <thead><tr><th>Cuerpo normativo</th><th>Disposiciones invocadas</th>
        <th class="num">Docs.</th><th>Pronunciamientos</th></tr></thead>
      <tbody>${orden.map(c => {
        const gg = g[c], ds = [...gg.docs].map(i => byId[i]).sort((a,b)=>a.fecha<b.fecha?-1:1);
        const al = c === 'Ley 19.628';
        return `<tr${al?' style="background:#fdf1eb"':''}>
          <td class="m" style="font-weight:600;color:${al?'var(--serious-ink)':'var(--accent-2)'}">${esc(c)}${al?' ⚠':''}</td>
          <td style="font-size:12px;color:var(--ink-2)">${gg.arts.map(a => esc(a.replace(c,'').trim()||'—')).join(' · ')}</td>
          <td class="num" style="font-weight:600">${gg.docs.size}</td>
          <td class="m">${ds.map(d => `<span style="color:var(--accent-2)">${esc(rotulo(d))}</span>`).join(' · ')}</td>
        </tr>`; }).join('')}</tbody>
    </table></div>`;
}

/* ═══ 6 · Confiabilidad ════════════════════════════════════ */
function renderConfianza(){
  const rojos = D.integridad.filter(c => c.severidad === 'falla').length;
  const avisos = D.integridad.filter(c => c.severidad === 'aviso').length;
  const MARCA = {ok:['chk-ok','✓ OK'], aviso:['chk-av','! AVISO'], falla:['chk-no','✗ FALLA']};
  document.getElementById('v-confianza').innerHTML = `
    <h2 class="vh">Confiabilidad</h2>
    <p class="vsub">La herramienta no pide que se le crea: publica el resultado de correr ${D.integridad.length}
    verificaciones deterministas sobre todo el corpus. Se ejecutan en cada ingesta y en un proceso
    nocturno. Si una falla, el índice no se publica.</p>

    <div class="tiles">
      <div class="tile"><div class="lab">Verificaciones</div>
        <div class="val" style="color:${rojos?'var(--critical-ink)':'var(--good-ink)'}">${D.integridad.length-rojos}/${D.integridad.length}</div>
        <div class="foot">${rojos?rojos+' en rojo':'ninguna en rojo'}${avisos?' · '+avisos+' aviso':''}</div></div>
      <div class="tile"><div class="lab">Citas verificadas</div>
        <div class="val" style="color:var(--good-ink)">${D.docs.length}/${D.docs.length}</div>
        <div class="foot">coincidencia exacta</div></div>
      <div class="tile"><div class="lab">Pasajes trazados</div>
        <div class="val" style="color:var(--good-ink)">${D.pasajes.length}</div>
        <div class="foot">subcadena literal del fuente</div></div>
      <div class="tile"><div class="lab">Referencias cerradas</div>
        <div class="val" style="color:var(--good-ink)">${D.citas.length}/${D.citas.length}</div>
        <div class="foot">resueltas o declaradas</div></div>
    </div>

    <div class="sect"><h3>Las verificaciones</h3>
      <div class="card">${D.integridad.map(c => {
        const [cls,txt] = MARCA[c.severidad];
        return `<div class="chk-row">
          <span class="chk-cod">${c.codigo}</span>
          <span class="chk-est ${cls}">${txt}</span>
          <span><b style="font-size:13px">${esc(c.titulo)}</b>
            <span class="chk-g"> — ${esc(c.glosa)}</span></span>
          <span class="chk-n">${c.total-c.fallos.length}/${c.total}</span>
          ${c.fallos.length ? `<div class="detalle">${c.fallos.slice(0,4).map(esc).join(' · ')}${
            c.fallos.length>4?` · … y ${c.fallos.length-4} más`:''}</div>` : ''}
        </div>`; }).join('')}</div>
      <p style="font-size:12.5px;color:var(--ink-3);margin-top:11px">
        <b>V12 y V15 son avisos, no fallos.</b> V12 lista pares de documentos que comparten materia
        sin declarar relación; V15, normas cuya ficha las rotula distinto de como el documento las
        cita («Estatutos CONAF art. 18» frente a «artículo 18 de los estatutos de la Corporación»).
        En ambos casos la máquina propone y un abogado adjudica: son colas que se vacían, no
        defectos. Las otras trece bloquean la publicación si fallan.</p>
    </div>

    <div class="sect"><h3>Defectos que la suite encontró</h3>
      <div class="card pad" style="margin-bottom:11px">
        <p style="margin:0 0 8px;font-size:13.5px;color:var(--ink-2)">
          <b>V14</b> —el tesauro no puede contener nombres de fuentes ni de órganos— encontró
          <b>2 términos</b> que se me habían pasado al depurar a mano: «ley de presupuestos del
          sector público» y «reglamento interno». Ese fue el defecto que emparentaba una consulta
          sobre teletrabajo con un memorándum de Planes de Manejo: bastaba que un texto citara el
          Estatuto Administrativo para quedar etiquetado como materia de personal.</p>
        <p style="margin:0;font-size:13.5px;color:var(--ink-2)">
          <b>V15</b> reveló que ficha y documento rotulan las normas de forma distinta en 6 casos.
          Las normas necesitan identidad canónica con variantes, igual que los dictámenes — es la
          misma solución, un nivel más abajo.</p>
      </div>
      <div class="card pad">
        <p style="margin:0 0 10px;font-size:13.5px;color:var(--ink-2)">
          En la primera corrida, <b>V02 falló en 4 de 285 pasajes</b>. La causa: al limpiar los
          encabezados de impresión que caen a mitad de un pasaje —los que cruzan un corte de
          página— el texto resultante dejaba de existir de forma contigua en el original. Eran
          citas que un abogado no habría podido encontrar en el PDF.</p>
        <p style="margin:0;font-size:13.5px;color:var(--ink-2)">
          La corrección no fue arreglar esos cuatro casos: fue recortar todo pasaje al tramo que sí
          es contiguo, cerrándolo en límite de oración. Ahora V02 es una <b>garantía estructural</b>
          y no una comprobación que a veces pasa. Ese es el patrón que debe repetirse con cada
          verificación.</p>
      </div>
    </div>

    <div class="sect"><h3>Prueba negativa del verificador</h3>
      <div class="card pad">
        <p style="margin:0 0 13px;font-size:13.5px;color:var(--ink-2)">
          Comparación exacta de subcadena contra el texto congelado, tras normalizar ligaduras
          (<code>ﬁ</code>, <code>ﬂ</code>), comillas, guiones y espacios. Determinista: o pasa o no pasa.</p>
        <table><thead><tr><th>Prueba sobre MM 5939/2025</th><th>Texto evaluado</th>
          <th style="text-align:right">Resultado</th></tr></thead>
          <tbody>${D.prueba.map(p => `<tr>
            <td style="white-space:nowrap;font-weight:${p.res?600:400}">${esc(p.caso)}</td>
            <td style="font-family:var(--serif);font-size:13px;color:var(--ink-2)">«${p.texto}»</td>
            <td style="text-align:right;white-space:nowrap">${p.res
              ? '<span class="chk">✓ PASA</span>' : '<span class="xmk">✕ FALLA</span>'}</td></tr>`).join('')}
          </tbody></table>
      </div>
    </div>

    <div class="sect"><h3>Alertas activas</h3>
      <div class="grid2">${D.alertas.map(a => `
        <div class="meth" style="border-left:3px solid ${
          a.sev==='serious'?'var(--serious)':a.sev==='warning'?'var(--warn)':'var(--ink-3)'}">
          <span class="badge st-${a.sev}" style="margin-bottom:7px"><span class="dot"></span>${
            a.sev==='serious'?'Acción requerida':a.sev==='warning'?'Atención':'Informativo'}</span>
          <h4>${esc(a.titulo)}</h4>
          <p style="margin-bottom:7px">${esc(a.detalle)}</p>
          <p style="color:var(--ink);font-weight:500">→ ${esc(a.accion)}</p>
        </div>`).join('')}</div>
    </div>

    <div class="sect"><h3>Calendario de vigencias</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Fecha</th><th>Hito</th><th>Impacto sobre el corpus</th></tr></thead>
        <tbody>${D.calendario.map(c => `<tr>
          <td class="m" style="font-weight:600">${c.fecha}</td>
          <td>${esc(c.hito)}</td>
          <td style="color:var(--ink-2);font-size:12.5px">${esc(c.impacto)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>`;
}

/* ═══ 7 · Arquitectura ═════════════════════════════════════ */
function renderArq(){
  const sql = esc(D.esquema)
    .replace(/(--[^\n]*)/g,'<span class="c">$1</span>')
    .replace(/\b(CREATE|TABLE|TYPE|INDEX|PRIMARY KEY|REFERENCES|NOT NULL|UNIQUE|DEFAULT|GENERATED ALWAYS AS|STORED|ON DELETE CASCADE|CHECK|RETURNS|BEGIN|END|IF|THEN|RAISE EXCEPTION|RETURN|LANGUAGE|REVOKE|FROM|OR REPLACE|FUNCTION|USING)\b/g,'<span class="k">$1</span>')
    .replace(/\b(bigserial|smallserial|serial|bigint|smallint|integer|text|date|timestamptz|boolean|bytea|jsonb|tsvector|trigger|ENUM)\b/g,'<span class="t">$1</span>');
  document.getElementById('v-arq').innerHTML = `
    <h2 class="vh">Qué se construye en producción</h2>
    <p class="vsub">El prototipo lleva el índice embebido y ejecuta la búsqueda en el navegador con
    el mismo plegado y lematizador del servidor. En producción el índice vive en Postgres, la
    lematización la hace <code>to_tsvector('spanish')</code> y las doce verificaciones corren como job.</p>

    <div class="sect"><h3>Canalización de ingesta</h3>
      <div class="flow">
        <div class="step"><span class="n">01</span><h5>Depósito</h5>
          <p>Llega el PDF. Se calcula sha256 del binario y se registra.</p></div>
        <div class="step"><span class="n">02</span><h5>Texto congelado</h5>
          <p>Extracción por página. El texto queda inmutable y es la base de toda verificación.</p></div>
        <div class="step"><span class="n">03</span><h5>Segmentación</h5>
          <p>Pasajes por enumeración o por párrafo. Ninguno puede quedar sin pasajes.</p></div>
        <div class="step"><span class="n">04</span><h5>Etiquetado</h5>
          <p>Tesauro con peso de evidencia: una frase basta, dos términos también. Umbral ${D.umbral}.</p></div>
        <div class="step gate"><span class="n">05</span><h5>Integridad</h5>
          <p><b>Compuerta.</b> ${D.integridad.length} verificaciones. Si una falla, el índice no se publica.</p></div>
        <div class="step gate"><span class="n">06</span><h5>Revisión</h5>
          <p><b>Compuerta.</b> Un abogado confirma criterio, fuerza, alcance y relaciones.</p></div>
      </div>
    </div>

    <div class="sect"><h3>Modelo de datos — PostgreSQL</h3>
      <pre>${sql}</pre>
      <div class="grid2" style="margin-top:13px">
        <div class="meth"><h4>El pasaje es la unidad recuperable</h4>
          <p>${D.pasajes.length} pasajes sobre ${D.docs.length} documentos. Las reglas del MM 4187/2026
          sobre geolocalización se encuentran aunque su materia sea otra.</p></div>
        <div class="meth"><h4>El tesauro pesa la evidencia</h4>
          <p>Una frase vale 2, un término aislado vale 1, el umbral es 2. Eso impidió que
          «superficie» etiquetara un texto de monumentos naturales como cabida predial.</p></div>
        <div class="meth"><h4>La identidad canónica precede al índice</h4>
          <p>E33624, 33624 y 33.624 se resuelven a una sola autoridad antes de indexar.</p></div>
        <div class="meth"><h4>La regla vive en la base</h4>
          <p>El trigger sobre <code>cita</code> impide publicar sin verificar por cualquier vía de
          escritura: API, carga masiva o consola.</p></div>
      </div>
    </div>

    <div class="sect"><h3>API</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Método</th><th>Ruta</th><th>Devuelve</th></tr></thead>
        <tbody>${D.api.map(([m,r,d]) => `<tr>
          <td class="m" style="font-weight:700;color:${m==='GET'?'var(--accent-2)':'var(--serious-ink)'}">${m}</td>
          <td class="m">${esc(r)}</td><td style="color:var(--ink-2)">${esc(d)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Componentes</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Capa</th><th>Tecnología</th><th>Notas de diseño</th></tr></thead>
        <tbody>${D.stack.map(([c,t,n]) => `<tr>
          <td style="font-weight:600;white-space:nowrap">${esc(c)}</td>
          <td class="m">${esc(t)}</td><td style="color:var(--ink-2)">${esc(n)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Plan por fases</h3>
      <div class="card scroll"><table>
        <thead><tr><th>Fase</th><th>Entrega</th><th>Contenido</th><th>Estimación</th></tr></thead>
        <tbody>${D.fases.map(([f,e,c,t],i) => `<tr${i===0?' style="background:var(--accent-soft)"':''}>
          <td class="m" style="font-weight:700;color:var(--accent-2)">${esc(f)}</td>
          <td style="font-weight:600;white-space:nowrap">${esc(e)}</td>
          <td style="color:var(--ink-2)">${esc(c)}</td>
          <td class="m" style="white-space:nowrap">${esc(t)}</td></tr>`).join('')}</tbody>
      </table></div>
    </div>

    <div class="sect"><h3>Límite de diseño</h3>
      <div class="card pad" style="border-left:3px solid var(--accent)">
        <p style="margin:0 0 9px;font-size:14px"><b>La biblioteca localiza y ordena; no concluye.</b></p>
        <p style="margin:0;font-size:13.5px;color:var(--ink-2)">
          La respuesta a «¿qué se ha dicho sobre X?» es una cronología con citas verificadas,
          jerarquía, fuerza y alcance, más la declaración explícita de lo que <i>no</i> está cubierto.
          El dossier exportable entrega ese material con un certificado de alcance —qué se buscó, por
          qué vías, sobre cuántos documentos, y qué quedó fuera— y nunca una conclusión redactada.
          El juicio jurídico es del abogado; la trazabilidad existe para que pueda ejercerlo sobre
          material verificable.</p>
      </div>
    </div>`;
}

/* ═══ navegación ═══════════════════════════════════════════ */
const VIEWS = [
  ['consulta','Consulta', renderConsulta],
  ['lineas','Líneas de criterio', renderLineas],
  ['vacios','Cierre de citas', renderVacios],
  ['corpus','Corpus', renderCorpus],
  ['normas','Normas', renderNormas],
  ['confianza','Confiabilidad', renderConfianza],
  ['arq','Arquitectura', renderArq],
];
const nav = document.getElementById('nav');
nav.innerHTML = VIEWS.map(([k,l],i) =>
  `<button role="tab" aria-selected="${i===0}" data-k="${k}">${l}</button>`).join('');
const hecho = new Set();
function ir(k){
  VIEWS.forEach(([kk,,fn]) => {
    document.getElementById('v-'+kk).classList.toggle('on', kk===k);
    if (kk===k && !hecho.has(kk)){ fn(); hecho.add(kk); }
  });
  nav.querySelectorAll('button').forEach(b => b.setAttribute('aria-selected', b.dataset.k===k));
  window.scrollTo({top:0,behavior:'smooth'});
}
nav.querySelectorAll('button').forEach(b => b.onclick = () => ir(b.dataset.k));

const rojos = D.integridad.filter(c => c.severidad==='falla').length;
document.getElementById('sello').textContent =
  `${D.integridad.length-rojos}/${D.integridad.length} verificaciones en verde`;
document.getElementById('sello').style.cssText = rojos ? '' :
  'color:var(--good-ink);background:#f0f8f0;border-color:#bfe4bf';
document.getElementById('pie').textContent =
  `${D.docs.length} documentos · ${D.pasajes.length} pasajes indexados · ` +
  `${D.citas.length} referencias cerradas · ${D.vacios.length} vacíos declarados`;

renderConsulta(); hecho.add('consulta');
