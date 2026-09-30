# Limitaciones del prototipo - InvestCopilot

## 1. Propósito de este documento

Este documento recoge las principales limitaciones del prototipo InvestCopilot.

Su objetivo es dejar claro que el prototipo es una demostración funcional y conceptual de una arquitectura multiagente aplicada al análisis previo de decisiones de inversión, pero no constituye una herramienta operativa definitiva ni un sistema validado para tomar decisiones reales de inversión.

InvestCopilot debe entenderse, en esta fase, como un entorno de prueba para demostrar cómo distintos agentes especializados pueden analizar una hipótesis de inversión desde perspectivas complementarias: research, macro, riesgo, mandatos, Asset Allocation y síntesis final.

---

## 2. Naturaleza del prototipo

El prototipo tiene carácter experimental y demostrativo.

Su finalidad principal es validar:

- La separación de funciones entre agentes especializados.
- El uso de información organizada por dominios.
- La generación de respuestas trazables.
- La identificación de riesgos, trade-offs y puntos pendientes.
- La capacidad de producir una síntesis estructurada para apoyar al gestor.
- El enfoque de IA responsable basado en supervisión humana.

El prototipo no debe utilizarse como una herramienta definitiva de asesoramiento, gestión, ejecución o recomendación de inversiones.

---

## 3. Uso de datos parciales, simplificados o simulados

Durante la fase de prototipo, es posible que algunos datos utilizados sean:

- Parciales.
- Simplificados.
- Estimados.
- Simulados.
- Inventados con fines demostrativos.
- No actualizados.
- No reconciliados con sistemas oficiales.

Cuando se utilicen datos simulados o simplificados, debe indicarse expresamente en la respuesta del agente.

Ejemplo recomendado:

```markdown
Nota: este análisis utiliza datos simulados para fines de demostración del prototipo. No debe utilizarse como base para una decisión real de inversión.
```

Los datos simulados nunca deben presentarse como datos reales.

---

## 4. Limitaciones sobre datos de mercado

El prototipo puede no disponer de datos de mercado completos, actualizados o validados.

Entre las posibles limitaciones están:

- Series históricas incompletas.
- Fechas de valoración no homogéneas.
- Ausencia de precios actualizados.
- Falta de datos de benchmark.
- Falta de datos de divisa.
- Ausencia de información sobre costes, liquidez o spreads.
- Datos de rentabilidad calculados con frecuencia distinta.
- Inexistencia de validación contra fuentes oficiales.

Por tanto, cualquier métrica calculada debe interpretarse con cautela.

---

## 5. Limitaciones sobre carteras

El prototipo puede trabajar con carteras de ejemplo, carteras simplificadas o carteras no actualizadas.

Esto implica que los resultados pueden no reflejar con precisión:

- La cartera real vigente.
- Los pesos actuales.
- Las posiciones agregadas.
- Las exposiciones indirectas.
- La exposición por divisa.
- La exposición por región.
- La exposición por sector.
- La exposición por emisor.
- La exposición por duración o rating.
- La exposición consolidada a través de fondos subyacentes.

Antes de cualquier uso real, la cartera debería validarse contra las fuentes oficiales correspondientes.

---

## 6. Limitaciones sobre métricas de riesgo

Las métricas de riesgo generadas por el prototipo pueden tener carácter aproximado o ilustrativo.

Esto puede afectar a variables como:

- Volatilidad.
- VaR.
- Tracking error.
- Drawdown.
- Beta.
- Correlaciones.
- Concentración.
- Sensibilidad a factores.
- Contribución al riesgo.
- Escenarios de estrés.

Estas métricas dependen de la calidad de los datos, la metodología utilizada, el periodo histórico, la frecuencia de cálculo y los supuestos aplicados.

Por tanto, no deben considerarse métricas oficiales salvo que hayan sido calculadas y validadas con la metodología y fuentes aprobadas por el área correspondiente.

---

## 7. Limitaciones sobre mandatos y restricciones

El prototipo puede no disponer de todos los mandatos, límites internos, restricciones regulatorias o condiciones específicas aplicables a cada cartera, fondo o vehículo de inversión.

Entre las posibles limitaciones están:

- Mandatos incompletos.
- Límites no actualizados.
- Restricciones no parametrizadas.
- Falta de reglas específicas por producto.
- Falta de validación jurídica, regulatoria u operativa.
- Ausencia de excepciones aprobadas.
- Falta de información sobre restricciones comerciales o de idoneidad.

Por tanto, cualquier validación de cumplimiento debe considerarse preliminar y requerir revisión humana.

---

## 8. Limitaciones sobre House View y escenarios macro

El prototipo puede utilizar una versión simplificada del House View o de los escenarios macroeconómicos.

Esto puede implicar:

- Escenarios macro incompletos.
- Ausencia de probabilidades oficiales.
- Narrativas macro resumidas.
- Falta de actualización reciente.
- Variables macro no incluidas.
- Falta de sensibilidad por regiones o clases de activo.
- Falta de conexión directa con documentos oficiales de estrategia.

Por tanto, el análisis macro generado por el agente debe considerarse una interpretación estructurada del contexto disponible, no una visión oficial definitiva salvo que así se indique expresamente.

---

## 9. Limitaciones sobre research y argumentos de inversión

El prototipo puede trabajar con research parcial, notas internas resumidas o argumentos de inversión creados para la demostración.

Esto implica que los análisis cualitativos pueden no recoger:

- Toda la información disponible.
- La visión completa del gestor.
- La visión oficial del equipo de análisis.
- Cambios recientes en mercado.
- Eventos corporativos relevantes.
- Revisión fundamental actualizada.
- Información de valoración completa.
- Riesgos idiosincráticos específicos.

Por tanto, el Agente Research debe indicar siempre qué información ha utilizado y qué información faltaría para completar el análisis.

---

## 10. Limitaciones sobre la síntesis final

El Agente Síntesis o Comité Virtual integra las respuestas de otros agentes, pero no sustituye al gestor ni al comité de inversión.

Su función es organizar conclusiones, detectar tensiones y presentar una visión consolidada.

La síntesis final no debe interpretarse como:

- Una recomendación automática.
- Una decisión de inversión.
- Una aprobación de la operación.
- Una validación definitiva de riesgos.
- Una validación definitiva de cumplimiento.
- Una instrucción de ejecución.

Si existen discrepancias entre agentes, deben mostrarse de forma clara.

---

## 11. Limitaciones técnicas

El prototipo puede estar sujeto a limitaciones técnicas propias de una primera versión.

Entre ellas:

- Lectura incompleta de documentos largos.
- Dificultad para interpretar tablas complejas.
- Dependencia de nombres de archivos y estructuras de carpetas.
- Posibles errores de extracción de información.
- Posibles inconsistencias entre fuentes.
- Falta de conexión con sistemas corporativos oficiales.
- Falta de automatización completa de cálculos.
- Falta de control de versiones avanzado.
- Falta de auditoría técnica completa.

Estas limitaciones deben tenerse en cuenta al interpretar cualquier resultado.

---

## 12. Limitaciones de lenguaje y razonamiento

Los agentes pueden generar respuestas útiles y estructuradas, pero pueden cometer errores si:

- La información de entrada es ambigua.
- Los datos están incompletos.
- Existen contradicciones entre fuentes.
- Las instrucciones no están suficientemente delimitadas.
- Se les pide responder fuera de su dominio.
- Se mezclan datos reales y simulados sin identificarlo.
- La pregunta requiere información que no está disponible.

Por este motivo, las respuestas deben revisarse siempre antes de ser utilizadas en un contexto real.

---

## 13. Riesgo de sobreinterpretación

Existe riesgo de que una respuesta bien redactada parezca más concluyente de lo que realmente es.

Para evitarlo, todos los agentes deben:

- Indicar los supuestos.
- Señalar la información faltante.
- Evitar conclusiones categóricas.
- Distinguir entre análisis y decisión.
- Recordar que la validación final es humana.
- Marcar claramente si los datos son simulados.

El tono debe ser profesional y útil, pero prudente.

---

## 14. No sustitución del criterio profesional

InvestCopilot no sustituye:

- Al gestor de inversiones.
- Al equipo de riesgos.
- Al equipo de Asset Allocation.
- Al equipo de cumplimiento normativo.
- Al comité de inversión.
- A los procesos internos de aprobación.
- A las fuentes oficiales de datos.
- A la revisión experta.

El prototipo puede ayudar a preparar mejor una decisión, pero no debe tomarla.

---

## 15. No ejecución de operaciones

InvestCopilot no ejecuta operaciones.

El prototipo no debe generar instrucciones operativas como:

- Comprar.
- Vender.
- Suscribir.
- Reembolsar.
- Ejecutar.
- Ordenar.
- Rotar inmediatamente.
- Implementar sin revisión.

Puede analizar hipótesis de inversión, comparar alternativas y señalar riesgos, pero cualquier actuación posterior debe seguir los procesos internos establecidos.

---

## 16. Uso adecuado del prototipo

El prototipo puede utilizarse para:

- Demostrar la arquitectura multiagente.
- Preparar una discusión de inversión.
- Organizar argumentos.
- Identificar información faltante.
- Comparar alternativas de forma estructurada.
- Analizar posibles impactos.
- Mejorar la trazabilidad del racional.
- Mostrar el potencial de una solución futura.

El prototipo no debe utilizarse para:

- Tomar decisiones reales sin revisión.
- Sustituir validaciones oficiales.
- Automatizar recomendaciones.
- Ejecutar órdenes.
- Presentar métricas simuladas como reales.
- Omitir procesos internos de control.

---

## 17. Frase estándar de advertencia

Cuando proceda, los agentes deberán incluir una advertencia como la siguiente:

```markdown
Este análisis forma parte de un prototipo de InvestCopilot y puede utilizar datos parciales, simplificados o simulados. No constituye una recomendación de inversión ni una validación operativa definitiva. La decisión final debe ser revisada por el gestor o por el órgano de decisión correspondiente.
```

---

## 18. Checklist de limitaciones antes de emitir una respuesta

Antes de responder, cada agente debe comprobar:

- ¿Los datos utilizados son reales, simulados o mixtos?
- ¿He indicado si los datos son incompletos?
- ¿He evitado presentar una estimación como dato oficial?
- ¿He señalado los supuestos utilizados?
- ¿He identificado la información faltante?
- ¿He limitado mi conclusión a mi ámbito?
- ¿He evitado emitir una recomendación automática?
- ¿He dejado claro que la decisión final es humana?
- ¿He marcado riesgos relevantes?
- ¿La respuesta puede ser revisada y trazada?

---

## 19. Mensaje final

Las limitaciones del prototipo no reducen su valor; al contrario, ayudan a utilizarlo correctamente.

InvestCopilot debe demostrar que la inteligencia artificial puede aportar estructura, velocidad y trazabilidad al análisis de decisiones de inversión, siempre bajo supervisión humana y con una separación clara entre análisis y decisión.

El objetivo del prototipo es aprender, validar la arquitectura y mostrar el potencial de una futura solución más completa, no sustituir los procesos profesionales de inversión.