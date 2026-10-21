# NetworkedAsociados · sitio web

*Trabajando en ti para crecer juntos.*

El sitio se genera solo a partir de los archivos de la carpeta `data/` y `contenido/`.
Cada vez que guardas un cambio en GitHub, se publica automáticamente en 1 o 2 minutos.
No necesitas instalar nada en tu computador.

## Qué hay en cada carpeta

| Carpeta / archivo | Para qué sirve |
|---|---|
| `data/config.json` | Tus redes, canales y videos destacados. |
| `data/empresas.json` | Brokers, fondeos y alertas de la Zona de peligro. |
| `data/apps.json` | Tus aplicaciones y proyectos. |
| `data/paginas.json` | Datos de cada artículo (sección, categoría, descripción para Google). |
| `data/redirecciones.json` | Direcciones viejas que llevan a la nueva ubicación. |
| `articulos.py` | **El texto de cada página interna** (análisis, libro, bot, sobre mí…), organizado en capítulos y bloques. |
| `bloques.py` | Convierte esos bloques en el diseño. No necesitas tocarlo. |
| `contenido/` | El HTML original de Blogger de cada página (respaldo y fuente para artículos nuevos). |
| `static/` | Logo, estilos (`site.css`) y funciones (`site.js`). |
| `respaldo_papelera/` | Copia de las 4 entradas que estaban en la papelera de Blogger. No se publican. |
| `build.py` | El programa que arma el sitio. No necesitas tocarlo. |

## Cómo agregar una empresa nueva

1. En GitHub, abre `data/empresas.json` y toca el lápiz (Editar).
2. Copia el bloque de una empresa parecida y cambia los datos:
   - `"zona"`: `"catalogo"` para brokers y fondeos, `"peligro"` para la Zona de peligro.
   - `"tipo"`: `"broker"` o `"fondeo"`.
   - `"calificacion"`: un número del 1 al 5, o `null` si no tiene.
   - `"riesgo"`: `"bajo"`, `"medio"` o `"alto"`.
   - `"analisis"`: la dirección de su artículo, por ejemplo `/2026/11/nueva-empresa.html`.
3. Revisa que cada bloque termine en `}` y que haya una coma entre bloques.
4. Toca **Commit changes**. En un par de minutos aparece en Brokers, Fondeo o Zona de peligro.

## Cómo cambiar el texto de una página

1. Abre `articulos.py` y busca la dirección de la página, por ejemplo `/2026/01/deriv-45.html`.
2. Cada página tiene una portada (`hero`) y capítulos (`cap`). Dentro de cada capítulo hay bloques:
   - `P('texto')` párrafo · `Grande('texto')` frase destacada
   - `Cifras(('2006', 'Año de fundación'), ...)` números grandes
   - `Lista('punto 1', 'punto 2')` lista con chulos · `ProsContras([...], [...])`
   - `Tarjetas(('🧠', 'Título', 'Texto'), ...)` · `Pasos(('Título', 'Texto'), ...)` · `Ficha(('Dato', 'Valor'), ...)`
   - `Nota('ok'|'warn'|'bad'|'info', 'Título', 'Texto')` · `Cita('frase')`
   - `Video('ID_DE_YOUTUBE', 'Título')` · `Botones(('Texto', 'enlace', 'b-acc', 'afiliado'))` · `Llamado('Título', 'Texto', botón...)`
3. Cambia solo el texto entre comillas. Si un texto lleva comillas simples (') dentro, escríbelo como \'.
4. Guarda. Si algo queda mal escrito, la pestaña **Actions** de GitHub mostrará una X roja y el sitio anterior sigue publicado.

## Cómo publicar un análisis o artículo nuevo

1. Crea el archivo en `contenido/` con la dirección que quieras, por ejemplo `contenido/2026/11/nueva-empresa.html`, y pega ahí el HTML del artículo (el mismo que pegabas en Blogger).
2. Agrega una línea en `data/paginas_raw.json` con el título y las fechas:
   `{"ruta": "/2026/11/nueva-empresa.html", "titulo": "Nueva Empresa", "tipo": "post", "publicado": "2026-11-05", "actualizado": "2026-11-05"}`
3. Agrega una línea en `data/paginas.json` con la sección, la categoría y la descripción para Google.
   Secciones: `brokers`, `fondeo`, `peligro`, `contenido`, `libro`, `apps`.
   Si el artículo es de una empresa, agrega `"empresa": "id-de-la-empresa"` para que muestre su ficha arriba.
4. Guarda los cambios. El sitio se actualiza solo: el HTML se convierte automáticamente al diseño nuevo, sin los colores viejos de Blogger.
5. (Opcional) Si quieres la versión con capítulos, cifras y tarjetas, agrégala en `articulos.py` copiando la estructura de una página parecida, o pídemela.

## Si un cambio rompe el sitio

En la pestaña **Actions** de GitHub verás una X roja. El error casi siempre es una coma o una llave en un `.json`.
Puedes volver a la versión anterior desde el historial del archivo (botón **History**).

## Probar en tu computador (opcional)

Necesitas Python 3.12 o superior. En la carpeta del proyecto:

```
python build.py
python -m http.server 8000 --directory _site
```

Luego abre `http://localhost:8000`.
