# Evidencias actuales y reproducción

**7 passed, 1 warning**, cinco integración y dos sistema local. [Fecha UTC y versiones](reportes/entorno.txt). Código fuente `b3f0b97`. No contiene DB, venv, cachés ni material privado.

## Recorrido de revisión
1. [stdout](reportes/pytest-salida.txt) y [JUnit con siete nodos](reportes/pytest-junit.xml).
2. [Matriz](../docs/matriz_casos_prueba.md): IDs conservados CP-INT-01/02, CP-SIS-03, CP-INT-04/05; nuevos CP-INT-06 y CP-SIS-07.
3. Comparar [pedido creado](api/pedido-exitoso.json) y [consultado](api/pedido-consultado.json), e inventario 10→7.

## Reportes y qué acreditan
| Archivo | Alcance |
|---|---|
| [entorno.txt](reportes/entorno.txt) | UTC real, commit fuente, versiones instaladas |
| [pytest-salida.txt](reportes/pytest-salida.txt) | Siete aprobados y warning upstream preservado |
| [pytest-junit.xml](reportes/pytest-junit.xml) | Siete testcase, cero failures/errors; nombres exactos correlacionan con nodos de matriz |
| [generacion-api.txt](reportes/generacion-api.txt) | Generador completado, warning conservado |

Normalización documentada: únicamente prefijos de rutas de venv/proyecto/temporales se sustituyen por `<virtualenv>`, `<project>`, `<temporary>` en logs. Se retira atributo hostname de JUnit por privacidad. No se alteran mensajes de warning/error, conteos, identidad/fecha del pedido, duraciones ni timestamps. El prefijo relativo de pytest puede preceder al token virtualenv.

## Nueve respuestas auxiliares, en orden
| Archivo | Qué muestra |
|---|---|
| [salud](api/salud.json) | GET /health 200, no salud profunda de DB |
| [productos](api/productos.json) | GET /products 200, seed sintético |
| [inventario antes](api/inventario-antes.json) | GET 200, stock 10 |
| [pedido exitoso](api/pedido-exitoso.json) | POST 201, cantidad 3, precio 12.50, ID/fecha generados reales |
| [pedido consultado](api/pedido-consultado.json) | GET 200 equivalente al pedido creado |
| [inventario después](api/inventario-despues.json) | GET 200, stock 7 |
| [stock insuficiente](api/stock-insuficiente.json) | POST 409: pedir 8 cuando quedan 7 |
| [cantidad inválida](api/cantidad-invalida.json) | POST 422, cantidad 0 |
| [producto inactivo](api/producto-inactivo.json) | POST 409, cantidad 2 |

Los JSON son cuerpos de respuesta; códigos esperados se verifican en el generador. No prueban conteos ni rollback por sí solos. La secuencia utiliza `product-active`; pytest usa `active-product`. CP-SIS-03 parte de stock 10 y cero pedidos; la secuencia auxiliar rechaza cantidad 0 después del éxito, con stock 7 y pedido anterior. CP-INT-05/06 se evidencian en pytest, no en un endpoint técnico. TestClient es HTTP en proceso, no red real.

## Comandos de reproducción (Linux/macOS, raíz del proyecto)
Preparar entorno como indica el [README](../README.md); no copiar venv ni DB.

```bash
source .venv/bin/activate
export PYTHONDONTWRITEBYTECODE=1
RUN_DIR="$(mktemp -d)"
export DATABASE_URL="sqlite:///$RUN_DIR/init.db"
python -m pip check
python -c 'from pathlib import Path; [compile(p.read_text(), str(p), "exec") for d in ("app", "scripts", "tests") for p in Path(d).rglob("*.py")]; print("Compile: PASS")'
python -m scripts.init_db
python -m pytest -q -p no:cacheprovider --basetemp "$RUN_DIR/pytest" --junitxml=evidencias/reportes/pytest-junit.xml
python -m scripts.generate_evidence
```

El generador crea su propia SQLite temporal y libera el engine; no escribe runtime. Para repetir un caso: `python -m pytest -q -p no:cacheprovider tests/test_orders_integration.py::test_post_flush_failure_rolls_back_before_session_close --basetemp "$RUN_DIR/isolated"`.

Reproducir produce identidad, fecha y duraciones nuevas; no comparar esos valores como fixtures. [Resultados y límites](../docs/resultados_conclusiones.md).
