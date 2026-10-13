# Referencias

Esta bibliografía separa la guía académica, la documentación técnica oficial y la evidencia generada por el proyecto. Las afirmaciones técnicas de la presentación se limitan a las fuentes oficiales enlazadas aquí.

## Guía del curso

La guía del profesor gobierna los entregables y la evaluación del laboratorio. No se reproduce ni se copia en este repositorio; se consulta desde el medio académico autorizado.

## Documentación técnica oficial

1. **FastAPI — Testing.** Consultada para sustentar que `TestClient` se basa en HTTPX y permite pruebas y aserciones directas con pytest. Respalda CP-SIS-03, el generador de evidencia HTTP y la explicación de la estrategia.
   <https://fastapi.tiangolo.com/tutorial/testing/>
2. **FastAPI — First Steps.** Consultada para sustentar la documentación interactiva en `/docs` y la generación OpenAPI. Respalda el borde HTTP mostrado en la demostración y la diapositiva de ambiente.
   <https://fastapi.tiangolo.com/tutorial/first-steps/>
3. **SQLAlchemy — Session Basics.** Consultada para sustentar que una transacción de `Session` permanece activa hasta `commit` o `rollback`, junto con los patrones de cierre/liberación. Respalda la decisión de una `Session` orquestada por Orders.
   <https://docs.sqlalchemy.org/en/20/orm/session_basics.html>
4. **SQLite — Foreign Key Support.** Consultada para sustentar que la aplicación debe habilitar la aplicación de claves foráneas por conexión con `PRAGMA foreign_keys = ON`; no se la supone activa. Respalda la configuración de `Database`.
   <https://www.sqlite.org/foreignkeys.html>
5. **SQLite — Is Transactional.** Consultada para sustentar la propiedad atómica: los cambios de una transacción SQLite ocurren completamente o no ocurren. Respalda la explicación de `commit`/`rollback` y CP-INT-05 y CP-INT-06.
   <https://www.sqlite.org/transactional.html>
6. **pytest — Managing pytest's output.** Consultada para sustentar que `--junit-xml` produce reportes XML procesables por herramientas. Respalda el artefacto `evidencias/reportes/pytest-junit.xml`.
   <https://docs.pytest.org/en/stable/how-to/output.html>
7. **Python — `venv`.** Consultada para sustentar el uso de entornos virtuales aislados. Respalda las instrucciones reproducibles de ambiente local.
   <https://docs.python.org/3/library/venv.html>

## Evidencia generada por el proyecto

La evidencia no es una fuente externa ni reemplaza las referencias anteriores. Registra ejecuciones locales observadas y debe leerse con sus límites:

- [Índice de evidencia](../evidencias/README.md): secuencia HTTP, reportes y límites.
- [Salida de pytest](../evidencias/reportes/pytest-salida.txt): resultado observado `7 passed, 1 warning`.
- [JUnit XML](../evidencias/reportes/pytest-junit.xml): resultado procesable de los siete casos.
- [Resultados y conclusiones](resultados_conclusiones.md): interpretación, alcance y advertencia observada.

No se atribuyen autores, fechas ni afirmaciones adicionales que no estén declarados en las fuentes verificadas o en los artefactos del proyecto.

Las siete URL son documentación oficial; no se inventan fechas de consulta, autores ni verificación automática de contenido versionado. La guía académica se atribuye por su título: «Guía para la exposición y laboratorio Estrategias de pruebas de integración y de sistema», secciones 7, 9, 12 y 13. No se publica su archivo local ni material privado.
