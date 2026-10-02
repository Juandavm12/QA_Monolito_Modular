# Arquitectura del pedido transaccional

Una aplicación FastAPI integra Catalog, Inventory y Orders con SQLAlchemy y SQLite. El límite modular organiza responsabilidades internas; no hay despliegues separados ni comunicación por red entre módulos.

## Responsabilidades

| Componente | Implementación | Contrato y responsabilidad |
|---|---|---|
| HTTP | `app/main.py` | `create_app()` valida cuerpos, entrega una sesión por solicitud y traduce errores a respuestas. |
| Catalog | `app/modules/catalog/` | `CatalogService` consulta productos y valida su estado activo; devuelve vistas, no modelos ORM. |
| Inventory | `app/modules/inventory/` | `InventoryService` consulta existencias y reserva sin confirmar la transacción. |
| Orders | `app/modules/orders/` | `OrdersService` coordina el pedido y decide `commit` o `rollback`. |
| Infraestructura | `app/core/database.py` | `Database` configura el motor, crea y cierra sesiones y habilita claves foráneas SQLite. |

El [diagrama SVG](../diagramas/arquitectura.svg) y su [fuente Mermaid](../diagramas/arquitectura.mmd) representan el mismo límite de aplicación, flujo de escritura y relaciones persistentes. Las lecturas HTTP de productos, inventario y pedidos invocan directamente el servicio correspondiente; no pasan todas por Orders.

## Flujo de creación

1. FastAPI valida `product_id` y una `quantity` positiva. Un cuerpo inválido se rechaza con `422` antes de entrar al servicio.
2. HTTP llama `OrdersService.place_order(session, command)` con la sesión de la solicitud.
3. Orders llama `CatalogService.get_active_product` con esa sesión. Un producto ausente o inactivo detiene el flujo antes de reservar.
4. Orders llama `InventoryService.reserve` con la misma sesión. Inventory comprueba disponibilidad y modifica el objeto en sesión; no ejecuta `commit`.
5. Orders construye `Order` con el precio consultado y llama `OrderPersistence.save_order`. El adaptador real agrega el pedido a la sesión sin confirmar.
6. Orders ejecuta un único `session.commit()` para pedido y existencias. Ante `DomainError`, ejecuta `rollback` y propaga el rechazo; ante otra excepción dentro de ese bloque, revierte y la envuelve en `PersistenceError`.

Database no decide la confirmación de pedidos. La sesión se cierra al terminar la solicitud. La validación defensiva de cantidad en Orders lanza `ValueError` antes del bloque transaccional; la validación HTTP impide llegar allí con cantidad no positiva.

`OrderPersistence` es un protocolo inyectable. Su doble de prueba falla después de reservar para comprobar la reversión, sin agregar una ruta técnica al API. El estado se verifica desde otra sesión, no solo desde los objetos modificados.

## Persistencia real

| Tabla y propietario | Claves y datos relevantes | Relación |
|---|---|---|
| `products` — Catalog | `id` PK; nombre, precio y estado activo | Un producto puede tener inventario y varios pedidos. |
| `inventory_items` — Inventory | `product_id` PK y FK; cantidad con `CHECK quantity >= 0` | `product_id → products.id`; como máximo una fila por producto, no se obliga a que todos tengan inventario. |
| `orders` — Orders | `id` PK; `product_id` FK; cantidad, precio y fecha | `product_id → products.id`; varios pedidos pueden apuntar al mismo producto. |

No existe clave foránea de `orders` a `inventory_items`. El esquema comparte una base física, aunque cada módulo posee su modelo. SQLite habilita `PRAGMA foreign_keys=ON` en cada conexión. El precio del pedido queda almacenado como valor de la compra. La fecha tiene valor predeterminado de servidor; el identificador se genera con UUID.

## Inicialización y configuración

`app/main.py`, `scripts/init_db.py` y `scripts/seed_data.py` importan los tres modelos antes de `Database.create_all()`. El inicializador crea tablas y agrega registros ausentes; no es un mecanismo de migraciones ni de restablecimiento de stock.

| Identificador del seed | Activo | Precio | Existencias iniciales |
|---|---|---|---:|
| `product-active` | Sí | `12.50` | 10 |
| `product-zero` | Sí | `8.00` | 0 |
| `product-inactive` | No | `5.00` | 4 |

Una URL explícita en `create_app(database_url=...)` tiene precedencia sobre `DATABASE_URL`; sin ambas se utiliza `sqlite:///./runtime/lab02.db`. Las pruebas usan bases temporales independientes.

## Respuestas y límites

Las rutas y ejemplos están en el [README](../README.md). Los errores controlados se traducen a `404` (ausente), `409` (estado incompatible), `422` (validación HTTP) y `500` (persistencia, mensaje genérico sin causa interna).

No hay microservicios, autenticación, pagos, colas, interfaz gráfica ni servicios externos. La transacción protege los casos secuenciales cubiertos; no demuestra que la reserva sea segura ante solicitudes concurrentes. No hay bloqueo explícito ni prueba de contención. La [estrategia de pruebas](estrategia_pruebas.md) delimita la evidencia automatizada disponible.
