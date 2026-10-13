# Resultados y conclusiones

La ejecución actual aprobó **7 casos (5 integración, 2 sistema local), con 1 warning**. [Salida completa](../evidencias/reportes/pytest-salida.txt) · [JUnit](../evidencias/reportes/pytest-junit.xml) · [entorno y fecha UTC](../evidencias/reportes/entorno.txt). Fuente ejecutable de las evidencias: commit `b3f0b97`.

## Resultados observados
| Caso | Observación respaldada por aserciones |
|---|---|
| CP-INT-01 | Pedido cantidad 3 recuperable en otra Session y stock 10→7 |
| CP-INT-02 | InsufficientStockError; stock 10 y cero pedidos |
| CP-SIS-03 | HTTP 422 para cantidad 0; stock 10 y cero pedidos |
| CP-INT-04 | ProductInactiveError; stock 4 y cero pedidos |
| CP-INT-05 | PersistenceError antes de flush; stock 10 y cero pedidos en otra Session |
| CP-INT-06 | Flush real muestra stock 7 y un pedido; RuntimeError controlado traducido; rollback explícito deja stock 10 y cero pedidos en misma y otra Session antes de cerrar original |
| CP-SIS-07 | POST 201, GET pedido e inventario 200, precio 12.50, identidad y fecha; persistencia independiente de una fila y stock 7 |

[Doce campos y nodos por caso](matriz_casos_prueba.md). Son resultados de tests aprobados, no capturas de cada valor SQL. Los nueve JSON auxiliares registran salud, productos, inventario antes/después, pedido creado/consultado y tres rechazos. El generador comprueba códigos y equivalencia del pedido; no añade casos a pytest.

## Entorno y evidencia auxiliar
[Versiones reales y fecha UTC](../evidencias/reportes/entorno.txt) y [generación API](../evidencias/reportes/generacion-api.txt). Los comandos de reproducción están en el [índice de evidencias](../evidencias/README.md).

## Interpretación
Una Session orquestada por Orders permite confirmar pedido y descuento juntos. CP-INT-05 comprueba rechazo técnico antes de SQL; CP-INT-06 añade evidencia de rollback de cambios enviados a SQLite, sin depender del cierre de sesión. CP-SIS-07 conecta respuesta HTTP y almacenamiento independiente. Estos contratos delimitados justifican la solución académica; no demuestran ausencia general de defectos.

## Advertencia upstream conservada
`StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.`

Se conserva íntegra en stdout y en el reporte del generador. Es un aviso de compatibilidad, no una falla funcional observada. No se ocultó ni se cambiaron dependencias para eliminarlo.

## Límites y próximos pasos
TestClient opera en proceso: no es servidor de red ni despliegue completo. Las excepciones son inyectadas deliberadamente, no una caída física de SQLite, fallo de disco o de commit. No se probó HTTP 500, concurrencia, carga, autenticación ni seguridad integral; no se calculó cobertura porcentual. Los JSON 409 son auxiliares y no sustituyen los conteos SQL de integración. Producto sin stock dedicado, HTTP 404/409/500 y concurrencia son posibles ampliaciones, no resultados actuales.

La [presentación HTML](../presentacion/index.html) utilizada durante la exposición corresponde a la versión de cinco casos. El paquete actual amplía la suite a siete casos (cinco de integración y dos de sistema local).
