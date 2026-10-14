# TaskFlow — Proyecto de test para comparativa Fable 5 vs Opus 4.8

## Harness de equipo

Este repositorio trae configurado el harness del equipo, el plugin `equipo` del marketplace [harness-equipo](https://github.com/JoaquinRuiz/harness-equipo), que convierte las reglas de la casa de TaskFlow en una skill con la receta para añadir endpoints y en unos hooks que, mientras trabaja el agente, protegen el `.env`, impiden añadir dependencias sin aprobación, avisan cuando un cambio rompe las capas o las dependencias y no le dejan dar la tarea por cerrada con la suite en rojo. La configuración son dos ficheros versionados: `.claude/settings.json`, que declara el marketplace y activa el plugin para este proyecto, y `.harness-equipo`, el marcador sin el cual los hooks no hacen nada aunque el plugin esté instalado.

Al abrir el proyecto con Claude Code por primera vez te pedirá que confíes en la carpeta y, al aceptarlo, añadirá por su cuenta el marketplace `harness-equipo` y marcará el plugin `equipo` como activado para este proyecto, pero no lo instala: hasta que lo instales, el panel `/plugin` lo muestra con un error de caché y los hooks no actúan, así que hay que instalarlo una vez con `claude plugin install equipo@harness-equipo --scope project` dentro del repositorio, y a partir de ahí queda activo solo en este proyecto (comprobado con Claude Code 2.1.294). Si no quieres usarlo, basta con no instalarlo, o desactivarlo solo para ti con `claude plugin disable equipo@harness-equipo --scope local`, que lo apunta en `.claude/settings.local.json` (ignorado por git) sin tocar la configuración del equipo; si lo que se quiere es apagar los hooks para todos, se borra el fichero `.harness-equipo` en un commit, y la skill sigue disponible para quien quiera usarla.

API REST de gestión de tareas construida con Flask + SQLAlchemy (sync) + Marshmallow.
**Diseñada a propósito con queries de base de datos mezcladas directamente en las vistas.**

## Datos del proyecto

- **22 archivos Python**, ~1.180 líneas de código
- **57 tests** — todos pasan
- **4 modelos** con relaciones (User, Project, Task, Tag + M2M)
- **4 módulos de vistas** con queries SQLAlchemy inline (el anti-patrón a refactorizar)
- **4 archivos de tests** con cobertura completa de todos los endpoints
- **Stack:** Flask 3.1, Flask-SQLAlchemy, Marshmallow, pytest, SQLite

## Setup rápido

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest -v   # → 57 passed
```

## Estructura

```
taskflow/
├── requirements.txt
├── app/
│   ├── __init__.py          ← App factory
│   ├── config.py            ← Configuración
│   ├── extensions.py        ← db, ma
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          ← User model
│   │   ├── project.py       ← Project model (FK → User)
│   │   └── task.py          ← Task model (FK → Project, User) + Tag + M2M
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py          ← Marshmallow schema
│   │   ├── project.py
│   │   └── task.py
│   └── views/
│       ├── __init__.py
│       ├── users.py         ← ⚠️ Queries DB inline
│       ├── projects.py      ← ⚠️ Queries DB inline
│       ├── tasks.py         ← ⚠️ Queries DB inline (el más complejo)
│       └── tags.py          ← ⚠️ Queries DB inline
└── tests/
    ├── __init__.py
    ├── conftest.py          ← Fixtures
    ├── test_users.py        ← 12 tests
    ├── test_projects.py     ← 11 tests
    ├── test_tasks.py        ← 22 tests
    └── test_tags.py         ← 12 tests
```

---

## PROTOCOLO DE COMPARATIVA

### Paso 1: Preparar dos copias idénticas

```bash
cp -r taskflow fable5-test
cp -r taskflow opus48-test
```

### Paso 2: Abrir Claude Code con cada modelo

```bash
# Terminal 1
cd fable5-test
claude --model claude-fable-5

# Terminal 2
cd opus48-test
claude --model claude-opus-4-8
```

### Paso 3: Dar el MISMO prompt a ambos

---

## EL PROMPT (copia y pega exacto en ambos)

```
Este proyecto es una REST API de gestión de tareas construida con Flask. Tiene un problema de diseño: todas las queries de SQLAlchemy están mezcladas directamente dentro de las vistas (views). Necesito que hagas una refactorización completa para implementar el patrón Repository.

Estos son los cambios que necesito:

1. CAPA DE REPOSITORIOS: Crea un directorio app/repositories/ con un archivo por cada entidad:
   - user_repository.py
   - project_repository.py
   - task_repository.py
   - tag_repository.py
   Cada repositorio debe encapsular TODAS las operaciones de base de datos de esa entidad (queries, inserts, updates, deletes). Usa métodos estáticos o de clase.

2. VISTAS LIMPIAS: Refactoriza las 4 vistas (users.py, projects.py, tasks.py, tags.py) para que NO importen ni usen db.session directamente. Las vistas solo deben:
   - Recibir el request
   - Validar los datos de entrada
   - Llamar al repositorio correspondiente
   - Serializar y devolver la respuesta
   Las vistas NO deben contener ninguna query de SQLAlchemy ni referencia a db.session.

3. TYPE HINTS: Añade type hints completos a todos los métodos de los repositorios:
   - Parámetros de entrada tipados
   - Return types explícitos (incluyendo Optional donde corresponda)
   - Usa los tipos de los modelos SQLAlchemy, no Any

4. TESTS: Los 57 tests existentes DEBEN seguir pasando sin modificaciones. No cambies los tests. Si tu refactorización es correcta, los tests pasan tal cual porque la API externa no cambia.

5. TESTS DE REPOSITORIOS: Añade un nuevo archivo tests/test_repositories.py con tests unitarios que cubran los métodos principales de cada repositorio. Estos tests deben interactuar directamente con los repositorios (no via HTTP).

REGLAS:
- No cambies las URLs ni el comportamiento de la API
- No cambies el framework (sigue siendo Flask)
- No cambies los modelos ni los schemas
- No modifiques los tests existentes
- Los 57 tests originales deben pasar EXACTAMENTE igual después de la refactorización

Empieza analizando la estructura del proyecto y luego haz la refactorización.
```

---

## Paso 4: Medir los resultados

### 4.1 — ¿Pasan los 57 tests originales?

```bash
pytest tests/test_users.py tests/test_projects.py tests/test_tasks.py tests/test_tags.py -v
```

**Resultado:** X/57 passed — ESTE ES EL DATO PRINCIPAL

### 4.2 — ¿Se crearon los repositorios?

```bash
ls app/repositories/
# Debe existir: user_repository.py, project_repository.py, task_repository.py, tag_repository.py
```

### 4.3 — ¿Las vistas ya no usan db.session?

```bash
# Si es 0, la refactorización fue completa
grep -n "db.session" app/views/*.py | wc -l
```

**El número debe ser 0.** Si hay alguna referencia a db.session en las vistas, la refactorización está incompleta.

### 4.4 — ¿Tienen type hints los repositorios?

```bash
# Busca funciones sin return type
grep -n "def " app/repositories/*.py | grep -v "\->" | wc -l
```

**El número debe ser 0** (todas las funciones deben tener -> tipo).

### 4.5 — ¿Se crearon tests de repositorios?

```bash
pytest tests/test_repositories.py -v
# Cuenta cuántos tests nuevos creó
```

### 4.6 — Tokens y tiempo

Anota del output de Claude Code:
- Tokens de input
- Tokens de output
- Tokens de thinking/reasoning
- Tiempo total de la sesión

---

## TABLA DE RESULTADOS (para mostrar en vídeo)

| Métrica                                    | Fable 5 | Opus 4.8 |
|--------------------------------------------|---------|----------|
| Tests originales que pasan (de 57)         |         |          |
| ¿Creó los 4 repositorios?                  | Sí/No   | Sí/No    |
| Refs a db.session en vistas (debe ser 0)   |         |          |
| Funciones sin type hints (debe ser 0)      |         |          |
| Tests de repositorio nuevos creados        |         |          |
| Tests de repositorio que pasan             |         |          |
| Tokens de output consumidos                |         |          |
| Tiempo total                               |         |          |
| Coste estimado a precio de API             |         |          |

---

## POR QUÉ ESTA PRUEBA ES BUENA PARA EL VÍDEO

1. **Es visual:** Puedes mostrar un `grep "db.session" app/views/*.py` antes y después. El antes tiene decenas de líneas. El después debe tener 0.

2. **Es binaria:** O los 57 tests pasan o no. No hay subjetividad.

3. **Testea multi-archivo real:** El modelo tiene que crear 4+ archivos nuevos, modificar 4 archivos existentes, y mantener todo coherente.

4. **Testea comprensión del código:** No es copiar y pegar — tiene que entender las relaciones entre modelos, las queries con filtros, la M2M de tags, la lógica de negocio (no borrar un user que tiene proyectos), etc.

5. **Es rápida:** 5-10 minutos por modelo. Perfecta para grabar.

6. **Es real:** Esta refactorización es algo que cualquier equipo de desarrollo se plantea. Tu audiencia se va a identificar.
