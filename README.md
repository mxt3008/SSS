# Speaker Simulator

Proyecto de simulación físico-numérica de altavoces para la maestría en Física Aplicada (Acústica).

## Estructura del proyecto

- `core/`: Motor físico (Thiele-Small, cajas).
- `acoustics/`: Modelado de salas y propagación.
- `visualization/`: Gráficas 2D/3D.
- `config/`: Configuraciones en JSON o YAML.
- `data/`: Datos de drivers reales o sintéticos.
- `tests/`: Pruebas unitarias.
- `docs/`: Documentación técnica.

## Cómo ejecutar

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Ejecutar simulación principal
python main.py

# Abrir notebooks
jupyter notebook
