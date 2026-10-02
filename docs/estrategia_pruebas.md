# Estrategia de pruebas

La suite protege la integridad del pedido y sus existencias mediante cuatro pruebas de integración y una prueba del borde HTTP. Utiliza servicios y SQLite reales, datos sintéticos y una base temporal por caso; no necesita Uvicorn ni red externa.

## Cinco casos ejecutables

| Prueba | Nivel | Comprobación desde una sesión de verificación |
|---|---|---|
| `test_places_order_and_commits_stock` | Integración | Cantidad 3: stock de 10 a 7 y pedido recuperable con producto y cantidad correctos. |
| `test_insufficient_stock_rolls_back` | Integración | Solicitar 11 con stock 10 produce `InsufficientStockError`; quedan stock 10 y cero pedidos. |
| `test_non_sellable_product_does_not_reserve` | Integración | Producto inactivo produce `ProductInactiveError`; quedan stock 4 y cero pedidos. |
| `test_persistence_failure_rolls_back` | Integración | Falla después de reservar produce `PersistenceError`; quedan stock 10 y cero pedidos. |
| `test_invalid_quantity_is_rejected_without_persistence` | Borde HTTP / sistema local | `TestClient` envía cantidad 0: HTTP `422`, stock 10 y cero pedidos. |

Las cuatro primeras están en [test_orders_integration.py](../tests/test_orders_integration.py); la última en [test_orders_api.py](../tests/test_orders_api.py). La clasificación de sistema corresponde al límite HTTP local en proceso, no a un despliegue completo con servidor y red.

## Aislamiento y dependencias

La [fixture](../tests/conftest.py) utiliza `tmp_path` para crear SQLite basado en archivo. Cada prueba recibe un esquema nuevo con productos `active-product` (10 unidades), `zero-stock-product` (0) e `inactive-product` (4). Son identificadores distintos de los del seed de ejecución: `product-active`, `product-zero` y `product-inactive`. No se utiliza ni se modifica la base `runtime/lab02.db`.

Catalog, Inventory, Orders y SQLAlchemy son reales. Las comprobaciones posteriores abren otra sesión para consultar estado persistido y evitar confundir el estado en memoria con una confirmación efectiva.

## Falla técnica controlada

El único doble es `FailingOrderPersistence`, inyectado en `OrdersService(persistence=...)`. Implementa `save_order` y lanza `RuntimeError` después de que Inventory haya reservado en la sesión, antes del `commit`. Orders ejecuta `rollback` y traduce la excepción a `PersistenceError`.

La prueba exige tanto la excepción como stock original y cero pedidos. La reserva está modificada en memoria dentro de la sesión: el doble falla antes de `flush`, por lo que no se ha emitido el `UPDATE` de stock. No acredita rollback de un `UPDATE` SQL ya enviado, no simula una caída física de SQLite ni verifica un fallo durante `commit`; tampoco comprueba HTTP `500`. No existe un endpoint para provocar fallas artificiales.

## Ejecución

Con el entorno y dependencias del [README](../README.md):

```bash
python -m pytest -q -p no:cacheprovider
python -m pytest -q -p no:cacheprovider \
  tests/test_orders_integration.py::test_persistence_failure_rolls_back
```

La suite debe informar cinco pruebas aprobadas; el segundo comando ejecuta únicamente el caso técnico. Una advertencia de deprecación de la combinación Starlette/TestClient con httpx puede aparecer con las versiones fijadas: se debe conservar y revisar, no ocultar ni interpretar como una sexta prueba.

## Límites de cobertura

El mapeo implementado permite HTTP `201`, `404`, `409`, `422` y `500`, pero la suite automatizada solo comprueba directamente `422` por HTTP. Los otros rechazos de negocio se ejercitan mediante servicios; los ejemplos del README permiten verificaciones HTTP adicionales.

No se mide cobertura porcentual ni se prueban concurrencia, carga, autenticación, seguridad integral, migraciones, fallas de disco, desconexiones, precios cambiantes o disponibilidad en producción. El producto sin stock existe en la fixture, pero no tiene un caso dedicado. Cinco resultados positivos respaldan estos contratos acotados, no la ausencia de defectos en todo el sistema.
