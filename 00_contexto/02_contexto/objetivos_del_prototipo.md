# Objetivos del prototipo - InvestCopilot

## 1. Propósito de este documento

Este documento define los objetivos del prototipo InvestCopilot.

Su finalidad es dejar claro qué queremos demostrar con esta primera versión, qué resultados esperamos obtener y qué criterios nos permitirán valorar si el prototipo aporta valor como copiloto de decisión para el análisis previo de inversiones.

El prototipo no busca ser una herramienta productiva definitiva, sino una demostración estructurada de cómo una arquitectura multiagente puede apoyar al gestor en la preparación, análisis y documentación de decisiones de inversión.

---

## 2. Objetivo principal

El objetivo principal del prototipo es demostrar que InvestCopilot puede ayudar a estructurar, acelerar y documentar el análisis previo a una decisión de inversión mediante agentes especializados.

InvestCopilot debe permitir analizar una hipótesis de inversión desde varias perspectivas complementarias:

- Research.
- Macro / House View.
- Riesgo.
- Mandatos.
- Asset Allocation.
- Síntesis final.

El valor del prototipo no está en decidir por el gestor, sino en ayudarle a analizar mejor, con mayor trazabilidad y manteniendo siempre la supervisión humana.

---

## 3. Objetivos específicos

Los objetivos específicos del prototipo son los siguientes.

### 3.1 Demostrar la lógica multiagente

El prototipo debe mostrar que una decisión de inversión puede analizarse mediante distintos agentes especializados, cada uno con un rol claro.

Cada agente debe aportar una visión concreta y limitada a su ámbito, evitando respuestas genéricas o fuera de dominio.

El sistema debe demostrar que la separación de funciones mejora la calidad, claridad y trazabilidad del análisis.

---

### 3.2 Analizar hipótesis de inversión

El prototipo debe ser capaz de recibir una hipótesis de inversión formulada por el usuario y convertirla en un análisis estructurado.

Ejemplos de hipótesis:

- Incrementar exposición a tecnología estadounidense.
- Reducir duración en renta fija.
- Aumentar exposición a crédito investment grade.
- Reducir exposición a mercados emergentes.
- Comparar dos alternativas de cartera.
- Evaluar una decisión frente al Asset Allocation estratégico.

La hipótesis debe tratarse como una idea a analizar, no como una orden de ejecución.

---

### 3.3 Integrar distintas perspectivas de análisis

El prototipo debe permitir que una misma hipótesis sea evaluada desde varios ángulos.

Por ejemplo:

- El Agente Research analiza argumentos a favor y en contra.
- El Agente Macro revisa el encaje con el House View.
- El Agente Riesgo estima impactos en métricas de cartera.
- El Agente Mandatos valida restricciones y límites disponibles.
- El Agente Síntesis consolida las conclusiones.

El objetivo es evitar que una decisión se analice desde una única perspectiva y favorecer una visión más completa.

---

### 3.4 Mejorar la trazabilidad del racional

Uno de los objetivos clave del prototipo es mejorar la trazabilidad del análisis.

Cada respuesta debe permitir entender:

- Qué hipótesis se ha analizado.
- Qué información se ha utilizado.
- Qué supuestos se han aplicado.
- Qué métricas se han considerado.
- Qué riesgos se han identificado.
- Qué información falta.
- Qué conclusión preliminar aporta cada agente.

El prototipo debe facilitar que el racional de inversión quede documentado de forma clara.

---

### 3.5 Identificar información faltante

El prototipo debe ayudar a detectar qué información sería necesaria para completar el análisis.

Esto puede incluir:

- Cartera actualizada.
- Series históricas.
- Benchmarks.
- Mandatos vigentes.
- Límites internos.
- House View actualizado.
- Escenarios macro.
- Research adicional.
- Datos de concentración.
- Métricas de riesgo.
- Restricciones regulatorias o comerciales.

Identificar información faltante es tan importante como generar conclusiones.

---

### 3.6 Hacer visibles riesgos y trade-offs

El prototipo debe ayudar a identificar los principales riesgos y compensaciones asociados a una hipótesis de inversión.

Puede señalar, entre otros:

- Mayor concentración.
- Incremento de volatilidad.
- Aumento de VaR.
- Aumento de tracking error.
- Dependencia de un escenario macro concreto.
- Tensión con límites internos.
- Posible desalineación con el Asset Allocation.
- Riesgo de liquidez.
- Riesgo de divisa.
- Riesgo sectorial o regional.
- Falta de información suficiente.

El objetivo es que el gestor vea de forma clara qué gana, qué asume y qué debe revisar.

---

### 3.7 Generar una síntesis orientada a comité

El prototipo debe ser capaz de generar una síntesis final útil para una conversación de inversión o comité.

La síntesis debe incluir:

- Resumen de la hipótesis.
- Principales argumentos a favor.
- Principales riesgos.
- Encaje macro.
- Impacto estimado en cartera.
- Validación preliminar de mandatos.
- Información faltante.
- Discrepancias entre agentes.
- Alertas relevantes.
- Conclusión prudente y no automática.

La síntesis debe ayudar a preparar la discusión, no sustituirla.

---

### 3.8 Reforzar la supervisión humana

El prototipo debe demostrar un uso responsable de la IA en decisiones de inversión.

Esto implica:

- No ejecutar operaciones.
- No emitir recomendaciones automáticas.
- No sustituir el criterio del gestor.
- No aprobar decisiones.
- No presentar análisis como verdad definitiva.
- Mantener la decisión final bajo responsabilidad humana.

Cada salida debe estar pensada como apoyo al análisis, no como decisión.

---

## 4. Objetivos funcionales

Desde el punto de vista funcional, el prototipo debería permitir:

1. Introducir una hipótesis de inversión.
2. Identificar qué agentes deben participar.
3. Ejecutar análisis por dominio.
4. Recoger respuestas estructuradas de cada agente.
5. Detectar riesgos, tensiones e información faltante.
6. Consolidar las respuestas en una síntesis final.
7. Mantener un registro trazable del análisis.
8. Diferenciar datos reales, simplificados y simulados.
9. Mostrar claramente las limitaciones del resultado.
10. Preparar una salida comprensible para gestor o comité.

---

## 5. Objetivos de datos

El prototipo debe demostrar cómo se pueden organizar datos y documentos para que los agentes trabajen mejor.

Para ello, el proyecto debe estructurar información en bloques como:

- Contexto del proyecto.
- Input de decisión.
- House View y escenarios macro.
- Cartera y métricas de riesgo.
- Mandatos y Asset Allocation.
- Universo de inversión.
- Research y notas de mercado.
- Casos de uso de demostración.
- Outputs de agentes.
- Trazabilidad y gobierno.

El objetivo es que los agentes no trabajen con información desordenada, sino con carpetas y documentos preparados por dominio.

---

## 6. Objetivos de demostración

En la sesión de trabajo, el prototipo debería servir para demostrar una historia sencilla y potente:

1. El gestor plantea una hipótesis de inversión.
2. InvestCopilot interpreta la hipótesis como un caso de análisis.
3. Cada agente aporta una visión especializada.
4. El sistema identifica argumentos, riesgos y restricciones.
5. La síntesis final muestra una visión estructurada y trazable.
6. El gestor conserva la decisión final.

La demostración debe ser clara, entendible y orientada a negocio.

No es necesario que el prototipo tenga todos los datos reales desde el primer día. Es preferible tener un caso de uso bien construido, con datos organizados y una salida convincente.

---

## 7. Casos de uso iniciales recomendados

Para una primera versión, se recomiendan pocos casos de uso, pero bien definidos.

### Caso 1: Incrementar tecnología estadounidense

Hipótesis:

```markdown
Evaluar si tiene sentido incrementar en 3 % la exposición a tecnología estadounidense en una cartera multiactivo.
```

Este caso es útil porque permite activar todos los agentes:

- Research: argumentos a favor y en contra del sector.
- Macro: coherencia con escenario de crecimiento, tipos e inflación.
- Riesgo: impacto en concentración, volatilidad y drawdown.
- Mandatos: revisión de límites sectoriales, regionales o de renta variable.
- Síntesis: visión consolidada.

---

### Caso 2: Reducir duración en renta fija

Hipótesis:

```markdown
Evaluar si tiene sentido reducir la duración de la cartera de renta fija ante un escenario de tipos más altos durante más tiempo.
```

Este caso permite probar:

- Sensibilidad a tipos.
- Riesgo de duración.
- Encaje macro.
- Impacto en rentabilidad esperada.
- Coherencia con Asset Allocation.
- Restricciones de mandato.

---

### Caso 3: Aumentar crédito investment grade

Hipótesis:

```markdown
Evaluar si tiene sentido aumentar exposición a crédito investment grade europeo frente a deuda pública.
```

Este caso permite analizar:

- Spreads.
- Riesgo de crédito.
- Liquidez.
- Encaje con escenario macro.
- Impacto en volatilidad y drawdown.
- Límites de rating o categoría.

---

## 8. Resultados esperados

Al finalizar el prototipo, deberíamos haber conseguido:

- Una estructura clara de carpetas y documentos.
- Un conjunto mínimo de datos por dominio.
- Un caso de uso demostrable.
- Agentes con roles diferenciados.
- Respuestas estructuradas por agente.
- Una síntesis final comprensible.
- Identificación de información faltante.
- Evidencia de trazabilidad.
- Claridad sobre limitaciones.
- Un relato sólido para explicar el valor de InvestCopilot.

---

## 9. Qué no se pretende conseguir en esta fase

En esta fase no se pretende:

- Construir una herramienta productiva completa.
- Conectarse a todos los sistemas corporativos.
- Automatizar decisiones reales.
- Ejecutar operaciones.
- Validar todos los mandatos oficiales.
- Sustituir procesos de riesgos o cumplimiento.
- Crear un motor definitivo de recomendaciones.
- Tener todos los datos reales y actualizados.
- Resolver todos los casos de uso posibles.
- Eliminar la revisión humana.

El objetivo es demostrar el concepto y aprender qué sería necesario para evolucionarlo.

---

## 10. Criterios de éxito

El prototipo puede considerarse exitoso si demuestra que:

- La hipótesis de inversión se entiende correctamente.
- Los agentes responden dentro de su ámbito.
- El análisis es claro y trazable.
- Se identifican riesgos relevantes.
- Se señalan datos faltantes.
- Se distinguen hechos, supuestos y estimaciones.
- La síntesis final es útil para un gestor.
- No se emiten recomendaciones automáticas.
- La decisión final permanece bajo responsabilidad humana.
- El enfoque multiagente aporta más claridad que una respuesta genérica.

---

## 11. Criterios de no éxito

El prototipo no cumpliría su objetivo si:

- Los agentes responden de forma genérica.
- Se mezclan dominios sin control.
- Se emiten recomendaciones automáticas.
- Se inventan datos.
- No se identifican limitaciones.
- La salida no es útil para el gestor.
- No queda claro qué información se ha usado.
- No se diferencian datos reales y simulados.
- El sistema parece decidir por sí mismo.
- La síntesis oculta riesgos o discrepancias.

---

## 12. Indicadores cualitativos de valor

Aunque esta fase no requiere métricas cuantitativas definitivas, sí se pueden observar indicadores cualitativos de valor:

- Mayor claridad en el análisis.
- Menor dispersión de información.
- Mejor documentación del racional.
- Mayor visibilidad de riesgos.
- Mejor separación entre análisis y decisión.
- Mayor facilidad para preparar una discusión de inversión.
- Mejor identificación de datos necesarios.
- Mayor consistencia entre casos de uso.
- Mayor alineamiento con principios de IA responsable.

---

## 13. Aprendizajes esperados

El prototipo también debe ayudarnos a aprender:

- Qué datos son imprescindibles.
- Qué datos pueden simularse inicialmente.
- Qué agentes aportan más valor.
- Qué preguntas hacen mejor los usuarios.
- Qué tipo de salida es más útil.
- Qué limitaciones aparecen con más frecuencia.
- Qué partes requieren validación humana.
- Qué conectores o fuentes serían necesarios en una versión futura.
- Qué estructura documental facilita mejor el trabajo de los agentes.

---

## 14. Evolución futura

Si el prototipo resulta útil, podría evolucionar hacia una solución más completa incorporando:

- Conexión con fuentes oficiales de cartera.
- Carga automática de series históricas.
- Integración con sistemas de riesgo.
- Reglas de mandato parametrizadas.
- House View actualizado.
- Research estructurado.
- Control de versiones.
- Registro de decisiones.
- Auditoría de outputs.
- Interfaz de usuario para gestores.
- Flujos de revisión humana.

Estas posibles evoluciones deberán evaluarse de forma controlada y siempre manteniendo los principios de IA responsable.

---

## 15. Mensaje clave

El objetivo del prototipo InvestCopilot es demostrar que la IA puede aportar estructura, velocidad y trazabilidad al análisis previo de decisiones de inversión.

No se trata de automatizar la decisión.

Se trata de ayudar al gestor a analizar mejor, con más información organizada, más claridad sobre riesgos y una documentación más sólida del racional.

La IA ayuda a preparar la decisión.

La persona decide.