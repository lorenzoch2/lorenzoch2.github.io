# -*- coding: utf-8 -*-
"""Compone el sitio: un diagrama de flujo recorrible de la aplicación.

Qué es
------
Un día de trabajo con la aplicación, paso a paso. En cada paso se ve **qué
hace la persona**, qué ocurre en el navegador y qué ocurre en la base de datos
o en el servicio externo que corresponda, con el dato viajando por las flechas.

Por qué así y no un texto
-------------------------
La versión anterior eran seis párrafos de ochenta palabras en gris sobre negro.
Decía cosas ciertas y no las leía nadie: no se entendía de qué iba antes de
empezar a leer, que es justo lo que una página tiene que resolver en cinco
segundos. Un diagrama se entiende antes de leerlo, y uno que se puede recorrer
se entiende usándolo.

Cómo está hecho
---------------
HTML, CSS y JavaScript a mano. El diagrama es SVG dibujado por el navegador a
partir de `PASOS`, y los puntos que viajan por las flechas son `animateMotion`,
que es nativo y no cuesta una librería. Sin framework, sin CDN, sin
dependencias: el sitio entero pesa menos que una fotografía.

    python componer-sitio.py
"""
import io
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))

#  Un color por capa. El tipo de cada nodo decide de qué color se pinta, así
#  que al recorrer los pasos la vista aprende sola qué es cada cosa: lo ámbar
#  es la persona, lo celeste el navegador, lo violeta la base y lo verde un
#  servicio de afuera.
CAPAS = {
    "persona": {"color": "#F5A65B", "etq": "La persona"},
    "front":   {"color": "#4CC9F0", "etq": "Navegador"},
    "back":    {"color": "#B18CFF", "etq": "Base de datos"},
    "externo": {"color": "#54D98C", "etq": "Servicio externo"},
}

#  Cada paso es una escena del diagrama: unos nodos colocados en una grilla de
#  cuatro carriles por cinco columnas, y las flechas entre ellos. No se guardan
#  coordenadas: el carril y la columna bastan, y así agregar un paso no obliga
#  a recalcular nada a mano.
PASOS = [
    {
        "titulo": "Entra a la app, parado en la vereda",
        "gesto": "Abre la aplicación con una mano, caminando, con la señal que haya.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Abre la app",
             "sub": "Una mano, mala señal"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Contexto de sesión",
             "sub": "React 19 · TypeScript"},
            {"id": "a",  "capa": "back",    "carril": 2, "col": 2, "etq": "Supabase Auth",
             "sub": "Devuelve un JWT"},
            {"id": "db", "capa": "back",    "carril": 2, "col": 3, "etq": "PostgreSQL",
             "sub": "Políticas por fila"},
        ],
        "flechas": [["p", "f", "toca"], ["f", "a", "credencial"], ["a", "db", "con el JWT"]],
        "nota": "No hay servidor propio: el navegador habla directo con Postgres. "
                "<b>Lo que protege los datos son las políticas de seguridad por fila</b>, "
                "no el código de la aplicación. Si el cliente miente, la base no le cree.",
    },
    {
        "titulo": "Mira el mapa del día",
        "gesto": "Ve de una los 333 locales de la campaña, agrupados donde se enciman.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Abre el mapa",
             "sub": "333 locales"},
            {"id": "q",  "capa": "front",   "carril": 1, "col": 1, "etq": "Una consulta",
             "sub": "useConsulta"},
            {"id": "db", "capa": "back",    "carril": 2, "col": 2, "etq": "PostgreSQL",
             "sub": "Filtra por política, no por código"},
            {"id": "c",  "capa": "front",   "carril": 1, "col": 3, "etq": "Agrupa y dibuja",
             "sub": "Celdas de 58 px · canvas"},
        ],
        "flechas": [["p", "q", "abre"], ["q", "db", "SELECT"], ["db", "c", "333 filas"]],
        "nota": "Los locales se juntan por celdas de 58 px calculadas con <code>mapa.project()</code> "
                "al zoom actual. <b>No se usó un plugin de clustering</b> porque el grupo tiene que "
                "pintarse con el estado más avanzado que contiene — y porque los puntos sueltos se "
                "dibujan en canvas, que aguanta 333 sin pestañear.",
    },
    {
        "titulo": "Planifica por dónde parte",
        "gesto": "Elige el punto de partida y la app ordena las paradas del día.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Traza el recorrido",
             "sub": "Desde dónde parte"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Ordena y parte",
             "sub": "Trozos de 10 paradas"},
            {"id": "v",  "capa": "externo", "carril": 3, "col": 2, "etq": "Valhalla · OSM",
             "sub": "Perfil peatonal"},
            {"id": "r",  "capa": "front",   "carril": 1, "col": 3, "etq": "Pinta el camino",
             "sub": "O línea recta punteada"},
        ],
        "flechas": [["p", "f", "toca"], ["f", "v", "10 paradas"], ["v", "r", "la ruta"]],
        "nota": "Perfil <code>pedestrian</code> porque la prospección se hace caminando: el de auto "
                "haría dar tres cuadras de vuelta para cruzar a la vereda de enfrente. El servidor "
                "acepta diez paradas, así que un recorrido largo se pide por trozos que se solapan "
                "en la parada del borde. <b>Si no contesta, vuelve la línea recta punteada y la hoja "
                "lo dice con todas sus letras.</b>",
    },
    {
        "titulo": "Entra a un local y lo registra",
        "gesto": "Toca el resultado: «atendió el dueño». Un toque, sin pasos intermedios.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Un toque",
             "sub": "«Atendió el dueño»"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Escribe al toque",
             "sub": "Y muestra «Deshacer»"},
            {"id": "v",  "capa": "back",    "carril": 2, "col": 2, "etq": "INSERT visita",
             "sub": "Queda registrada"},
            {"id": "e",  "capa": "back",    "carril": 2, "col": 3, "etq": "UPDATE estado",
             "sub": "Avanza la gestión"},
        ],
        "flechas": [["p", "f", "toca"], ["f", "v", "sin confirmar"], ["v", "e", "mismo gesto"]],
        "nota": "<b>El seguro no es confirmar antes: es poder deshacer después.</b> El aviso dura "
                "doce segundos y revierte el estado y borra la visita. Todo el resto de la "
                "aplicación es al revés —ninguna hoja guarda sin confirmar— y esta excepción es "
                "deliberada: es el gesto que se hace caminando.",
    },
    {
        "titulo": "El dueño pregunta cuánto sale",
        "gesto": "Arma el presupuesto ahí mismo, de pie en el mesón.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Cotiza",
             "sub": "En el mesón"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Arma las líneas",
             "sub": "Servicios y cantidades"},
            {"id": "t",  "capa": "back",    "carril": 2, "col": 2, "etq": "Precio en cascada",
             "sub": "Cliente → zona → general"},
            {"id": "n",  "capa": "front",   "carril": 1, "col": 3, "etq": "Total a la vista",
             "sub": "Neto, IVA y total"},
        ],
        "flechas": [["p", "f", "elige"], ["f", "t", "¿cuánto vale?"], ["t", "n", "el que aplica"]],
        "nota": "Un tarifario especial guarda <b>sólo lo que de verdad cambia</b> y el resto lo "
                "hereda. La cascada vive en una función y no se duplica en las pantallas, porque "
                "un precio que se calcula en dos lugares termina siendo dos precios.",
    },
    {
        "titulo": "Se lo manda por WhatsApp, ahí mismo",
        "gesto": "El presupuesto sale del teléfono al teléfono del cliente, sin pasar por nadie.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Pide el PDF",
             "sub": "Y lo comparte"},
            {"id": "l",  "capa": "front",   "carril": 1, "col": 1, "etq": "Carga jsPDF",
             "sub": "Recién ahora: 130 KB"},
            {"id": "d",  "capa": "front",   "carril": 1, "col": 2, "etq": "Compone el documento",
             "sub": "Fuentes incrustadas"},
            {"id": "s",  "capa": "persona", "carril": 0, "col": 3, "etq": "Menú de compartir",
             "sub": "54 KB"},
        ],
        "flechas": [["p", "l", "toca"], ["l", "d", "comprime"], ["d", "s", "54 KB"]],
        "nota": "<b>El servidor no participa.</b> Dos cuidados costaron encontrar: "
                "<code>compress: true</code> en el constructor —sin eso el logotipo entra como mapa "
                "de bits crudo y el archivo pesa 1,6 MB en vez de 54 KB— y el módulo se importa "
                "sólo al pedir el PDF, porque jsPDF más las fuentes son 130 KB comprimidos que "
                "nadie necesita para mirar un pendiente.",
    },
    {
        "titulo": "Cierra la mantención del mes",
        "gesto": "Termina el trabajo, lo cierra, y la próxima queda agendada sola.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Cierra",
             "sub": "Un solo botón"},
            {"id": "c",  "capa": "back",    "carril": 2, "col": 1, "etq": "Cierra la actual",
             "sub": "Con su fecha"},
            {"id": "s",  "capa": "back",    "carril": 2, "col": 2, "etq": "Agenda la siguiente",
             "sub": "Según su frecuencia"},
            {"id": "u",  "capa": "back",    "carril": 2, "col": 3, "etq": "Actualiza el equipo",
             "sub": "ultima_mantencion"},
        ],
        "flechas": [["p", "c", "toca"], ["c", "s", "y agenda"], ["s", "u", "y actualiza"]],
        "nota": "Es el motor del ingreso recurrente: <b>si la próxima no queda agendada al cerrar "
                "la anterior, no la agenda nadie.</b> Por eso una función hace las tres cosas y no "
                "hay una pantalla aparte que haya que acordarse de abrir.",
    },
    {
        "titulo": "Cuando la red se cae",
        "gesto": "Pasa todos los días: un local sin señal, un subterráneo, un ascensor.",
        "nodos": [
            {"id": "q",  "capa": "front",   "carril": 1, "col": 0, "etq": "La consulta sale",
             "sub": "Y no vuelve"},
            {"id": "x",  "capa": "externo", "carril": 3, "col": 1, "etq": "Sin red",
             "sub": "Supabase reintenta 7 s"},
            {"id": "r",  "capa": "front",   "carril": 1, "col": 2, "etq": "Reporta cómo le fue",
             "sub": "No devuelve []"},
            {"id": "b",  "capa": "persona", "carril": 0, "col": 3, "etq": "Franja de aviso",
             "sub": "Arriba, visible"},
        ],
        "flechas": [["q", "x", "fetch"], ["x", "r", "falla"], ["r", "b", "avisa"]],
        "nota": "Las pantallas pintan <code>datos ?? []</code>. Sin aviso, la ficha de un cliente "
                "diría «sin equipos cargados» cuando lo que pasó es que no cargó nada, y uno sale a "
                "trabajar creyendo algo falso. <b>Una consulta que falla no puede verse igual que "
                "una lista vacía.</b> En vez de repetir el manejo de error en veinticuatro "
                "pantallas, cada consulta reporta cómo le fue y un éxito borra la racha.",
    },
]

CIFRAS = [
    ("54 KB", "pesa el presupuesto en PDF, desde 1,6 MB"),
    ("333", "locales en el mapa, dibujados en canvas"),
    ("0", "servidores propios"),
]

CORREO = "lorenzochacano@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/lorenzochacano"
GITHUB = "https://github.com/lorenzoch2"

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --fondo:#0B0F16; --panel:#121926; --linea:#1F2A3C; --papel:#EEF2F8; --mute:#8595AD;
  --persona:#F5A65B; --front:#4CC9F0; --back:#B18CFF; --externo:#54D98C;
}
body{font-family:Archivo,system-ui,-apple-system,sans-serif;background:var(--fondo);
 color:var(--papel);line-height:1.6;-webkit-font-smoothing:antialiased;font-size:16px}
.col{max-width:1060px;margin:0 auto;padding:0 22px}
a{color:var(--front);text-decoration:none}
a:hover{text-decoration:underline}
code{font-family:PlexMono,ui-monospace,monospace;font-size:.87em;background:#0D1420;
 border:1px solid var(--linea);border-radius:4px;padding:.08em .36em}
b{font-weight:600;color:var(--papel)}

nav{border-bottom:1px solid var(--linea);background:rgba(11,15,22,.9);
 backdrop-filter:blur(8px);position:sticky;top:0;z-index:20}
nav .col{display:flex;align-items:center;justify-content:space-between;height:56px}
nav .yo{font-weight:700;letter-spacing:-.01em}
nav .liga{font-family:PlexMono,monospace;font-size:12px;color:var(--mute);letter-spacing:.06em}

header{padding:62px 0 34px}
.rot{font-family:PlexMono,monospace;font-size:11.5px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--front)}
h1{font-size:clamp(28px,4.6vw,40px);font-weight:700;line-height:1.14;
 letter-spacing:-.025em;margin:14px 0 16px;max-width:19ch}
h1 em{font-style:normal;color:var(--persona)}
header p{color:var(--mute);max-width:60ch}
.cifras{display:flex;flex-wrap:wrap;gap:30px;margin-top:26px}
.cifras .n{font-family:PlexMono,monospace;font-size:20px;color:var(--papel)}
.cifras .g{font-size:13px;color:var(--mute);margin-top:2px}

/* ── El recorrido ───────────────────────────────────────────────── */
.barra{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:10px 0 18px}
.pasos{display:flex;gap:7px;flex-wrap:wrap;flex:1}
.chip{width:34px;height:34px;border-radius:9px;border:1px solid var(--linea);
 background:var(--panel);color:var(--mute);font-family:PlexMono,monospace;font-size:13px;
 cursor:pointer;transition:.18s;flex:none}
.chip:hover{border-color:var(--front);color:var(--papel)}
.chip[aria-current=true]{background:var(--front);border-color:var(--front);color:#07101A;
 font-weight:700}
.chip.visto{color:var(--papel);border-color:#2C3C55}
.play{display:flex;align-items:center;gap:8px;border:1px solid var(--linea);
 background:var(--panel);color:var(--papel);border-radius:9px;padding:8px 15px;
 font-family:inherit;font-size:13.5px;font-weight:600;cursor:pointer;transition:.18s}
.play:hover{border-color:var(--front)}
.play b{width:8px;height:8px;border-radius:50%;background:var(--externo);display:block}
.play.on b{background:var(--persona);animation:lat 1.1s infinite}
@keyframes lat{50%{opacity:.25}}

.escena{border:1px solid var(--linea);border-radius:16px;background:var(--panel);
 overflow:hidden}
.cab{padding:20px 24px 0}
.cab .np{font-family:PlexMono,monospace;font-size:12px;color:var(--front);letter-spacing:.08em}
.cab h2{font-size:clamp(19px,2.6vw,25px);font-weight:700;letter-spacing:-.02em;margin:5px 0 4px}
.cab .gesto{color:var(--mute);font-size:14.5px;max-width:62ch}

.lienzo{overflow-x:auto;padding:4px 10px 0}
svg.dg{display:block;width:100%;min-width:720px;height:auto}
.nodo rect{transition:.25s}
.nodo .et{font-weight:600;font-size:12.5px;fill:var(--papel)}
.nodo .sb{font-size:10.5px;fill:var(--mute)}
.carril{font-family:PlexMono,monospace;font-size:9.5px;letter-spacing:.12em;
 text-transform:uppercase}
.fl{stroke-width:1.5;fill:none}
.flet{font-family:PlexMono,monospace;font-size:9.5px;fill:var(--mute)}

.nota{padding:4px 24px 22px;color:var(--mute);font-size:14.5px;max-width:74ch}

.leyenda{display:flex;gap:18px;flex-wrap:wrap;padding:0 24px 20px;
 font-family:PlexMono,monospace;font-size:10.5px;letter-spacing:.07em;text-transform:uppercase}
.leyenda span{display:flex;align-items:center;gap:7px;color:var(--mute)}
.leyenda i{width:9px;height:9px;border-radius:3px;display:block}

.pista{margin:14px 0 54px;color:var(--mute);font-size:13px;font-family:PlexMono,monospace}
kbd{border:1px solid var(--linea);border-radius:4px;padding:1px 6px;font-size:11px;
 background:var(--panel)}

section.fin{border-top:1px solid var(--linea);padding:48px 0 60px}
section.fin h2{font-size:clamp(21px,3vw,27px);font-weight:700;letter-spacing:-.02em;margin:12px 0 16px}
section.fin p{color:var(--mute);max-width:64ch;margin-bottom:14px}
.enlaces{display:flex;flex-wrap:wrap;gap:11px;margin-top:22px}
.enlaces a{border:1px solid var(--linea);border-radius:9px;padding:11px 17px;
 color:var(--papel);font-size:14.5px;font-weight:600}
.enlaces a:hover{border-color:var(--front);color:var(--front);text-decoration:none}
footer{padding:0 0 46px;color:var(--mute);font-size:12.5px;font-family:PlexMono,monospace}
@media(max-width:720px){nav .liga{display:none}}
@media(max-width:560px){header{padding:46px 0 26px}.cab{padding:16px 17px 0}
 .nota,.leyenda{padding-left:17px;padding-right:17px}}
"""

JS = """
const CAPAS = __CAPAS__, PASOS = __PASOS__;
const NS = 'http://www.w3.org/2000/svg';
const COLW = 196, FILA = 96, X0 = 104, Y0 = 44, NW = 148, NH = 50;
let actual = 0, auto = null;

const col = c => getComputedStyle(document.documentElement).getPropertyValue('--' + c).trim();
const el = (t, a = {}) => { const n = document.createElementNS(NS, t);
  for (const k in a) n.setAttribute(k, a[k]); return n; };

function dibujar(p) {
  const cols = Math.max(...p.nodos.map(n => n.col)) + 1;
  const carriles = [...new Set(p.nodos.map(n => n.carril))].sort();
  const W = X0 + cols * COLW, H = Y0 + carriles.length * FILA + 18;
  const svg = el('svg', {class: 'dg', viewBox: `0 0 ${W} ${H}`, role: 'img',
                         'aria-label': p.titulo});
  const fila = {}; carriles.forEach((c, i) => fila[c] = Y0 + i * FILA);
  const pos = {};
  p.nodos.forEach(n => pos[n.id] = {x: X0 + n.col * COLW, y: fila[n.carril], capa: n.capa});

  // Rótulo de cada carril, a la izquierda
  carriles.forEach(c => {
    const capa = p.nodos.find(n => n.carril === c).capa;
    const t = el('text', {x: 8, y: fila[c] + NH / 2 + 3, class: 'carril', fill: col(capa)});
    t.textContent = CAPAS[capa].etq; svg.appendChild(t);
    svg.appendChild(el('line', {x1: 8, y1: fila[c] + NH + 12, x2: W - 10,
      y2: fila[c] + NH + 12, stroke: 'var(--linea)', 'stroke-width': 1,
      'stroke-dasharray': '2 6'}));
  });

  // Flechas primero, para que queden bajo los nodos
  p.flechas.forEach((f, i) => {
    const a = pos[f[0]], b = pos[f[1]];
    const x1 = a.x + NW, y1 = a.y + NH / 2, x2 = b.x, y2 = b.y + NH / 2;
    const mx = (x1 + x2) / 2;
    const d = `M${x1} ${y1} C${mx} ${y1} ${mx} ${y2} ${x2 - 7} ${y2}`;
    const g = el('g'); g.style.opacity = 0;
    g.appendChild(el('path', {d, class: 'fl', stroke: 'var(--linea)'}));
    const vis = el('path', {d, class: 'fl', stroke: col(b.capa), 'stroke-opacity': .55});
    vis.style.strokeDasharray = 600; vis.style.strokeDashoffset = 600;
    vis.style.transition = 'stroke-dashoffset .5s ease ' + (i * .32 + .25) + 's';
    g.appendChild(vis);
    svg.appendChild(g);
    setTimeout(() => { g.style.transition = 'opacity .3s'; g.style.opacity = 1;
                       vis.style.strokeDashoffset = 0; }, 20);

    // Punta
    const pt = el('path', {d: `M${x2 - 9} ${y2 - 4.5} L${x2 - 1} ${y2} L${x2 - 9} ${y2 + 4.5}`,
      fill: col(b.capa), opacity: .75});
    g.appendChild(pt);
    // La etiqueta de la flecha
    if (f[2]) { const t = el('text', {x: mx, y: Math.min(y1, y2) - 32, class: 'flet',
      'text-anchor': 'middle'}); t.textContent = f[2]; g.appendChild(t); }
    // El dato viajando
    const c = el('circle', {r: 3.6, fill: col(b.capa)});
    const am = el('animateMotion', {dur: '1.9s', repeatCount: 'indefinite',
      path: d, begin: (i * .45) + 's', keyPoints: '0;1', keyTimes: '0;1', calcMode: 'linear'});
    c.appendChild(am); g.appendChild(c);
  });

  // Nodos
  p.nodos.forEach((n, i) => {
    const {x, y} = pos[n.id], c = col(n.capa);
    const g = el('g', {class: 'nodo'});
    g.style.opacity = 0; g.style.transform = 'translateY(7px)';
    g.style.transition = `opacity .34s ease ${i * .09}s, transform .34s ease ${i * .09}s`;
    g.appendChild(el('rect', {x, y, width: NW, height: NH, rx: 11, fill: c,
      'fill-opacity': .13, stroke: c, 'stroke-width': 1.5}));
    g.appendChild(el('rect', {x, y, width: 3.5, height: NH, rx: 2, fill: c}));
    const t1 = el('text', {x: x + 15, y: y + 21, class: 'et'}); t1.textContent = n.etq;
    const t2 = el('text', {x: x + 15, y: y + 37, class: 'sb'}); t2.textContent = n.sub;
    g.append(t1, t2); svg.appendChild(g);
    setTimeout(() => { g.style.opacity = 1; g.style.transform = 'none'; }, 20);
  });
  return svg;
}

function ir(i, porAuto) {
  actual = (i + PASOS.length) % PASOS.length;
  const p = PASOS[actual];
  document.querySelectorAll('.chip').forEach((c, k) => {
    c.setAttribute('aria-current', k === actual);
    c.classList.toggle('visto', k < actual);
  });
  document.getElementById('np').textContent =
    'Paso ' + String(actual + 1).padStart(2, '0') + ' de ' + String(PASOS.length).padStart(2, '0');
  document.getElementById('tt').textContent = p.titulo;
  document.getElementById('gs').textContent = p.gesto;
  document.getElementById('nt').innerHTML = p.nota;
  const l = document.getElementById('lz'); l.innerHTML = ''; l.appendChild(dibujar(p));
  if (!porAuto) parar();
}

function parar() { if (auto) { clearInterval(auto); auto = null;
  document.getElementById('pl').classList.remove('on');
  document.getElementById('plt').textContent = 'Reproducir'; } }

document.addEventListener('DOMContentLoaded', () => {
  const cont = document.getElementById('chips');
  PASOS.forEach((p, i) => { const b = document.createElement('button');
    b.className = 'chip'; b.textContent = i + 1; b.type = 'button';
    b.title = p.titulo; b.setAttribute('aria-label', 'Paso ' + (i + 1) + ': ' + p.titulo);
    b.onclick = () => ir(i); cont.appendChild(b); });

  document.getElementById('pl').onclick = function () {
    if (auto) return parar();
    this.classList.add('on');
    document.getElementById('plt').textContent = 'Pausar';
    ir(actual + 1, true);
    auto = setInterval(() => ir(actual + 1, true), 5200);
  };
  addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') ir(actual + 1);
    if (e.key === 'ArrowLeft') ir(actual - 1);
  });
  ir(0);
});
"""


def fuentes():
    return "".join(
        f"@font-face{{font-family:'{f}';font-weight:{w};font-style:normal;font-display:swap;"
        f"src:url(assets/fonts/{n}) format('woff2')}}"
        for n, f, w in (("Archivo-400.woff2", "Archivo", 400), ("Archivo-600.woff2", "Archivo", 600),
                        ("Archivo-700.woff2", "Archivo", 700),
                        ("IBMPlexMono-400.woff2", "PlexMono", 400)))


def pagina():
    cifras = "".join(f'<div><div class="n">{n}</div><div class="g">{g}</div></div>'
                     for n, g in CIFRAS)
    leyenda = "".join(f'<span><i style="background:{v["color"]}"></i>{v["etq"]}</span>'
                      for v in CAPAS.values())
    js = JS.replace("__CAPAS__", json.dumps(CAPAS, ensure_ascii=False)) \
           .replace("__PASOS__", json.dumps(PASOS, ensure_ascii=False))
    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Lorenzo Chacano · Analytics Engineer</title>
<meta name="description" content="Un día de trabajo con una aplicación en producción, paso a
 paso: qué hace la persona, qué hace el navegador y qué hace la base de datos.">
<meta name="color-scheme" content="dark">
<meta property="og:title" content="Lorenzo Chacano · Analytics Engineer">
<meta property="og:description" content="Un día de trabajo con una aplicación en producción,
 paso a paso.">
<style>{fuentes()}{CSS}</style>
</head><body>

<nav><div class="col">
  <span class="yo">Lorenzo Chacano</span>
  <span class="liga">ANALYTICS ENGINEER · DATA ENGINEER</span>
</div></nav>

<header><div class="col">
  <div class="rot">Un día con la aplicación</div>
  <h1>Qué pasa, de verdad, cuando alguien <em>toca un botón</em></h1>
  <p>Diseñé y construí entera la aplicación de gestión de Calor y Frío Industrial, la empresa de
  climatización que dirijo en Santiago. Está en producción y se usa todos los días en terreno.
  Esto es un día de trabajo con ella: el gesto de la persona arriba, y debajo lo que ocurre en el
  navegador, en la base de datos y en los servicios de afuera.</p>
  <div class="cifras">{cifras}</div>
</div></header>

<div class="col">
  <div class="barra">
    <div class="pasos" id="chips"></div>
    <button class="play" id="pl" type="button"><b></b><span id="plt">Reproducir</span></button>
  </div>

  <div class="escena">
    <div class="cab">
      <div class="np" id="np"></div>
      <h2 id="tt"></h2>
      <p class="gesto" id="gs"></p>
    </div>
    <div class="lienzo" id="lz"></div>
    <div class="leyenda">{leyenda}</div>
    <p class="nota" id="nt"></p>
  </div>

  <p class="pista">Toca un número, o muévete con <kbd>←</kbd> <kbd>→</kbd></p>
</div>

<section class="fin"><div class="col">
  <div class="rot">Antes de esto</div>
  <h2>Analytics Engineer en Gregario SpA</h2>
  <p>Bajé el costo de infraestructura de <b>800 a 20 USD mensuales</b> migrando los procesos a
  Google Cloud Platform con Docker, y reduje la tasa de error en un <b>98 %</b> reestructurando la
  arquitectura SQL a SQLMesh. También saqué del código los secretos y contraseñas, estandarizando
  cuentas de servicio, y puse detección y freno automático de procesos colgados.</p>
  <p>El código es de la empresa, así que lo que queda son los resultados.</p>
  <div class="rot" style="margin-top:36px">Contacto</div>
  <h2>Busco un cargo de Analytics Engineer o Data Engineer, remoto o híbrido.</h2>
  <div class="enlaces">
    <a href="mailto:{CORREO}">{CORREO}</a>
    <a href="{LINKEDIN}" rel="me">LinkedIn</a>
    <a href="{GITHUB}" rel="me">GitHub</a>
  </div>
</div></section>

<footer><div class="col">HTML, CSS y JavaScript a mano. Sin framework, sin CDN,
 sin dependencias.</div></footer>
<script>{js}</script>
</body></html>"""


def main():
    ruta = os.path.join(AQUI, "index.html")
    io.open(ruta, "w", encoding="utf-8").write(pagina())
    print(f"    index.html  {os.path.getsize(ruta) / 1024:.1f} KB  ·  {len(PASOS)} pasos")


if __name__ == "__main__":
    main()
