# Estrategia de pruebas

Validar que pedido y existencias se confirman juntos o quedan sin cambios en los escenarios definidos. [Matriz con siete casos](matriz_casos_prueba.md) · [evidencia actual](../evidencias/README.md).

## 1. Objetivo de las pruebas
Comprobar integridad transaccional y coherencia del borde HTTP local, con aserciones sobre respuestas y estado SQL persistido.

## 2. Componentes incluidos
Catalog valida productos, Inventory reserva existencias y Orders orquesta una Session compartida. FastAPI es el borde externo; SQLAlchemy y SQLite basados en archivo son reales. [Diagrama](../diagramas/arquitectura.svg) · [arquitectura](arquitectura.md).

## 3. Puntos de integración que serán validados
| Punto | Casos |
|---|---|
| Orders → Catalog | CP-INT-01, CP-INT-04 |
| Orders → Inventory | CP-INT-01, CP-INT-02 |
| Orders → persistencia y rollback | CP-INT-05, CP-INT-06 |
| HTTP → validación → servicios → SQLite → consultas | CP-SIS-03, CP-SIS-07 |

## 4. Riesgos identificados
| Riesgo | Caso |
|---|---|
| R1: confirmar stock sin pedido o viceversa | CP-INT-01 |
| R2: aceptar más existencias de las disponibles | CP-INT-02 |
| R3: entrada inválida modifica datos | CP-SIS-03 |
| R4: producto inactivo reservado | CP-INT-04 |
| R5: reserva en memoria sin pedido | CP-INT-05 |
| R6: SQL parcial no revertido explícitamente | CP-INT-06 |
| R7: HTTP exitoso sin persistencia coherente | CP-SIS-07 |

## 5. Alcance y exclusiones
Cinco pruebas de integración y dos de sistema local con TestClient en proceso. No acreditan servidor de red, despliegue, concurrencia, carga, seguridad integral, fallas físicas, fallas de commit ni HTTP 500. No se mide porcentaje de cobertura. El producto sin stock existe en la fixture, pero no tiene caso dedicado.

## 6. Ambiente necesario
Python 3.14 y requisitos fijados; [instalación](../README.md). Cada fixture crea SQLite temporal, sin usar runtime. [Versiones observadas](../evidencias/reportes/entorno.txt). No se requieren servicios externos ni tecnologías de pago.

## 7. Datos de prueba
Fixtures: `active-product` activo, precio 12.50, stock 10; `inactive-product` inactivo, stock 4; `zero-stock-product` stock 0. Cantidades 3 (éxito), 11 (insuficiente), 2 (inactivo), 0 (inválida). Seed de demo separado: `product-active`, `product-inactive`, `product-zero`. Inicializar agrega ausentes, no restablece stock consumido.

## 8. Dependencias reales y simuladas
Servicios, ORM y SQLite son reales. Solo dos dobles de persistencia: `FailingOrderPersistence` lanza RuntimeError después de reserva en memoria, antes de flush (CP-INT-05). `FailingFlushedOrderPersistence` agrega pedido, hace flush real y afirma stock 7 y un pedido antes de lanzar RuntimeError (CP-INT-06). Orders traduce a PersistenceError y ejecuta rollback. El segundo caso exige causa y mensaje exactos, stock 10 y cero pedidos en la misma sesión y en otra, antes de cerrar la original: no confunde rollback explícito con cierre. No simulan caída de SQLite ni fallo de commit.

## 9. Herramientas seleccionadas
pytest automatiza aserciones y JUnit; TestClient recorre HTTP sin Uvicorn; SQLAlchemy permite verificación independiente. El [generador](../scripts/generate_evidence.py) captura nueve respuestas en SQLite descartable. [Reproducción exacta](../evidencias/README.md).

## 10. Criterios para determinar si una prueba es aprobada o fallida
Aprobado: todas las aserciones del nodo se cumplen y pytest lo marca passed. Fallido: una aserción, excepción no esperada o error de preparación impide ese contrato; investigar sin sustituir evidencia. Suite aceptable: siete passed, cero failures/errors; conservar y revisar warnings. Los rechazos y fallas controladas esperados son casos aprobados. Los JSON solos no acreditan rollback ni conteos de tablas. El generador exige códigos 200/201/409/422 y equivalencia del pedido creado/consultado; es evidencia auxiliar, no un octavo caso de la suite.
