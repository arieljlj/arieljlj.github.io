---
name: wikiforge
description: >
  Convierte cualquier colección de documentos en una wiki de conocimiento
  interconectada en Obsidian, siguiendo el patrón LLM Wiki de Karpathy.
  Ingesta transcripciones de YouTube, cursos, reuniones Meet/Zoom, informes,
  PDFs, artículos web, podcasts, hilos de Slack y notas sueltas — y los
  transforma en páginas markdown con wikilinks, frontmatter YAML e índice
  navegable. Activar siempre que el usuario mencione "wiki", "segundo cerebro",
  "base de conocimiento", "knowledge base", "obsidian", "ingestar", "organizar
  notas", "organizar transcripciones", "crear wiki", "LLM wiki", "wiki
  Karpathy", "wikiforge", o quiera estructurar cualquier corpus de documentos
  en un sistema de conocimiento. También activar cuando pida consultar,
  mantener, hacer lint, o ampliar una wiki existente, o conectar varias wikis
  entre sí. Si el usuario tiene documentos desordenados y quiere orden, esta
  es la skill.
---

# WikiForge para Antigravity

Transforma documentos en bruto en wikis de conocimiento vivas.

La idea central es simple: en lugar de que Antigravity redescubra el conocimiento cada vez que le preguntas algo (como hace RAG tradicional), aquí Antigravity lee las fuentes una vez, extrae el conocimiento y lo organiza en páginas markdown interconectadas que se enriquecen con cada fuente nueva. El conocimiento se compila y se acumula — no se re-deriva en cada consulta.

Obsidian es el IDE. Antigravity es el programador. La wiki es el código.

---

## Cómo funciona — Las 5 operaciones en Antigravity

WikiForge consta de 5 operaciones optimizadas para el entorno de Antigravity. Cada una se puede invocar individualmente, pero el flujo típico es: SETUP → INGEST (batch) → QUERY → LINT → repetir.

### SETUP — Crear un vault nuevo

Antes de crear nada, entiende el proyecto. Si el usuario da material sin explicar nada, infiere todo del contenido utilizando tus herramientas de lectura — es mejor actuar de manera inteligente que abrumar con preguntas. Si hay ambigüedad real, pregunta solo lo imprescindible:

- **Dominio** (¿de qué trata?)
- **Tipos de fuente** (¿qué material va a entrar?)
- **Objetivo** (¿consulta personal, agentes, contenido, estudio?)

Con eso, decide las categorías de la wiki (subcarpetas bajo `wiki/`) y los tipos de entidad a extraer. Después, ejecuta los siguientes pasos usando las herramientas de Antigravity:

1. **Crear la estructura de carpetas**: Usa `write_to_file` para inicializar el directorio.
2. **Mover las fuentes**: Si las fuentes están dispersas, organízalas en una carpeta `raw/` dentro de tu espacio de trabajo.
3. **Generar `CLAUDE.md`**: Crea este archivo en la raíz del vault usando `write_to_file`. Debe detallar cómo opera Antigravity sobre este vault específico (patrones, herramientas sugeridas, etc.).
4. **Inicializar índices**: Crea `wiki/index.md` y `wiki/log.md` vacíos o con la plantilla inicial.

#### Detectar estructura interna de las fuentes

Antes de ingestar, analiza cómo están organizadas las fuentes usando `list_dir` o `view_file`. Los corpus no son todos iguales. Detectar la estructura es clave para decidir la granularidad de las páginas bajo `fuentes/` y cómo vincular los archivos originales:

| Estructura del corpus | Granularidad de `fuentes/` | Vinculación a raw |
|---|---|---|
| Curso con módulos y lecciones | Una página fuente por módulo, con wikilinks a cada lección individual | `## Transcripciones del módulo` con [[nombre-leccion]] |
| Reuniones periódicas de un equipo | Una página fuente por reunión (o por sprint/semana) | `## Actas originales` con [[nombre-acta]] |
| Canal de Slack / Discord | Una página fuente por hilo relevante o tema recurrente | `## Hilos originales` con [[nombre-hilo]] |
| Colección de artículos / PDFs | Una página fuente por documento | `## Documento original` con [[nombre-documento]] |
| Vídeos de YouTube sueltos | Una página fuente por vídeo | `## Transcripción original` con [[nombre-transcripcion]] |
| Notas sueltas del usuario | Agrupar por tema si hay un patrón, o una por nota | `## Notas originales` con [[nombre-nota]] |

La regla general: cada página en `fuentes/` debe incluir wikilinks a todos los archivos raw que cubre. Esto es lo que hace que aparezcan conectados en el grafo de Obsidian.

#### Arquitectura del vault

```
vault-nombre/
├── CLAUDE.md              ← Esquema: cómo opera Antigravity sobre este vault
├── raw/                   ← Fuentes originales — INMUTABLES
│   └── [estructura libre del usuario]
├── wiki/
│   ├── index.md           ← Catálogo maestro (enlace + resumen de cada página)
│   ├── log.md             ← Historial cronológico de operaciones
│   ├── hot.md             ← (opcional) Cache de contexto reciente
│   ├── fuentes/           ← Un resumen por cada fuente ingestada (SIEMPRE)
│   └── [categorias]/      ← Subcarpetas adaptadas al dominio
└── .obsidian/
```

La carpeta `fuentes/` es obligatoria. Las demás subcarpetas dependen del dominio. Algunos ejemplos:

- **Curso / educación**: `tecnicas/`, `conceptos/`, `herramientas/`, `ejemplos/`
- **Negocio / equipo**: `decisiones/`, `proyectos/`, `personas/`, `metricas/`
- **Investigación**: `hallazgos/`, `metodologias/`, `autores/`, `hipotesis/`

---

### INGEST — Procesar fuentes

Esta es la operación central. Por cada fuente:

1. **Leer la fuente**: Usa `view_file` para leer la fuente completa desde `raw/`.
2. **Clasificar el tipo** (transcripción, informe, artículo, reunión, notas...).
3. **Extraer entidades del dominio**: Conceptos, técnicas, herramientas, personas, decisiones, datos, ejemplos, relaciones causales.
4. **Crear o actualizar páginas wiki**:
   - Usa `write_to_file` para páginas nuevas.
   - Usa `replace_file_content` o `multi_replace_file_content` para actualizar páginas existentes ampliándolas con el nuevo contenido. **¡No dupliques páginas!**
   - Siempre crea una página en `fuentes/` con el resumen de la fuente.
   - Incluye en cada página `fuentes/` los wikilinks a cada archivo raw que cubre.
5. **Enlazar densamente con `[[wikilinks]]`**:
   - Mínimo 8 wikilinks por página, distribuidos a lo largo del texto (no solo al final).
   - Usa `[[nombre-pagina|Texto visible]]` cuando el nombre de la página difiera de la redacción natural.
6. **Actualizar** `wiki/index.md` con las nuevas entradas usando `replace_file_content`.
7. **Registrar en `wiki/log.md`** con el formato:
   ```markdown
   ## [YYYY-MM-DD] ingest | Nombre de la fuente
   - Páginas creadas: X
   - Páginas actualizadas: Y
   - Entidades extraídas: lista breve
   ```

#### Reglas según tipo de fuente

- **Transcripciones**: Limpia muletillas y repeticiones. Extrae la estructura lógica, no la temporal. Preserva ejemplos prácticos.
- **Reuniones**: Preserva quién dijo qué si es relevante. Extrae decisiones, acciones pendientes y contexto.
- **Informes / PDFs**: Respeta la estructura del documento. Extrae datos cuantitativos y conclusiones.
- **Artículos web**: Distingue hechos de opiniones. Registra autor, fecha y URL en el frontmatter.

#### Idioma

Todas las páginas de la wiki deben escribirse en el mismo idioma que las fuentes. Detecta el idioma al inicio y mantenlo estrictamente (títulos, secciones, cuerpo de texto).

> [!IMPORTANT]
> Cuando delegues tareas de ingesta a subagentes de Antigravity, debes especificar explícitamente el idioma objetivo en sus instrucciones, ya que tienden a usar inglés por defecto.

#### Formato estándar de página wiki

Usa exactamente esta plantilla para toda nueva página. Los 5 campos de frontmatter son obligatorios:

```markdown
---
tags: [categoria, subcategoria]
tipo: tecnica | concepto | persona | herramienta | decision | fuente
fuentes: ["nombre-fuente-original"]
fecha_creacion: YYYY-MM-DD
fecha_actualizacion: YYYY-MM-DD
---

# Título

Descripción clara y concisa en 2-3 párrafos. Incluir [[wikilinks]] a las páginas relacionadas directamente en el texto.

## Detalle

Desarrollo del contenido con [[wikilinks]] entretejidos en cada párrafo donde se mencionen entidades con página propia.

## Ejemplo / Evidencia

> Cita o ejemplo concreto extraído de las fuentes.

## Relaciones

- Véase también: [[pagina-relacionada]]
- Depende de: [[concepto-previo]]
- Se conecta con: [[otra-pagina]]

## Fuentes

- [[fuente-original]]
```

#### Batch ingest con Subagentes de Antigravity

Cuando haya un gran volumen de fuentes a ingestar:
1. Enumera todos los archivos en `raw/` usando `list_dir`.
2. Planifica el orden conceptual óptimo (lo básico primero).
3. **Paralelización**: Puedes delegar la ingesta a subagentes paralelos usando la herramienta `invoke_subagent` con la configuración `self`.
4. El prompt del subagente debe incluir:
   - **Idioma obligatorio**.
   - **Bloque de frontmatter estándar**.
   - **Listado de páginas existentes** (para evitar enlaces rotos o duplicados).
   - **Mínimo de 8 wikilinks**.

---

### QUERY — Consultar la wiki

Para responder preguntas del usuario basándote en la wiki:
1. Usa `grep_search` para buscar palabras clave o conceptos dentro del directorio `wiki/`.
2. Lee las páginas más relevantes usando `view_file`.
3. Sintetiza la respuesta citando las páginas correspondientes como wikilinks.
4. Si la consulta revela un "vacío" de información (gap) en la wiki, sugiere al usuario investigar o ingestar fuentes adicionales.

---

### LINT — Mantenimiento Automatizado

El mantenimiento de la wiki debe realizarse obligatoriamente después de cada batch ingest. En Antigravity, puedes automatizar esto ejecutando comandos o creando scripts de diagnóstico en PowerShell.

#### Checklist obligatoria post-batch

Ejecuta estos chequeos y reporta los resultados con métricas exactas:

1. **Frontmatter**: 100% de las páginas deben tener los 5 campos exactos. Puedes usar un script de PowerShell rápido para validarlo:
   ```powershell
   Get-ChildItem -Path wiki -Filter *.md -Recurse | ForEach-Object {
       $content = Get-Content $_.FullName -Raw
       if ($content -notmatch 'tags:' -or $content -notmatch 'tipo:' -or $content -notmatch 'fuentes:' -or $content -notmatch 'fecha_creacion:' -or $content -notmatch 'fecha_actualizacion:') {
           Write-Output "Falla frontmatter: $($_.Name)"
       }
   }
   ```
2. **Idioma**: Verifica que todo esté escrito en el idioma correcto.
3. **Enlaces Fantasmas (Rotos)**: Busca wikilinks `[[pagina]]` que no existan como archivos markdown reales.
4. **Densidad de enlaces**: Asegúrate de que cada página temática tenga al menos 8 wikilinks.
5. **Huérfanas**: Encuentra páginas que no tengan ningún enlace entrante (puedes buscar su nombre en el resto del vault usando `grep_search`).
6. **Archivos raw vinculados**: Asegúrate de que cada archivo de `raw/` esté citado en al menos una página de `fuentes/`.

Registra los resultados y correcciones del LINT en `wiki/log.md`.

---

## Convenciones de Estilo

- **Nombres de archivo**: Usar siempre `kebab-case` sin tildes ni caracteres especiales (ej. `cadena-de-pensamiento.md`).
- **YAML Frontmatter**: Usar exactamente los 5 campos predefinidos.
- **Brevedad**: Mantener las páginas entre 200 y 500 palabras. Si crece demasiado, divídela y enlázala.
- **Evidencia**: Incluir al menos una cita o dato factual por página.