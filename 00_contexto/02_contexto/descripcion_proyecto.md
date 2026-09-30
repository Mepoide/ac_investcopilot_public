# Descripción del proyecto - InvestCopilot

## 1. Resumen ejecutivo

InvestCopilot es un prototipo de copiloto de decisión diseñado para apoyar a los gestores de inversión en el análisis previo a decisiones relevantes de cartera.

El proyecto nace con el objetivo de estructurar, acelerar y documentar mejor el proceso de análisis de inversión, integrando de forma ordenada información que normalmente se encuentra dispersa: research, visión macroeconómica, escenarios de mercado, análisis de riesgos, mandatos, restricciones de inversión y Asset Allocation estratégico.

InvestCopilot no pretende sustituir al gestor, automatizar decisiones ni ejecutar operaciones. Su función es actuar como un apoyo estructurado que ayuda a preparar mejor una decisión, identificar riesgos y trade-offs, comparar alternativas y dejar documentado el racional utilizado.

La decisión final permanece siempre bajo responsabilidad humana.

---

## 2. Contexto del proyecto

Las decisiones de inversión relevantes suelen requerir la combinación de múltiples fuentes de información en un periodo de tiempo limitado.

En la práctica, un gestor puede tener que considerar simultáneamente:

- La visión macroeconómica de la casa.
- El contexto de mercado.
- El research disponible.
- La composición actual de la cartera.
- Las métricas de riesgo.
- Las restricciones del mandato.
- El Asset Allocation estratégico.
- Las alternativas posibles.
- Los riesgos de concentración.
- Los impactos esperados sobre la cartera.

Este proceso puede ser complejo, fragmentado y dependiente de la disponibilidad de distintas personas, documentos o herramientas.

InvestCopilot busca ordenar ese proceso mediante una arquitectura basada en agentes especializados, cada uno centrado en un dominio concreto del análisis.

---

## 3. Problema que se quiere resolver

El proyecto intenta dar respuesta a varios problemas habituales en el análisis previo a decisiones de inversión:

- La información relevante puede estar dispersa en distintos documentos, sistemas o equipos.
- El análisis puede depender demasiado de procesos manuales o de conocimiento no documentado.
- Puede resultar difícil comparar alternativas de forma homogénea.
- Algunos riesgos o restricciones pueden no revisarse de forma sistemática.
- La trazabilidad del racional de inversión puede no quedar suficientemente documentada.
- El gestor puede necesitar coordinar distintas perspectivas en poco tiempo.
- La documentación final de la decisión puede ser incompleta o poco estructurada.

InvestCopilot no elimina la complejidad de la decisión, pero ayuda a organizarla.

---

## 4. Propuesta de solución

La propuesta consiste en desarrollar un copiloto de decisión basado en un sistema multiagente.

Cada agente analiza la hipótesis de inversión desde una perspectiva específica y aporta una respuesta especializada. Posteriormente, un agente de síntesis consolida las distintas perspectivas y prepara una visión final orientada al gestor o al comité.

El objetivo no es que un único modelo responda de forma genérica, sino que el análisis se divida por dominios:

- Research.
- Macro / House View.
- Riesgo.
- Mandatos y Asset Allocation.
- Síntesis final.

Esta separación permite que cada agente tenga un papel claro, reduzca el riesgo de respuestas fuera de ámbito y mejore la trazabilidad del análisis.

---

## 5. Objetivo del prototipo

El objetivo del prototipo es demostrar que InvestCopilot puede ayudar a estructurar una decisión de inversión de forma más rápida, ordenada y trazable.

En esta fase, el prototipo debe demostrar que es posible:

- Recibir una hipótesis de inversión como input.
- Activar agentes especializados por dominio.
- Analizar la decisión desde distintas perspectivas complementarias.
- Identificar argumentos a favor y en contra.
- Evaluar el encaje con el House View.
- Estimar impactos sobre métricas de riesgo.
- Revisar posibles tensiones con mandatos o límites.
- Generar una síntesis final clara y estructurada.
- Documentar el racional de la decisión.
- Mantener siempre la supervisión humana.

El prototipo no busca validar una solución operativa final, sino demostrar la arquitectura conceptual y el valor potencial del enfoque.

---

## 6. Qué es InvestCopilot

InvestCopilot es:

- Un copiloto de apoyo al análisis de inversión.
- Un sistema de ayuda a la decisión.
- Una arquitectura multiagente.
- Una herramienta para estructurar información.
- Una forma de documentar mejor el racional de inversión.
- Un apoyo para preparar comités o discusiones de inversión.
- Un mecanismo para hacer visibles riesgos, trade-offs y limitaciones.
- Una solución orientada a mejorar disciplina, trazabilidad y consistencia.

---

## 7. Qué no es InvestCopilot

InvestCopilot no es:

- Un sistema de trading automático.
- Un sistema de ejecución de operaciones.
- Un recomendador automático de compra o venta.
- Un sustituto del gestor de inversiones.
- Un sustituto del comité de inversión.
- Una herramienta que toma decisiones por sí sola.
- Una fuente única de verdad sobre mercado, riesgos o carteras.
- Una validación definitiva de cumplimiento, riesgo o idoneidad.
- Un sistema que elimina la necesidad de revisión humana.

Cualquier análisis generado por InvestCopilot debe considerarse apoyo al proceso de decisión, no una decisión en sí misma.

---

## 8. Agentes previstos

El prototipo puede estructurarse inicialmente en cinco agentes principales.

### 8.1 Agente Research

Su función es analizar la tesis de inversión desde un punto de vista cualitativo.

Puede identificar:

- Argumentos a favor.
- Argumentos en contra.
- Catalizadores.
- Riesgos cualitativos.
- Factores de mercado relevantes.
- Información adicional necesaria.

No debe validar límites, calcular riesgo ni emitir una decisión final.

---

### 8.2 Agente Macro / House View

Su función es evaluar la coherencia de la hipótesis con el escenario macroeconómico y la visión de la casa.

Puede analizar:

- Encaje con el escenario central.
- Sensibilidad a escenarios alternativos.
- Variables macro relevantes.
- Catalizadores macro.
- Riesgos de cambio de escenario.

No debe emitir una recomendación de inversión ni validar mandatos.

---

### 8.3 Agente Riesgo

Su función es analizar el impacto estimado de la decisión sobre la cartera.

Puede evaluar:

- Volatilidad.
- VaR.
- Drawdown.
- Tracking error.
- Concentración.
- Sensibilidad por activo, región, divisa o sector.
- Cambios en el perfil de riesgo.

Debe diferenciar claramente entre datos reales, supuestos y estimaciones.

---

### 8.4 Agente Mandatos / Asset Allocation

Su función es validar si la decisión es compatible con los mandatos vigentes, límites internos y Asset Allocation estratégico.

Puede analizar:

- Cumplimiento de rangos permitidos.
- Proximidad a límites.
- Restricciones por activo, región, divisa o categoría.
- Coherencia con la arquitectura de inversión.
- Posibles incumplimientos o zonas de alerta.

No debe valorar si una inversión es atractiva desde el punto de vista de mercado.

---

### 8.5 Agente Síntesis / Comité Virtual

Su función es integrar las conclusiones del resto de agentes y preparar una visión consolidada.

Debe presentar:

- Resumen de la decisión analizada.
- Principales argumentos a favor.
- Principales riesgos.
- Impacto estimado en cartera.
- Encaje macro.
- Validación de mandatos y límites.
- Información faltante.
- Puntos que requieren revisión humana.
- Conclusión estructurada, sin recomendación automática.

Este agente debe reflejar también las discrepancias entre agentes cuando existan.

---

## 9. Casos de uso iniciales

El prototipo puede probarse con hipótesis de inversión sencillas y representativas, por ejemplo:

- Incrementar exposición a tecnología estadounidense.
- Reducir duración en renta fija.
- Aumentar peso en crédito investment grade.
- Reducir exposición a emergentes.
- Comparar dos alternativas de cartera.
- Evaluar una propuesta frente al Asset Allocation estratégico.
- Analizar el impacto de una idea de inversión en riesgo y concentración.

Estos casos deben formularse como hipótesis de análisis, no como instrucciones de ejecución.

---

## 10. Valor esperado

InvestCopilot puede aportar valor en varios niveles.

### 10.1 Para el gestor

- Reduce tiempo de preparación.
- Ordena la información relevante.
- Hace visibles riesgos y trade-offs.
- Ayuda a comparar alternativas.
- Facilita una visión más completa antes de decidir.

### 10.2 Para el proceso de inversión

- Mejora la trazabilidad del análisis.
- Favorece la disciplina de inversión.
- Refuerza la revisión sistemática de mandatos y límites.
- Facilita la documentación del racional.
- Reduce dependencia de procesos informales o dispersos.

### 10.3 Para gobierno y control

- Refuerza la supervisión humana.
- Permite separar análisis y decisión.
- Ayuda a documentar supuestos y fuentes.
- Facilita la revisión posterior.
- Se alinea con un enfoque prudente de IA responsable.

---

## 11. Principios de IA responsable

InvestCopilot debe diseñarse y utilizarse bajo principios de IA responsable.

Los principios mínimos son:

- Supervisión humana.
- No sustitución del criterio profesional.
- No ejecución automática.
- Trazabilidad del análisis.
- Explicabilidad de las respuestas.
- Separación clara entre análisis y decisión.
- Uso prudente de datos.
- Identificación de información faltante.
- Claridad sobre supuestos y limitaciones.
- Revisión humana antes de cualquier actuación.

---

## 12. Limitaciones del prototipo

En esta fase, InvestCopilot es un prototipo y puede trabajar con datos parciales, simplificados o simulados.

Por tanto:

- Las conclusiones no deben interpretarse como recomendación de inversión.
- Los resultados cuantitativos pueden tener carácter ilustrativo.
- Los datos utilizados deben validarse antes de cualquier uso real.
- Los mandatos y límites deben revisarse con fuentes oficiales.
- El análisis macro puede estar basado en supuestos simplificados.
- La síntesis final no sustituye al gestor ni al comité.
- Cualquier decisión real debe seguir los procesos internos establecidos.

El objetivo del prototipo es demostrar el potencial de la arquitectura, no reemplazar procesos reales de inversión.

---

## 13. Funcionamiento esperado

El flujo conceptual del prototipo es el siguiente:

1. El usuario introduce una hipótesis de inversión.
2. El sistema identifica qué agentes deben participar.
3. Cada agente analiza la hipótesis desde su ámbito.
4. Cada agente devuelve una respuesta estructurada.
5. El agente de síntesis consolida los resultados.
6. La salida final muestra argumentos, riesgos, límites, discrepancias e información faltante.
7. El gestor revisa el análisis y mantiene la decisión final.

---

## 14. Ejemplo de hipótesis de entrada

```markdown
Hipótesis de inversión:
Evaluar si tiene sentido incrementar en 3 % la exposición a tecnología estadounidense en una cartera multiactivo.

Objetivo:
Analizar el encaje de la decisión con el House View, el impacto en riesgo y concentración, la compatibilidad con mandatos y los principales argumentos a favor y en contra.
```

---

## 15. Ejemplo de salida esperada

La salida final del prototipo debería incluir:

- Resumen de la hipótesis.
- Visión del Agente Research.
- Visión del Agente Macro.
- Visión del Agente Riesgo.
- Visión del Agente Mandatos.
- Principales puntos de acuerdo.
- Principales tensiones o discrepancias.
- Información faltante.
- Alertas relevantes.
- Conclusión prudente y no automática.
- Recordatorio de revisión humana.

---

## 16. Criterio de éxito del prototipo

El prototipo será útil si demuestra que puede:

- Ordenar el análisis de una decisión compleja.
- Separar correctamente las funciones de cada agente.
- Reducir la dispersión de información.
- Generar respuestas comprensibles y orientadas a comité.
- Hacer explícitos los riesgos y supuestos.
- Identificar información faltante.
- Mejorar la trazabilidad del racional.
- Mantener la decisión final bajo responsabilidad humana.

No será necesario que el prototipo esté conectado a todas las fuentes reales desde el primer momento. En esta fase es suficiente con demostrar la lógica de funcionamiento, la estructura de información y el valor del enfoque multiagente.

---

## 17. Mensaje clave

InvestCopilot es un apoyo estructurado al análisis de inversión.

No decide por el gestor, no ejecuta operaciones y no genera recomendaciones automáticas.

Su valor está en ayudar a analizar mejor, más rápido y con mayor trazabilidad, asegurando que las perspectivas clave —research, macro, riesgo, mandatos y Asset Allocation— estén presentes antes de tomar una decisión.

La decisión final siempre corresponde a una persona.