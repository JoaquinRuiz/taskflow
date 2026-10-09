# TaskFlow

API REST de gestión de tareas: usuarios, proyectos, tareas y etiquetas.
Flask + Flask-SQLAlchemy + Marshmallow sobre SQLite. Si el README y el código no
coinciden, manda el código.

## Comandos
- Entorno: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Suite completa: `.venv/bin/python -m pytest -q`
- Un fichero: `.venv/bin/python -m pytest -q tests/test_tasks.py`
- Arrancar en local: `.venv/bin/flask --app app run`

## Mapa
- `app/__init__.py`: app factory `create_app` y registro de blueprints.
- `app/config.py`: configuración; lee variables de entorno con valor por defecto.
- `app/extensions.py`: `db` (SQLAlchemy) y `ma` (Marshmallow).
- `app/models/`: modelos SQLAlchemy y sus constantes (estados, prioridades).
- `app/repositories/`: un `<Entidad>Repository` por entidad, métodos estáticos con type
  hints. Es la única capa que toca la base de datos.
- `app/schemas/`: esquemas Marshmallow.
- `app/views/`: un blueprint por recurso (`/api/<recurso>`), registrados en la lista
  `blueprints` de `app/views/__init__.py`.
- `tests/`: `conftest.py` (fixtures), `test_<recurso>.py` (API vía `client`) y
  `test_repositories.py` (repositorios sin HTTP).

## Reglas de la casa
Cada regla dice cómo se comprueba. Se verifican en revisión y con hooks.

- **R1 · Datos solo por el repositorio.** Fuera de `app/repositories/`, `app/models/` y
  `app/extensions.py`, ningún código de la aplicación importa `db`, `sqlalchemy`,
  `flask_sqlalchemy` o `sqlite3`, ni usa `.session`, `.query` o `.execute`. Las vistas y
  cualquier capa intermedia llaman a métodos del repositorio. Leer constantes de un
  modelo sí está permitido.
- **R2 · Todo endpoint nuevo con tests.** Cada ruta nueva tiene al menos un test en
  `tests/` que la llama con su método HTTP: el caso feliz y cada error que devuelve.
- **R3 · Formato de error.** Un error al cliente es siempre `{"error": "<mensaje>"}`, con
  una sola clave, y código 4xx: 400 datos inválidos, 404 no existe, 409 conflicto. Nada de
  `abort()` ni de otros formatos.
- **R4 · Ninguna dependencia nueva.** `requirements.txt` no se toca y no se crean otros
  ficheros de dependencias. Solo se importa la biblioteca estándar, el código del proyecto
  y lo que ya instala `requirements.txt`. Si algo parece necesitar un paquete, resuélvelo
  con la biblioteca estándar o deja la propuesta en el resumen para que el equipo la apruebe.
- **R5 · El `.env` no se lee ni se edita.** Es de cada persona y guarda secretos. Una
  variable nueva se lee en `app/config.py` con `os.environ.get("NOMBRE", <defecto>)` y se
  documenta en `.env.example`, que sí se edita.
- **R6 · Suite en verde antes de cerrar.** La tarea no está terminada hasta que
  `.venv/bin/python -m pytest -q` pasa entero. Los tests que ya existen no se borran, no se
  saltan (`skip`) ni se marcan como `xfail`.
