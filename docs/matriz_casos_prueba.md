# Matriz de siete casos de prueba

Resultado actual: siete aprobados; cinco de integración y dos de sistema local en proceso. [Ejecución y entorno](../evidencias/README.md). Cada caso tiene los doce campos de la sección 9 de la guía; riesgo y nodo son trazabilidad adicional.

## CP-INT-01 — Crear pedido con stock disponible

| Campo | Definición |
|---|---|
| Identificador | CP-INT-01 |
| Nombre | Crear pedido con stock disponible |
| Tipo de prueba | Integración |
| Objetivo | Pedido recuperable de cantidad 3 y producto correcto; stock 7. |
| Componentes involucrados | Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | Producto activo; stock 10; base temporal nueva. |
| Datos de entrada | active-product, cantidad 3 |
| Procedimiento | Invocar Orders y consultar pedido e inventario con otra Session. |
| Resultado esperado | Pedido recuperable de cantidad 3 y producto correcto; stock 7. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: Pedido recuperable de cantidad 3 y producto correcto; stock 7. |
| Evidencia | [Nodo `test_places_order_and_commits_stock`](../tests/test_orders_integration.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R1: confirmación parcial. **Nodo pytest:** `tests/test_orders_integration.py::test_places_order_and_commits_stock`.

## CP-INT-02 — Rechazar stock insuficiente

| Campo | Definición |
|---|---|
| Identificador | CP-INT-02 |
| Nombre | Rechazar stock insuficiente |
| Tipo de prueba | Integración |
| Objetivo | InsufficientStockError; stock 10; cero pedidos. |
| Componentes involucrados | Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | Producto activo; stock 10; cero pedidos. |
| Datos de entrada | active-product, cantidad 11 |
| Procedimiento | Invocar Orders; exigir InsufficientStockError; consultar con otra Session. |
| Resultado esperado | InsufficientStockError; stock 10; cero pedidos. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: InsufficientStockError; stock 10; cero pedidos. |
| Evidencia | [Nodo `test_insufficient_stock_rolls_back`](../tests/test_orders_integration.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R2: stock negativo. **Nodo pytest:** `tests/test_orders_integration.py::test_insufficient_stock_rolls_back`.

## CP-SIS-03 — Rechazar cantidad HTTP inválida

| Campo | Definición |
|---|---|
| Identificador | CP-SIS-03 |
| Nombre | Rechazar cantidad HTTP inválida |
| Tipo de prueba | Sistema |
| Objetivo | HTTP 422; stock 10; cero pedidos. |
| Componentes involucrados | FastAPI, Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | TestClient sobre base temporal; stock 10; cero pedidos. |
| Datos de entrada | POST /orders: active-product, quantity 0 |
| Procedimiento | Enviar POST y consultar inventario y conteo SQL con otra Session. |
| Resultado esperado | HTTP 422; stock 10; cero pedidos. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: HTTP 422; stock 10; cero pedidos. |
| Evidencia | [Nodo `test_invalid_quantity_is_rejected_without_persistence`](../tests/test_orders_api.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R3: entrada inválida altera datos. **Nodo pytest:** `tests/test_orders_api.py::test_invalid_quantity_is_rejected_without_persistence`.

## CP-INT-04 — Rechazar producto no vendible

| Campo | Definición |
|---|---|
| Identificador | CP-INT-04 |
| Nombre | Rechazar producto no vendible |
| Tipo de prueba | Integración |
| Objetivo | ProductInactiveError; stock 4; cero pedidos. |
| Componentes involucrados | Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | Producto inactivo; stock 4; cero pedidos. |
| Datos de entrada | inactive-product, cantidad 2 |
| Procedimiento | Invocar Orders; exigir ProductInactiveError; verificar con otra Session. |
| Resultado esperado | ProductInactiveError; stock 4; cero pedidos. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: ProductInactiveError; stock 4; cero pedidos. |
| Evidencia | [Nodo `test_non_sellable_product_does_not_reserve`](../tests/test_orders_integration.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R4: reserva no permitida. **Nodo pytest:** `tests/test_orders_integration.py::test_non_sellable_product_does_not_reserve`.

## CP-INT-05 — Revertir falla antes de flush

| Campo | Definición |
|---|---|
| Identificador | CP-INT-05 |
| Nombre | Revertir falla antes de flush |
| Tipo de prueba | Integración |
| Objetivo | PersistenceError; stock 10; cero pedidos. No UPDATE SQL emitido. |
| Componentes involucrados | Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | Base nueva; stock 10; FailingOrderPersistence inyectado. |
| Datos de entrada | active-product, cantidad 3 |
| Procedimiento | Reservar; doble lanza RuntimeError antes de flush; verificar otra Session. |
| Resultado esperado | PersistenceError; stock 10; cero pedidos. No UPDATE SQL emitido. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: PersistenceError; stock 10; cero pedidos. No UPDATE SQL emitido. |
| Evidencia | [Nodo `test_persistence_failure_rolls_back`](../tests/test_orders_integration.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R5: reserva sin pedido. **Nodo pytest:** `tests/test_orders_integration.py::test_persistence_failure_rolls_back`.

## CP-INT-06 — Revertir SQL tras flush antes de cerrar sesión

| Campo | Definición |
|---|---|
| Identificador | CP-INT-06 |
| Nombre | Revertir SQL tras flush antes de cerrar sesión |
| Tipo de prueba | Integración |
| Objetivo | PersistenceError causada por RuntimeError con mensaje controlado; stock 10 y cero pedidos en misma y otra Session. |
| Componentes involucrados | Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | Base nueva; stock 10; FailingFlushedOrderPersistence inyectado. |
| Datos de entrada | active-product, cantidad 3 |
| Procedimiento | Agregar pedido; flush; afirmar stock 7 y un pedido; lanzar RuntimeError; comprobar causa exacta y ambas sesiones antes de cerrar original. |
| Resultado esperado | PersistenceError causada por RuntimeError con mensaje controlado; stock 10 y cero pedidos en misma y otra Session. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: PersistenceError causada por RuntimeError con mensaje controlado; stock 10 y cero pedidos en misma y otra Session. |
| Evidencia | [Nodo `test_post_flush_failure_rolls_back_before_session_close`](../tests/test_orders_integration.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R6: SQL parcial sin rollback explícito. **Nodo pytest:** `tests/test_orders_integration.py::test_post_flush_failure_rolls_back_before_session_close`.

## CP-SIS-07 — Crear y consultar pedido por HTTP

| Campo | Definición |
|---|---|
| Identificador | CP-SIS-07 |
| Nombre | Crear y consultar pedido por HTTP |
| Tipo de prueba | Sistema |
| Objetivo | 200 inicial; 201 con ID y fecha, cantidad 3 y precio 12.50; GET 200 igual al pedido; stock 7; una fila persistida. |
| Componentes involucrados | FastAPI, Orders, Catalog, Inventory, SQLAlchemy y SQLite |
| Precondiciones | TestClient sobre base nueva; producto activo; stock 10. |
| Datos de entrada | POST /orders: active-product, quantity 3 |
| Procedimiento | GET inventario; POST; GET pedido e inventario; verificar SQL con sesión independiente. |
| Resultado esperado | 200 inicial; 201 con ID y fecha, cantidad 3 y precio 12.50; GET 200 igual al pedido; stock 7; una fila persistida. |
| Resultado obtenido | Aserciones aprobadas en la ejecución actual: 200 inicial; 201 con ID y fecha, cantidad 3 y precio 12.50; GET 200 igual al pedido; stock 7; una fila persistida. |
| Evidencia | [Nodo `test_valid_order_http_flow_persists_order_and_stock`](../tests/test_orders_api.py) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [stdout](../evidencias/reportes/pytest-salida.txt) |
| Estado | Aprobado |

**Riesgo vinculado:** R7: respuesta HTTP incoherente con persistencia. **Nodo pytest:** `tests/test_orders_api.py::test_valid_order_http_flow_persists_order_and_stock`.

Los JSON adicionales usan el seed `product-active`, no las fixtures `active-product`; no sustituyen los conteos SQL ni las pruebas técnicas. Un rechazo esperado o falla inyectada con aserciones correctas significa caso aprobado, no test fallido.
