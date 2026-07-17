# Progressive Context Router

Skill pública y portable para configurar repositorios con **contexto progresivo** e **instrucciones de enrutamiento** para agentes de programación.

La skill convierte documentación e instrucciones dispersas en un sistema con dos capas:

1. Un punto de entrada pequeño y estable, normalmente `AGENTS.md`.
2. Un router en `docs/agent/index.md` que dirige cada tarea hacia el contexto mínimo necesario.

No cambia la lógica del producto. Audita la estructura del repositorio, conserva las instrucciones existentes, documenta únicamente hechos verificados y valida enlaces, rutas, duplicaciones y presupuesto aproximado de contexto.

## Estructura

```text
progressive-context-router-skill/
├── README.md
├── LICENSE
└── skills/
    └── progressive-context-router/
        ├── SKILL.md
        ├── assets/
        ├── evals/
        ├── references/
        └── scripts/
```

El `SKILL.md` está dentro de `skills/progressive-context-router/` para que una instalación desde un repositorio Git conserve también `assets/`, `references/`, `scripts/` y `evals/`.

## Instalación local

Desde el directorio que contiene esta carpeta:

```bash
npx skills add ./progressive-context-router-skill \
  --skill progressive-context-router
```

Para instalarla globalmente en un agente concreto:

```bash
npx skills add ./progressive-context-router-skill \
  --skill progressive-context-router \
  --agent codex \
  --global
```

Sustituye `codex` por el identificador de tu cliente cuando corresponda.

## Publicación en GitHub

Sube el contenido de `progressive-context-router-skill/` a un repositorio. Después podrá instalarse con:

```bash
npx skills add propietario/repositorio \
  --skill progressive-context-router
```

## Prompts de uso

### Configuración inicial

```text
Configura este repositorio con progressive-context-router.
Crea un punto de entrada pequeño para agentes, un router de contexto y
solo la documentación bajo demanda que puedas verificar en el código.
No modifiques la lógica del producto.
```

### Refactor de instrucciones existentes

```text
Usa progressive-context-router para refactorizar AGENTS.md y CLAUDE.md.
Conserva todas las restricciones válidas, elimina duplicaciones y mueve
los detalles de cada subsistema a documentación cargada bajo demanda.
```

### Auditoría sin cambios

```text
Audita la configuración de contexto para agentes con
progressive-context-router. No escribas archivos; entrega hallazgos,
rutas rotas, instrucciones siempre cargadas, duplicaciones y una propuesta.
```

### Actualización por drift

```text
Actualiza el router de contexto después de los cambios recientes del
repositorio. Conserva las notas humanas y modifica solamente lo que haya
quedado obsoleto.
```

## Scripts incluidos

Los scripts usan únicamente la biblioteca estándar de Python y no ejecutan código del repositorio:

- `repo_inventory.py`: inventario determinista y de solo lectura.
- `validate_context_setup.py`: validación de entrypoints, enlaces, rutas, duplicaciones y casos de routing.
- `context_budget.py`: medición de líneas, caracteres y tokens estimados para contexto siempre cargado y documentación bajo demanda.

Ejemplo, ejecutado desde el directorio de la skill:

```bash
python3 scripts/repo_inventory.py --root /ruta/al/repo --markdown
python3 scripts/validate_context_setup.py --root /ruta/al/repo
python3 scripts/context_budget.py --root /ruta/al/repo
```

## Resultado típico en el repositorio objetivo

```text
AGENTS.md
CLAUDE.md                         # solo cuando sea necesario

docs/agent/
├── index.md                     # router
├── architecture.md             # solo hechos no evidentes
├── testing.md
├── task-template.md
├── routing-cases.json
└── modules/
    ├── auth.md
    ├── billing.md
    └── notifications.md
```

La división se realiza por comportamiento, ownership, invariantes y forma de verificación; no por la regla mecánica de “un documento por carpeta”.

## Validación del paquete

```bash
python3 -m py_compile skills/progressive-context-router/scripts/*.py
python3 -m unittest discover -s tests -v
npx skills add . --list
```

El repositorio incluye una acción de GitHub que prueba los scripts con Python 3.9 y 3.13.

## Compatibilidad y requisitos

- Formato: Agent Skills (`SKILL.md` con frontmatter YAML).
- Python 3.9 o superior es opcional y solo se necesita para los scripts.
- No requiere red ni dependencias Python externas.
- Licencia MIT.

## Referencias de formato

- Agent Skills specification: https://agentskills.io/specification
- Agent Skills best practices: https://agentskills.io/skill-creation/best-practices
- Skills CLI: https://github.com/vercel-labs/skills
