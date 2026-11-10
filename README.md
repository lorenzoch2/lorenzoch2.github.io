# lorenzoch2.github.io

Un día de trabajo con una aplicación en producción, paso a paso, como diagrama recorrible:
<https://lorenzoch2.github.io/>

En cada paso se ve **qué hace la persona**, qué ocurre en el navegador y qué ocurre en la base de
datos o en el servicio externo que corresponda, con el dato viajando por las flechas.

## Se compone, no se edita

```
python componer-sitio.py
```

Los pasos viven en `PASOS`, dentro del script. Cada uno declara sus nodos con un **carril** y una
**columna** —no coordenadas— y las flechas entre ellos; el navegador dibuja el SVG a partir de
eso. Agregar un paso no obliga a recalcular nada a mano.

**Editar `index.html` no sirve**: la próxima composición lo reemplaza.

## Por qué un diagrama y no un texto

La versión anterior eran seis párrafos de ochenta palabras en gris sobre negro. Decía cosas
ciertas y no las leía nadie: no se entendía de qué iba antes de empezar a leer, que es justo lo
que una página tiene que resolver en cinco segundos.

Un diagrama se entiende antes de leerlo, y uno que se puede recorrer se entiende usándolo.

## Cómo está hecho

HTML, CSS y JavaScript a mano. El SVG lo dibuja el navegador; los puntos que viajan por las
flechas son `animateMotion`, que es nativo y no cuesta una librería. Las tipografías se sirven
desde el propio repositorio —64 KB— en vez de Google Fonts: carga antes y no le cuenta a nadie
quién visitó.

Sin framework, sin CDN, sin dependencias. El sitio entero pesa menos que una fotografía.

## Pendiente

- La versión en inglés. El generador ya separa contenido de estructura, así que es traducir
  `PASOS` y emitir una segunda página.
