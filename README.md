---
cover: >-
  https://images.unsplash.com/photo-1573096272447-f58103a3fe16?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHNlYXJjaHw0fHxzdWJ3b29mZXJ8ZW58MHx8fHwxNzUyODE2NjA0fDA&ixlib=rb-4.1.0&q=85
coverY: 548.242620020113
layout:
  width: default
  cover:
    visible: true
    size: full
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Speaker Simulation Software - SSS

Proyecto de simulación físico-numérica de altavoces para la maestría en Física Aplicada (Acústica).

## Estructura del proyecto

* `core/`: Motor físico (Thiele-Small, cajas).
* `acoustics/`: Modelado de salas y propagación.
* `visualization/`: Gráficas 2D/3D.
* `config/`: Configuraciones en JSON o YAML.
* `data/`: Datos de drivers reales o sintéticos.
* `tests/`: Pruebas unitarias.
* `docs/`: Documentación técnica.

## Cómo ejecutar

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Ejecutar simulación principal
python main.py

# Abrir notebooks
jupyter notebook
```

$$
f(x) = x * e^{2 pi i \xi x}
$$

