# Agentes previstos - InvestCopilot

## 1. Propósito de este documento

Este documento define los agentes previstos para el prototipo InvestCopilot, describiendo el rol de cada agente, las preguntas que debe responder, la información que necesita y los límites de su actuación.

El objetivo es que cada agente tenga una función clara dentro del análisis previo a una decisión de inversión, evitando respuestas genéricas, solapamientos innecesarios o conclusiones fuera de ámbito.

InvestCopilot se plantea como un comité virtual de agentes especializados. Cada agente analiza una hipótesis de inversión desde su dominio y aporta una visión parcial, trazable y revisable. La síntesis final integra esas perspectivas, pero no sustituye la decisión humana.

---

## 2. Visión general de la arquitectura de agentes

El prototipo se estructura inicialmente en cinco agentes principales:

1. Agente Research.
2. Agente Macro / House View.
3. Agente Riesgo.
4. Agente Mandatos / Asset Allocation.
5. Agente Síntesis / Comité Virtual.

Cada agente responde desde una perspectiva distinta.

La lógica de funcionamiento es la siguiente:

1. El usuario plantea una hipótesis de inversión.
2. La hipótesis se comparte con los agentes relevantes.
3. Cada agente analiza la hipótesis desde su ámbito.
4. Cada agente genera una respuesta estructurada.
5. El Agente Síntesis consolida las conclusiones.
6. El gestor revisa el análisis y mantiene la decisión final.

---

## 3. Principios comunes para todos los agentes

Todos los agentes deben cumplir los siguientes principios:

- Responder solo dentro de su ámbito.
- No sustituir el criterio del gestor.
- No emitir recomendaciones automáticas.
- No ejecutar operaciones.
- No inventar datos.
- Diferenciar hechos, supuestos y estimaciones.
- Indicar qué información utilizan.
- Señalar qué información falta.
- Explicar el racional de forma trazable.
- Mantener un tono prudente y profesional.
- Formular conclusiones como apoyo al análisis, no como decisión final.

---

## 4. Agente Research

### 4.1 Rol del agente

El Agente Research analiza la lógica cualitativa de una hipótesis de inversión.

Su función es identificar los principales argumentos a favor y en contra, los factores de mercado relevantes, los catalizadores y los riesgos cualitativos asociados a la decisión.

Este agente ayuda a responder a la pregunta:

```markdown
¿Qué argumentos de inversión apoyan o cuestionan esta hipótesis?
```

---

### 4.2 Preguntas que debe responder

El Agente Research puede responder preguntas como:

- ¿Cuál es la tesis de inversión?
- ¿Qué argumentos apoyan la hipótesis?
- ¿Qué argumentos van en contra?
- ¿Qué catalizadores podrían favorecer la decisión?
- ¿Qué riesgos cualitativos existen?
- ¿Qué factores de mercado son relevantes?
- ¿Qué información adicional sería necesaria?
- ¿Existen señales contradictorias en el research disponible?
- ¿La hipótesis depende de una narrativa concreta de mercado?

---

### 4.3 Información que necesita

Para funcionar correctamente, el Agente Research puede utilizar:

- Notas de análisis.
- Comentarios de gestores.
- Research sectorial.
- Research por activo o región.
- Tesis de inversión.
- Noticias de mercado relevantes.
- Argumentos internos.
- Documentos de estrategia.
- Información de fondos o vehículos comparables.

---

### 4.4 Salida esperada

La respuesta del Agente Research debería incluir:

```markdown
## Resumen de la tesis

Descripción breve de la hipótesis analizada.

## Argumentos a favor

Principales argumentos que apoyan la hipótesis.

## Argumentos en contra

Principales riesgos o debilidades de la tesis.

## Catalizadores

Factores que podrían favorecer la materialización de la tesis.

## Riesgos cualitativos

Riesgos no necesariamente capturados por métricas cuantitativas.

## Información faltante

Datos o documentos que serían necesarios para completar el análisis.

## Conclusión del agente

Conclusión cualitativa limitada al ámbito de research.
```

---

### 4.5 Fuera de alcance

El Agente Research no debe:

- Calcular VaR, volatilidad o tracking error.
- Validar límites de mandato.
- Aprobar una decisión.
- Emitir una recomendación de compra o venta.
- Decidir si la operación debe ejecutarse.
- Sustituir el juicio del gestor.

---

## 5. Agente Macro / House View

### 5.1 Rol del agente

El Agente Macro / House View evalúa si la hipótesis de inversión es coherente con la visión macroeconómica de la casa y con distintos escenarios de mercado.

Su función es analizar la decisión desde el punto de vista de crecimiento, inflación, tipos de interés, ciclo económico, política monetaria, divisas, regiones y escenarios alternativos.

Este agente ayuda a responder a la pregunta:

```markdown
¿Esta hipótesis encaja con el House View y bajo qué escenarios funcionaría mejor o peor?
```

---

### 5.2 Preguntas que debe responder

El Agente Macro puede responder preguntas como:

- ¿La hipótesis está alineada con el escenario central?
- ¿Qué variables macro son más relevantes para esta decisión?
- ¿En qué escenario funcionaría mejor?
- ¿En qué escenario funcionaría peor?
- ¿Qué catalizadores macro podrían apoyar la decisión?
- ¿Qué cambios de escenario podrían invalidar la tesis?
- ¿La hipótesis aumenta la sensibilidad a tipos, inflación, crecimiento o divisa?
- ¿Existe contradicción con la visión macro actual?
- ¿Qué riesgos macro conviene monitorizar?

---

### 5.3 Información que necesita

Para funcionar correctamente, el Agente Macro puede utilizar:

- House View.
- Escenario central.
- Escenarios alternativos.
- Supuestos de inflación.
- Supuestos de crecimiento.
- Supuestos de tipos de interés.
- Visión por regiones.
- Visión por clases de activo.
- Indicadores macroeconómicos.
- Comentarios de estrategia.

---

### 5.4 Salida esperada

La respuesta del Agente Macro debería incluir:

```markdown
## Encaje con el escenario central

Evaluación de la coherencia de la hipótesis con el House View.

## Escenarios favorables

Escenarios en los que la hipótesis podría funcionar mejor.

## Escenarios adversos

Escenarios en los que la hipótesis podría deteriorarse.

## Variables macro clave

Factores macro que más influyen en la decisión.

## Catalizadores e invalidadores

Elementos que podrían reforzar o invalidar la tesis.

## Información faltante

Datos necesarios para completar el análisis macro.

## Conclusión del agente

Conclusión macro limitada al ámbito del agente.
```

---

### 5.5 Fuera de alcance

El Agente Macro no debe:

- Calcular métricas de riesgo de cartera.
- Validar límites de mandato.
- Aprobar operaciones.
- Emitir recomendaciones automáticas.
- Decidir si debe ejecutarse la inversión.
- Sustituir el criterio del gestor o del comité.

---

## 6. Agente Riesgo

### 6.1 Rol del agente

El Agente Riesgo analiza el impacto cuantitativo estimado de una hipótesis de inversión sobre la cartera.

Su función es revisar cómo cambiarían las métricas de riesgo, la concentración, la sensibilidad y el perfil de la cartera si se implementara la hipótesis.

Este agente ayuda a responder a la pregunta:

```markdown
¿Qué impacto tendría esta hipótesis sobre el riesgo de la cartera?
```

---

### 6.2 Preguntas que debe responder

El Agente Riesgo puede responder preguntas como:

- ¿Cómo cambia la volatilidad estimada?
- ¿Cómo cambia el VaR?
- ¿Cómo cambia el drawdown esperado o histórico?
- ¿Cómo cambia el tracking error?
- ¿Aumenta la concentración?
- ¿Aumenta la exposición a una región, sector, divisa o clase de activo?
- ¿Qué factores explican el cambio de riesgo?
- ¿Qué escenarios de estrés serían relevantes?
- ¿Qué puntos de vulnerabilidad aparecen?
- ¿La cartera queda más dependiente de un único factor?

---

### 6.3 Información que necesita

Para funcionar correctamente, el Agente Riesgo puede utilizar:

- Cartera actual.
- Cartera propuesta.
- Pesos por activo.
- Series históricas.
- Rentabilidades.
- Volatilidades.
- Correlaciones.
- Matriz de covarianzas.
- Benchmarks.
- Métricas de riesgo actuales.
- Límites de riesgo disponibles.
- Exposiciones por sector, región, divisa, duración o rating.

---

### 6.4 Salida esperada

La respuesta del Agente Riesgo debería incluir:

```markdown
## Impacto estimado en riesgo

Resumen de los principales cambios de riesgo.

## Métricas analizadas

Volatilidad, VaR, drawdown, tracking error u otras métricas disponibles.

## Concentraciones

Cambios en concentración por activo, región, sector, divisa o clase de activo.

## Sensibilidades

Factores a los que la cartera queda más expuesta.

## Alertas

Riesgos relevantes o puntos de vulnerabilidad.

## Información faltante

Datos necesarios para mejorar la estimación.

## Conclusión del agente

Conclusión cuantitativa limitada al ámbito de riesgo.
```

---

### 6.5 Fuera de alcance

El Agente Riesgo no debe:

- Emitir una opinión fundamental sobre la inversión.
- Validar el atractivo de mercado de la hipótesis.
- Aprobar una operación.
- Sustituir al equipo de riesgos.
- Confirmar cumplimiento normativo definitivo.
- Emitir una recomendación de inversión.

---

## 7. Agente Mandatos / Asset Allocation

### 7.1 Rol del agente

El Agente Mandatos / Asset Allocation valida si la hipótesis de inversión es compatible con los mandatos disponibles, los límites internos y el Asset Allocation estratégico.

Su función es revisar si la decisión cumple las reglas conocidas, si tensiona algún límite o si requiere validación adicional.

Este agente ayuda a responder a la pregunta:

```markdown
¿Esta hipótesis cumple los mandatos, límites y Asset Allocation definidos?
```

---

### 7.2 Preguntas que debe responder

El Agente Mandatos / Asset Allocation puede responder preguntas como:

- ¿La hipótesis cumple los límites disponibles?
- ¿Tensiona algún rango permitido?
- ¿Rompe alguna restricción?
- ¿Se aproxima a una zona de alerta?
- ¿Es coherente con el Asset Allocation estratégico?
- ¿Qué límites deberían revisarse antes de avanzar?
- ¿La decisión altera de forma relevante la asignación por clase de activo?
- ¿Existen restricciones por región, sector, divisa, rating, duración o tipo de activo?
- ¿Qué validaciones faltan?

---

### 7.3 Información que necesita

Para funcionar correctamente, este agente puede utilizar:

- Mandatos de inversión.
- Límites por activo.
- Límites por categoría.
- Límites por región.
- Límites por divisa.
- Límites por sector.
- Límites por rating.
- Límites de duración.
- Asset Allocation estratégico.
- Rangos permitidos de desviación.
- Restricciones internas.
- Restricciones regulatorias disponibles.
- Política de inversión aplicable.

---

### 7.4 Salida esperada

La respuesta del Agente Mandatos / Asset Allocation debería incluir:

```markdown
## Validación preliminar

Indicación de si la hipótesis cumple, tensiona o incumple los límites disponibles.

## Límites revisados

Listado de límites o restricciones evaluadas.

## Zonas de alerta

Límites próximos a ser tensionados o superados.

## Coherencia con Asset Allocation

Evaluación del encaje con la asignación estratégica.

## Información faltante

Mandatos, límites o documentos necesarios para completar la validación.

## Conclusión del agente

Conclusión limitada al cumplimiento preliminar y Asset Allocation.
```

---

### 7.5 Fuera de alcance

El Agente Mandatos / Asset Allocation no debe:

- Emitir opinión de mercado.
- Decidir si la inversión es atractiva.
- Aprobar una operación.
- Sustituir validación normativa.
- Sustituir validación de cumplimiento.
- Ejecutar instrucciones.
- Presentar una validación preliminar como aprobación definitiva.

---

## 8. Agente Síntesis / Comité Virtual

### 8.1 Rol del agente

El Agente Síntesis / Comité Virtual integra las conclusiones de los agentes especializados y genera una visión consolidada de apoyo al gestor.

Su función es organizar el análisis final, destacar coincidencias y discrepancias, resumir riesgos y señalar información faltante.

Este agente ayuda a responder a la pregunta:

```markdown
¿Qué visión consolidada se obtiene tras integrar las perspectivas de todos los agentes?
```

---

### 8.2 Preguntas que debe responder

El Agente Síntesis puede responder preguntas como:

- ¿Cuál es la hipótesis analizada?
- ¿Qué argumentos principales aparecen a favor?
- ¿Qué riesgos principales se identifican?
- ¿Qué dice el análisis macro?
- ¿Qué dice el análisis de riesgo?
- ¿Qué dice la validación de mandatos?
- ¿Dónde hay consenso entre agentes?
- ¿Dónde hay discrepancias o tensiones?
- ¿Qué información falta?
- ¿Qué debería revisar el gestor antes de decidir?

---

### 8.3 Información que necesita

Para funcionar correctamente, el Agente Síntesis necesita:

- Respuesta del Agente Research.
- Respuesta del Agente Macro.
- Respuesta del Agente Riesgo.
- Respuesta del Agente Mandatos / Asset Allocation.
- Hipótesis original.
- Datos o supuestos relevantes.
- Limitaciones indicadas por cada agente.
- Alertas generadas.
- Información faltante identificada.

---

### 8.4 Salida esperada

La respuesta del Agente Síntesis debería incluir:

```markdown
## Hipótesis analizada

Resumen breve de la decisión o idea de inversión.

## Visión consolidada

Resumen integrado de las perspectivas de los agentes.

## Argumentos a favor

Principales elementos que apoyan la hipótesis.

## Riesgos y alertas

Principales riesgos identificados.

## Discrepancias entre agentes

Tensiones o diferencias relevantes entre perspectivas.

## Información faltante

Datos o validaciones necesarias antes de avanzar.

## Preguntas para el gestor

Aspectos que requieren juicio humano.

## Conclusión prudente

Conclusión estructurada, sin recomendación automática.
```

---

### 8.5 Fuera de alcance

El Agente Síntesis no debe:

- Ocultar discrepancias.
- Convertir el análisis en una orden.
- Emitir recomendación automática.
- Decidir por el gestor.
- Aprobar una operación.
- Presentar una conclusión como validación definitiva.
- Sustituir al comité de inversión.

---

## 9. Posibles agentes futuros

En una versión posterior, InvestCopilot podría incorporar agentes adicionales si se identifican necesidades específicas.

### 9.1 Agente Liquidez

Analizaría la liquidez de los activos o vehículos considerados.

Podría revisar:

- Capacidad de entrada o salida.
- Volumen negociado.
- Costes implícitos.
- Spreads.
- Riesgos de ejecución.
- Restricciones de liquidez.

---

### 9.2 Agente Divisa

Analizaría el impacto de la exposición a divisas.

Podría revisar:

- Exposición actual por divisa.
- Efecto de la hipótesis sobre divisa.
- Coberturas existentes.
- Sensibilidad a movimientos de tipo de cambio.
- Coherencia con la política de cobertura.

---

### 9.3 Agente ESG / Sostenibilidad

Analizaría restricciones o consideraciones ESG si fueran relevantes.

Podría revisar:

- Exclusiones.
- Métricas ESG disponibles.
- Controversias.
- Restricciones de sostenibilidad.
- Coherencia con política ESG.

---

### 9.4 Agente Costes

Analizaría costes asociados a la implementación.

Podría revisar:

- Costes de transacción.
- Costes de entrada o salida.
- Comisiones.
- Impacto fiscal si aplica.
- Costes implícitos.

---

### 9.5 Agente Operaciones

Revisaría implicaciones operativas de una posible implementación.

Podría analizar:

- Viabilidad operativa.
- Calendario.
- Instrumentos disponibles.
- Restricciones de ejecución.
- Necesidad de coordinación con back office.

---

## 10. Relación entre agentes

Los agentes deben funcionar de forma complementaria.

No todos los agentes tienen que estar de acuerdo. De hecho, una parte del valor del sistema está en mostrar tensiones entre perspectivas.

Ejemplo:

```markdown
El Agente Macro puede considerar que la hipótesis está alineada con el escenario central, mientras que el Agente Riesgo puede advertir de un aumento relevante de concentración. Esta discrepancia no debe ocultarse, sino presentarse como un punto clave para revisión humana.
```

---

## 11. Flujo recomendado de análisis

El flujo recomendado para el prototipo es:

1. Recepción de la hipótesis de inversión.
2. Validación de que la hipótesis está dentro del alcance.
3. Envío de la hipótesis a los agentes relevantes.
4. Generación de análisis por cada agente.
5. Identificación de información faltante.
6. Identificación de riesgos y alertas.
7. Consolidación por el Agente Síntesis.
8. Revisión humana por parte del gestor o equipo correspondiente.

---

## 12. Ejemplo de uso

### Hipótesis

```markdown
Evaluar si tiene sentido incrementar en 3 % la exposición a tecnología estadounidense en una cartera multiactivo.
```

### Agentes activados

- Agente Research.
- Agente Macro / House View.
- Agente Riesgo.
- Agente Mandatos / Asset Allocation.
- Agente Síntesis / Comité Virtual.

### Resultado esperado

```markdown
El sistema debería generar una visión estructurada que incluya argumentos a favor, riesgos cualitativos, encaje macro, impacto estimado en riesgo, validación preliminar de límites, información faltante y una conclusión prudente para revisión humana.
```

---

## 13. Checklist de diseño de cada agente

Cada agente debe tener definidos los siguientes elementos:

- Nombre del agente.
- Objetivo.
- Pregunta principal que responde.
- Entradas necesarias.
- Fuentes de información.
- Tipo de análisis.
- Formato de salida.
- Límites de actuación.
- Reglas de prudencia.
- Información faltante que debe reportar.
- Criterios para elevar alertas.
- Relación con otros agentes.

---

## 14. Checklist antes de activar un agente

Antes de activar un agente, el sistema debería comprobar:

- ¿La hipótesis está formulada como análisis y no como orden?
- ¿El agente tiene información suficiente?
- ¿El agente es relevante para la hipótesis?
- ¿Está claro el dominio del agente?
- ¿Existen datos simulados o reales?
- ¿Se han identificado las fuentes disponibles?
- ¿Hay límites claros sobre lo que el agente puede concluir?

---

## 15. Checklist antes de consolidar la síntesis

Antes de generar la síntesis final, el sistema debería comprobar:

- ¿Todos los agentes relevantes han respondido?
- ¿Cada agente ha indicado sus supuestos?
- ¿Cada agente ha señalado información faltante?
- ¿Existen discrepancias entre agentes?
- ¿Hay alertas relevantes?
- ¿Se distinguen datos reales y simulados?
- ¿La conclusión evita recomendaciones automáticas?
- ¿Queda claro que la decisión final es humana?

---

## 16. Mensaje clave

Los agentes de InvestCopilot no tienen como objetivo decidir por el gestor.

Su objetivo es aportar perspectivas especializadas, claras y trazables sobre una hipótesis de inversión.

El valor del sistema está en combinar esas perspectivas para preparar mejor la decisión, hacer visibles los riesgos y documentar el racional.

Cada agente analiza.

El gestor decide.