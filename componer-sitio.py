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
    "persona": {"color": "#F5A65B", "etq": "Usuario"},
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
        "titulo": "Autenticación e inicio de sesión",
        "gesto": "El usuario abre la aplicación en el teléfono, en terreno.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Apertura",
             "sub": "Dispositivo móvil"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Contexto de sesión",
             "sub": "React 19 · TypeScript"},
            {"id": "a",  "capa": "back",    "carril": 2, "col": 2, "etq": "Supabase Auth",
             "sub": "Emite un JWT"},
            {"id": "db", "capa": "back",    "carril": 2, "col": 3, "etq": "PostgreSQL",
             "sub": "Políticas por fila"},
        ],
        "flechas": [["p", "f", "apertura"], ["f", "a", "credencial"], ["a", "db", "JWT"]],
        "nota": "La aplicación no dispone de servidor propio: el navegador consulta PostgreSQL "
                "directamente. El control de acceso está implementado mediante <b>políticas de "
                "seguridad por fila en la base de datos</b>, no en el código de la aplicación.",
    },
    {
        "titulo": "Carga del mapa y agrupamiento de puntos",
        "gesto": "El usuario consulta sobre el mapa los 333 locales de la campaña.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Consulta el mapa",
             "sub": "333 locales"},
            {"id": "q",  "capa": "front",   "carril": 1, "col": 1, "etq": "Consulta",
             "sub": "useConsulta"},
            {"id": "db", "capa": "back",    "carril": 2, "col": 2, "etq": "PostgreSQL",
             "sub": "Filtrado por política"},
            {"id": "c",  "capa": "front",   "carril": 1, "col": 3, "etq": "Agrupa y dibuja",
             "sub": "Celdas de 58 px · canvas"},
        ],
        "flechas": [["p", "q", "apertura"], ["q", "db", "SELECT"], ["db", "c", "333 filas"]],
        "nota": "Los puntos se agrupan por celdas de 58 px calculadas con <code>mapa.project()</code> "
                "al nivel de zoom vigente. No se empleó una biblioteca de agrupamiento por dos "
                "requisitos: <b>el grupo debe representarse con el estado de gestión más avanzado "
                "que contiene</b>, y los puntos individuales se dibujan sobre canvas para sostener "
                "333 elementos sin pérdida de rendimiento.",
    },
    {
        "titulo": "Trazado del recorrido",
        "gesto": "El usuario selecciona el punto de partida y solicita el trazado del recorrido.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Solicita el trazado",
             "sub": "Define el origen"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Ordena y segmenta",
             "sub": "Tramos de 10 paradas"},
            {"id": "v",  "capa": "externo", "carril": 3, "col": 2, "etq": "Valhalla · OSM",
             "sub": "Perfil peatonal"},
            {"id": "r",  "capa": "front",   "carril": 1, "col": 3, "etq": "Representa el trazado",
             "sub": "O línea recta"},
        ],
        "flechas": [["p", "f", "solicitud"], ["f", "v", "10 paradas"], ["v", "r", "ruta"]],
        "nota": "Se emplea el perfil <code>pedestrian</code> porque el recorrido se realiza a pie; "
                "el perfil de automóvil introduce desvíos por sentido de circulación. El servicio "
                "admite diez paradas por consulta, de modo que los recorridos extensos se "
                "solicitan en tramos que se solapan en la parada límite. <b>Ante falta de "
                "respuesta se traza la línea recta y la interfaz indica que el recorrido no está "
                "medido.</b>",
    },
    {
        "titulo": "Registro de visita",
        "gesto": "El usuario registra el resultado de la visita con una sola pulsación.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Una pulsación",
             "sub": "Resultado de la visita"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Escritura inmediata",
             "sub": "Reversión por 12 s"},
            {"id": "v",  "capa": "back",    "carril": 2, "col": 2, "etq": "INSERT visita",
             "sub": "Queda registrada"},
            {"id": "e",  "capa": "back",    "carril": 2, "col": 3, "etq": "UPDATE estado",
             "sub": "Avanza la gestión"},
        ],
        "flechas": [["p", "f", "pulsación"], ["f", "v", "INSERT"], ["v", "e", "UPDATE"]],
        "nota": "El registro se escribe sin confirmación previa y se ofrece una <b>reversión "
                "durante doce segundos</b>, que elimina la visita y restituye el estado anterior. "
                "El resto de la aplicación exige confirmación explícita; la excepción responde a "
                "que esta operación se ejecuta en desplazamiento.",
    },
    {
        "titulo": "Cotización en terreno",
        "gesto": "El usuario elabora un presupuesto en el domicilio del cliente.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Elabora el presupuesto",
             "sub": "En el domicilio"},
            {"id": "f",  "capa": "front",   "carril": 1, "col": 1, "etq": "Compone las líneas",
             "sub": "Servicios y cantidades"},
            {"id": "t",  "capa": "back",    "carril": 2, "col": 2, "etq": "Resolución en cascada",
             "sub": "Cliente → zona → general"},
            {"id": "n",  "capa": "front",   "carril": 1, "col": 3, "etq": "Totales",
             "sub": "Neto, IVA y total"},
        ],
        "flechas": [["p", "f", "selección"], ["f", "t", "consulta"], ["t", "n", "tarifa"]],
        "nota": "Un tarifario particular almacena únicamente los precios que difieren del nivel "
                "superior; el resto se hereda. <b>La resolución está implementada en una única "
                "función</b> y no se replica en las pantallas.",
    },
    {
        "titulo": "Generación del documento PDF",
        "gesto": "El usuario solicita el documento y lo entrega por el menú de compartir del "
                 "sistema.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Solicita el documento",
             "sub": "Entrega al cliente"},
            {"id": "l",  "capa": "front",   "carril": 1, "col": 1, "etq": "Importación diferida",
             "sub": "jsPDF · 130 KB"},
            {"id": "d",  "capa": "front",   "carril": 1, "col": 2, "etq": "Composición",
             "sub": "Tipografías incrustadas"},
            {"id": "s",  "capa": "persona", "carril": 0, "col": 3, "etq": "Menú de compartir",
             "sub": "54 KB"},
        ],
        "flechas": [["p", "l", "solicitud"], ["l", "d", "comprime"], ["d", "s", "54 KB"]],
        "nota": "La composición ocurre íntegramente en el cliente; el servidor no interviene. Dos "
                "parámetros determinan el resultado: <code>compress: true</code> en el "
                "constructor, sin el cual el logotipo se incorpora como mapa de bits sin comprimir "
                "y el archivo alcanza <b>1,6 MB en lugar de 54 KB</b>; y la importación diferida "
                "del módulo, dado que jsPDF y las tipografías suman 130 KB comprimidos.",
    },
    {
        "titulo": "Cierre de mantención programada",
        "gesto": "El usuario cierra la mantención ejecutada.",
        "nodos": [
            {"id": "p",  "capa": "persona", "carril": 0, "col": 0, "etq": "Cierra",
             "sub": "Mantención ejecutada"},
            {"id": "c",  "capa": "back",    "carril": 2, "col": 1, "etq": "Cierra la vigente",
             "sub": "Con su fecha"},
            {"id": "s",  "capa": "back",    "carril": 2, "col": 2, "etq": "Programa la siguiente",
             "sub": "Según la frecuencia"},
            {"id": "u",  "capa": "back",    "carril": 2, "col": 3, "etq": "Actualiza el equipo",
             "sub": "ultima_mantencion"},
        ],
        "flechas": [["p", "c", "cierre"], ["c", "s", "programa"], ["s", "u", "actualiza"]],
        "nota": "El cierre ejecuta tres operaciones: cierra la mantención vigente, programa la "
                "siguiente según la frecuencia del contrato y actualiza la fecha de última "
                "mantención del equipo. <b>La programación automática evita la omisión del ciclo "
                "siguiente</b>, que es el mecanismo del ingreso recurrente.",
    },
    {
        "titulo": "Degradación ante fallo de red",
        "gesto": "La consulta no obtiene respuesta por ausencia de cobertura.",
        "nodos": [
            {"id": "q",  "capa": "front",   "carril": 1, "col": 0, "etq": "Consulta emitida",
             "sub": "Sin respuesta"},
            {"id": "x",  "capa": "externo", "carril": 3, "col": 1, "etq": "Sin cobertura",
             "sub": "Reintentos, 7 s"},
            {"id": "r",  "capa": "front",   "carril": 1, "col": 2, "etq": "Informa el resultado",
             "sub": "No devuelve []"},
            {"id": "b",  "capa": "persona", "carril": 0, "col": 3, "etq": "Aviso en pantalla",
             "sub": "Franja superior"},
        ],
        "flechas": [["q", "x", "fetch"], ["x", "r", "error"], ["r", "b", "aviso"]],
        "nota": "Las pantallas representan <code>datos ?? []</code>. Sin señalización, <b>un fallo "
                "de consulta resulta indistinguible de un conjunto vacío</b>: la ficha de un "
                "cliente indicaría que no tiene equipos registrados. Cada consulta informa su "
                "resultado y la interfaz muestra un aviso cuando se acumulan fallos; una respuesta "
                "correcta reinicia el contador.",
    },
]

#  El retrato. Se acepta cualquiera de estas extensiones para que baste con
#  dejar el archivo en su sitio, sin convertirlo antes. Si no hay ninguna, va
#  un monograma: un hueco con las iniciales se ve deliberado; una imagen rota,
#  no.
FOTOS = ("assets/foto.jpg", "assets/foto.jpeg", "assets/foto.png", "assets/foto.webp")


def retrato_archivo():
    for f in FOTOS:
        if os.path.exists(os.path.join(AQUI, f)):
            return f
    return None

PERFIL = {
    "nombre": "Lorenzo Chacano",
    "rol": "Analytics Engineer · Data Engineer",
    "texto": "Trabajo con Python, SQL y Google Cloud Platform sobre procesos de datos en "
             "producción: infraestructura, costo operacional y confiabilidad de los flujos. "
             "Estudio Ingeniería en Ciencia de Datos en la Universidad Andrés Bello.",
    "lugar": "Santiago, Chile",
}

CORREO = "lorenzochacano@gmail.com"

EXPERIENCIA = [
    {
        "empresa": "Calor y Frío Industrial SpA",
        "cargo": "Responsable de Tecnología",
        "periodo": "2026 – presente",
        "texto": "Infraestructura tecnológica de la empresa y desarrollo de la aplicación de "
                 "gestión con que opera: modelo de datos, interfaz, despliegue y operación.",
    },
    {
        "empresa": "Gregario SpA",
        "cargo": "Analytics Engineer",
        "periodo": "2024 – 2025",
        "texto": "Infraestructura de datos y procesos de transformación: confiabilidad de los "
                 "flujos, costo de la nube y cumplimiento de las políticas sobre credenciales.",
        "logros": [
            "Reducción del costo de infraestructura de <b>800 a 20 USD mensuales</b> mediante "
            "migración a Google Cloud Platform con Docker.",
            "Reducción del <b>98 %</b> en la tasa de error de los procesos mediante "
            "reestructuración de la arquitectura SQL a SQLMesh.",
            "Eliminación de credenciales del código fuente mediante estandarización de cuentas "
            "de servicio.",
            "Detección y detención automática de procesos con tardanza inesperada, con alertas "
            "tempranas.",
        ],
        "nota": "El código es propiedad de la empresa; se documentan únicamente los resultados.",
    },
    {
        "empresa": "Mesati",
        "cargo": "Desarrollador Web Front-End",
        "periodo": "2023 – 2024",
        "texto": "Diseño, desarrollo e implementación del sitio web corporativo, con criterio "
                 "de minimizar el costo de mantención posterior.",
    },
]

PROYECTO = {
    "nombre": "Aplicación de gestión en terreno",
    "linea": "Calor y Frío Industrial · en producción, uso diario",
    "texto": "Aplicación con que opera una empresa de climatización de Santiago: prospección, "
             "clientes, presupuestos, inventario, mantenciones programadas, informes técnicos y "
             "caja. Diseño, modelo de datos, desarrollo y despliegue propios. El diagrama "
             "siguiente recorre ocho operaciones: la acción del usuario, el procesamiento en el "
             "navegador y las operaciones sobre la base de datos y los servicios externos.",
    "stack": "React 19 · TypeScript · Vite · Supabase · PostgreSQL · Netlify · Valhalla/OSM",
}

#  LinkedIn y GitHub son marcas: van sus logotipos reales, de simple-icons —un
#  solo trazo y un solo color, que es justo lo que hace falta para pintarlos
#  con el color de su tarjeta—. Dibujarlos a mano sale deforme, y un logotipo
#  ajeno mal trazado se ve peor que ninguno.
#
#  Los otros dos no son marcas con logotipo monocromo disponible, así que van
#  dibujados acá: son cuatro trazos y no justifican una dependencia.
ICO = {
    "mail": ("trazo", '<rect x="3" y="5" width="18" height="14" rx="2.5"/>'
                      '<path d="m3.7 7.1 8.3 5.9 8.3-5.9"/>'),
    "gob": ("trazo", '<path d="M12 3.4 4.4 7.3v4.9c0 4.1 3.2 7 7.6 7.7 4.4-.7 7.6-3.6 '
                     '7.6-7.7V7.3z"/><path d="m9.1 11.9 2.1 2.1 3.8-4.1"/>'),
    "linkedin": ("relleno", '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>'),
    "github": ("relleno", '<path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>'),
}

REDES = [
    {"ico": "mail", "capa": "front", "etq": "Correo", "val": CORREO,
     "href": "mailto:" + CORREO},
    {"ico": "linkedin", "capa": "persona", "etq": "LinkedIn", "val": "in/lorenzo-chacano",
     "href": "https://www.linkedin.com/in/lorenzo-chacano"},
    {"ico": "github", "capa": "back", "etq": "GitHub", "val": "lorenzoch2",
     "href": "https://github.com/lorenzoch2"},
    {"ico": "gob", "capa": "externo", "etq": "Get on Board", "val": "p/lorenzo-chacano",
     "href": "https://www.getonbrd.com/p/lorenzo-chacano"},
]


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

header{padding:52px 0 34px}
.rot{font-family:PlexMono,monospace;font-size:11.5px;letter-spacing:.16em;
 text-transform:uppercase;color:var(--front)}
h1{font-size:clamp(28px,4.6vw,40px);font-weight:700;line-height:1.14;
 letter-spacing:-.025em;margin:14px 0 16px;max-width:19ch}
h1 em{font-style:normal;color:var(--persona)}
header p{color:var(--mute);max-width:60ch}

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

.pista{margin:14px 0 0;color:var(--mute);font-size:13px;font-family:PlexMono,monospace}
kbd{border:1px solid var(--linea);border-radius:4px;padding:1px 6px;font-size:11px;
 background:var(--panel)}

footer{padding:0 0 46px;color:var(--mute);font-size:12.5px;font-family:PlexMono,monospace}

/* ── Pestañas ───────────────────────────────────────────────────── */
.tabs{display:flex;gap:6px;border-bottom:1px solid var(--linea);margin-bottom:0;
 position:sticky;top:56px;background:rgba(11,15,22,.94);backdrop-filter:blur(8px);z-index:10;
 overflow-x:auto;scrollbar-width:none}
.tabs::-webkit-scrollbar{display:none}
.tab{appearance:none;background:none;border:0;border-bottom:2px solid transparent;
 color:var(--mute);font-family:inherit;font-size:15px;font-weight:600;letter-spacing:-.01em;
 padding:16px 18px 14px;cursor:pointer;transition:.18s;white-space:nowrap;
 display:flex;align-items:center;gap:9px}
.tab:hover{color:var(--papel)}
.tab i{font-family:PlexMono,monospace;font-style:normal;font-size:11px;opacity:.6}
.tab[aria-selected=true]{color:var(--papel);border-bottom-color:var(--front)}
.tab[aria-selected=true] i{color:var(--front);opacity:1}
.panel{padding:40px 0 60px;animation:aparece .32s ease}
.panel[hidden]{display:none}
@keyframes aparece{from{opacity:0;transform:translateY(7px)}to{opacity:1;transform:none}}

/* ── Experiencia: línea de tiempo ───────────────────────────────── */
.linea-t{position:relative;padding-left:30px}
.linea-t::before{content:"";position:absolute;left:5px;top:9px;bottom:9px;width:1px;
 background:linear-gradient(var(--front),var(--back),transparent)}
.linea-t article{position:relative;padding:0 0 34px}
.linea-t article:last-child{padding-bottom:0}
.linea-t article::before{content:"";position:absolute;left:-29px;top:7px;width:11px;height:11px;
 border-radius:50%;background:var(--fondo);border:2px solid var(--front)}
.linea-t article:nth-child(2)::before{border-color:var(--back)}
.linea-t article:nth-child(3)::before{border-color:var(--mute)}
.tarjeta{border:1px solid var(--linea);border-radius:14px;background:var(--panel);
 padding:20px 22px;transition:.2s}
.tarjeta:hover{border-color:#2B3B52}
.tarjeta .alto{display:flex;flex-wrap:wrap;align-items:baseline;gap:10px;margin-bottom:3px}
.tarjeta .emp{font-size:17px;font-weight:700;letter-spacing:-.015em}
.tarjeta .per{font-family:PlexMono,monospace;font-size:11px;color:var(--mute);
 letter-spacing:.07em;border:1px solid var(--linea);border-radius:20px;padding:3px 10px}
.tarjeta .cargo{font-family:PlexMono,monospace;font-size:11.5px;letter-spacing:.09em;
 text-transform:uppercase;color:var(--front);margin-bottom:10px}
.tarjeta p{color:var(--mute);font-size:15px;max-width:64ch}
.tarjeta ul{list-style:none;margin:14px 0 0;display:grid;gap:9px}
.tarjeta li{color:var(--mute);font-size:14.5px;padding-left:20px;position:relative;max-width:64ch}
.tarjeta li::before{content:"";position:absolute;left:0;top:.7em;width:8px;height:1.5px;
 background:var(--front)}
.tarjeta .pie{font-size:13px;opacity:.75;margin-top:13px;padding-top:11px;
 border-top:1px solid var(--linea)}

/* ── Proyecto ───────────────────────────────────────────────────── */
.proy{border:1px solid var(--linea);border-radius:14px;background:var(--panel);
 padding:22px 24px;margin-bottom:26px}
.proy .nombre{font-size:clamp(19px,2.7vw,23px);font-weight:700;letter-spacing:-.02em}
.proy .linea{font-family:PlexMono,monospace;font-size:11.5px;letter-spacing:.08em;
 text-transform:uppercase;color:var(--externo);margin-top:5px}
.proy>p{color:var(--mute);max-width:66ch;margin:13px 0 0;font-size:15px}
.proy .stack{font-family:PlexMono,monospace;font-size:11.5px;color:var(--mute);
 margin-top:15px;padding-top:14px;border-top:1px solid var(--linea);line-height:1.8}

/* ── Contacto ───────────────────────────────────────────────────── */
.redes{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;
 max-width:720px}
.red{display:flex;align-items:center;gap:15px;border:1px solid var(--linea);border-radius:14px;
 background:var(--panel);padding:18px 20px;transition:.2s;color:var(--papel)}
.red:hover{border-color:currentColor;transform:translateY(-2px);text-decoration:none}
.red .caja{width:42px;height:42px;border-radius:11px;flex:none;display:grid;place-items:center}
.red svg{width:20px;height:20px;stroke-width:1.7;stroke-linecap:round;
 stroke-linejoin:round;display:block}
.red .txt{display:flex;flex-direction:column;gap:3px;min-width:0}
.red .etq{font-size:15px;font-weight:600;letter-spacing:-.01em;display:block}
.red .val{font-family:PlexMono,monospace;font-size:11.5px;color:var(--mute);
 display:block;word-break:break-all;line-height:1.45}

/* ── Perfil ─────────────────────────────────────────────────────── */
.perfil{display:flex;gap:26px;align-items:flex-start}
.retrato{width:104px;height:104px;border-radius:50%;flex:none;overflow:hidden;
 border:1px solid var(--linea);background:var(--panel);display:grid;place-items:center}
.retrato img{width:100%;height:100%;object-fit:cover;display:block}
.retrato span{font-family:PlexMono,monospace;font-size:30px;color:var(--front);
 letter-spacing:.04em}
.perfil h1{margin:2px 0 4px;max-width:none;font-size:clamp(26px,4vw,36px)}
.perfil .rol{font-family:PlexMono,monospace;font-size:12.5px;letter-spacing:.1em;
 text-transform:uppercase;color:var(--front);margin-bottom:14px}
.perfil .lugar{font-family:PlexMono,monospace;font-size:11.5px;letter-spacing:.08em;
 text-transform:uppercase;color:var(--mute);margin-top:12px}

/* ── Secciones ──────────────────────────────────────────────────── */
h2.sec{font-size:clamp(20px,2.9vw,26px);font-weight:700;letter-spacing:-.022em;
 margin:0 0 22px}
.panel>.col>p{color:var(--mute);max-width:62ch}

.proy .nombre{font-size:clamp(19px,2.7vw,24px);font-weight:700;letter-spacing:-.02em}
.proy .linea{font-family:PlexMono,monospace;font-size:11.5px;letter-spacing:.08em;
 text-transform:uppercase;color:var(--externo);margin-top:5px}
.proy>p{color:var(--mute);max-width:66ch;margin:14px 0 0}
.proy .stack{font-family:PlexMono,monospace;font-size:11.5px;color:var(--mute);
 margin-top:14px;padding-top:13px;border-top:1px solid var(--linea);line-height:1.8}
@media(max-width:620px){.redes{grid-template-columns:1fr}.perfil{gap:18px}.retrato{width:76px;height:76px}
 .retrato span{font-size:22px}}
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

// ── Pestañas ────────────────────────────────────────────────────────
function pestana(id, empujar) {
  document.querySelectorAll('.tab').forEach(t =>
    t.setAttribute('aria-selected', t.dataset.p === id));
  document.querySelectorAll('.panel').forEach(pn => {
    const activo = pn.id === 'pan-' + id;
    pn.hidden = !activo;
    if (activo) { pn.style.animation = 'none'; void pn.offsetWidth; pn.style.animation = ''; }
  });
  if (id !== 'proyecto') parar(); else ir(actual);
  if (empujar) history.replaceState(null, '', '#' + id);
}

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
    if (document.getElementById('pan-proyecto').hidden) return;
    if (document.activeElement && document.activeElement.classList.contains('tab')) return;
    if (e.key === 'ArrowRight') ir(actual + 1);
    if (e.key === 'ArrowLeft') ir(actual - 1);
  });
  document.querySelectorAll('.tab').forEach(t => {
    t.onclick = () => pestana(t.dataset.p, true);
    t.onkeydown = e => {
      const ts = [...document.querySelectorAll('.tab')], i = ts.indexOf(t);
      if (e.key === 'ArrowRight') { ts[(i + 1) % ts.length].focus(); ts[(i + 1) % ts.length].click(); }
      if (e.key === 'ArrowLeft') { ts[(i - 1 + ts.length) % ts.length].focus();
                                   ts[(i - 1 + ts.length) % ts.length].click(); }
    };
  });
  ir(0);
  const h = location.hash.slice(1);
  pestana(['experiencia', 'proyecto', 'contacto'].includes(h) ? h : 'experiencia', false);
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
    leyenda = "".join(f'<span><i style="background:{v["color"]}"></i>{v["etq"]}</span>'
                      for v in CAPAS.values())
    js = JS.replace("__CAPAS__", json.dumps(CAPAS, ensure_ascii=False)) \
           .replace("__PASOS__", json.dumps(PASOS, ensure_ascii=False))
    exp = ""
    for e in EXPERIENCIA:
        logros = "".join(f"<li>{x}</li>" for x in e.get("logros", []))
        exp += (f'<article><div class="meta"><div class="emp">{e["empresa"]}</div>'
                f'<div class="per">{e["periodo"]}</div></div><div>'
                f'<div class="cargo">{e["cargo"]}</div><p>{e["texto"]}</p>'
                + (f"<ul>{logros}</ul>" if logros else "")
                + (f'<p class="pie">{e["nota"]}</p>' if e.get("nota") else "")
                + "</div></article>")

    foto = retrato_archivo()
    retrato = (f'<img src="{foto}" alt="{PERFIL["nombre"]}" width="104" height="104">'
               if foto
               else f'<span>{"".join(w[0] for w in PERFIL["nombre"].split())}</span>')

    exp = ""
    for e in EXPERIENCIA:
        logros = "".join(f"<li>{x}</li>" for x in e.get("logros", []))
        exp += (f'<article><div class="tarjeta">'
                f'<div class="alto"><span class="emp">{e["empresa"]}</span>'
                f'<span class="per">{e["periodo"]}</span></div>'
                f'<div class="cargo">{e["cargo"]}</div><p>{e["texto"]}</p>'
                + (f"<ul>{logros}</ul>" if logros else "")
                + (f'<p class="pie">{e["nota"]}</p>' if e.get("nota") else "")
                + "</div></article>")

    redes = ""
    for r in REDES:
        c = CAPAS[r["capa"]]["color"]
        tipo, cuerpo = ICO[r["ico"]]
        pinta = f'fill="{c}"' if tipo == "relleno" else f'fill="none" stroke="{c}"'
        redes += (f'<a class="red" href="{r["href"]}" rel="me" style="--c:{c}">'
                  f'<span class="caja" style="background:{c}1C">'
                  f'<svg viewBox="0 0 24 24" {pinta}>{cuerpo}</svg></span>'
                  f'<span class="txt"><span class="etq">{r["etq"]}</span>'
                  f'<span class="val">{r["val"]}</span></span></a>')

    foto = retrato_archivo()
    retrato = (f'<img src="{foto}" alt="{PERFIL["nombre"]}" width="104" height="104">'
               if foto
               else f'<span>{"".join(w[0] for w in PERFIL["nombre"].split())}</span>')

    return f"""<!doctype html>
<html lang="es"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{PERFIL['nombre']} · Analytics Engineer</title>
<meta name="description" content="Analytics Engineer. Procesos de datos en producción:
 infraestructura, costo operacional y confiabilidad de los flujos.">
<meta name="color-scheme" content="dark">
<meta property="og:title" content="{PERFIL['nombre']} · Analytics Engineer">
<meta property="og:description" content="Analytics Engineer. Procesos de datos en producción.">
<style>{fuentes()}{CSS}</style>
</head><body>

<nav><div class="col">
  <span class="yo">{PERFIL['nombre']}</span>
  <span class="liga">ANALYTICS ENGINEER · DATA ENGINEER</span>
</div></nav>

<header><div class="col">
  <div class="perfil">
    <div class="retrato">{retrato}</div>
    <div>
      <h1>{PERFIL['nombre']}</h1>
      <div class="rol">{PERFIL['rol']}</div>
      <p>{PERFIL['texto']}</p>
      <div class="lugar">{PERFIL['lugar']}</div>
    </div>
  </div>
</div></header>

<div class="col"><div class="tabs" role="tablist" aria-label="Secciones">
  <button class="tab" type="button" role="tab" data-p="experiencia"
          id="tab-experiencia" aria-controls="pan-experiencia" aria-selected="true">
    <i>01</i>Mi experiencia</button>
  <button class="tab" type="button" role="tab" data-p="proyecto"
          id="tab-proyecto" aria-controls="pan-proyecto" aria-selected="false">
    <i>02</i>Mi proyecto</button>
  <button class="tab" type="button" role="tab" data-p="contacto"
          id="tab-contacto" aria-controls="pan-contacto" aria-selected="false">
    <i>03</i>Contacto</button>
</div></div>

<div class="panel" id="pan-experiencia" role="tabpanel" aria-labelledby="tab-experiencia">
  <div class="col">
    <h2 class="sec">Experiencia</h2>
    <div class="linea-t">{exp}</div>
  </div>
</div>

<div class="panel" id="pan-proyecto" role="tabpanel" aria-labelledby="tab-proyecto" hidden>
  <div class="col">
    <h2 class="sec">{PROYECTO['nombre']}</h2>
    <div class="proy">
      <div class="nombre">{PROYECTO['nombre']}</div>
      <div class="linea">{PROYECTO['linea']}</div>
      <p>{PROYECTO['texto']}</p>
      <div class="stack">{PROYECTO['stack']}</div>
    </div>

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

    <p class="pista">Selección directa por número; desplazamiento con <kbd>←</kbd>
     <kbd>→</kbd></p>
  </div>
</div>

<div class="panel" id="pan-contacto" role="tabpanel" aria-labelledby="tab-contacto" hidden>
  <div class="col">
    <h2 class="sec">Contacto</h2>
    <p style="margin-bottom:26px">Disponible para cargos de Analytics Engineer o Data Engineer,
    en modalidad remota o híbrida.</p>
    <div class="redes">{redes}</div>
  </div>
</div>

<footer><div class="col">HTML, CSS y JavaScript sin dependencias externas.</div></footer>
<script>{js}</script>
</body></html>"""


def main():
    ruta = os.path.join(AQUI, "index.html")
    io.open(ruta, "w", encoding="utf-8").write(pagina())
    foto = retrato_archivo()
    print(f"    index.html  {os.path.getsize(ruta) / 1024:.1f} KB  ·  {len(PASOS)} pasos"
          f"  ·  retrato: {foto or 'monograma (falta assets/foto.jpg)'}")


if __name__ == "__main__":
    main()
