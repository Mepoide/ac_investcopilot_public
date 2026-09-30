# Alcance y no alcance - InvestCopilot

## 1. Propósito de este documento

Este documento define el alcance y el no alcance del prototipo InvestCopilot.

Su objetivo es dejar claro qué puede hacer el prototipo, qué no debe hacer y cuáles son los límites funcionales, operativos y de responsabilidad que deben respetarse durante su desarrollo y uso.

InvestCopilot debe entenderse como una herramienta de apoyo al análisis previo de decisiones de inversión, no como un sistema que toma decisiones, ejecuta operaciones o sustituye el criterio profesional del gestor.

---

## 2. Alcance general del prototipo

El prototipo de InvestCopilot tiene como alcance demostrar cómo una arquitectura multiagente puede ayudar a estructurar el análisis de una hipótesis de inversión.

El sistema debe ser capaz de recibir una idea o decisión preliminar y analizarla desde distintas perspectivas complementarias:

- Research.
- Macro / House View.
- Riesgo.
- Mandatos.
- Asset Allocation.
- Síntesis final.

El objetivo es mostrar cómo cada agente puede aportar una visión especializada y cómo la combinación de esas visiones puede ayudar al gestor a preparar mejor una decisión.

---

## 3. Qué sí está dentro del alcance

InvestCopilot sí puede utilizarse para:

- Analizar hipótesis de inversión.
- Ordenar información relevante para una decisión.
- Identificar argumentos a favor y en contra.
- Evaluar el encaje de una decisión con el House View.
- Revisar posibles impactos sobre riesgo y concentración.
- Contrastar una hipótesis con mandatos y límites definidos.
- Evaluar coherencia con el Asset Allocation estratégico.
- Comparar alternativas de decisión.
- Identificar riesgos, trade-offs y puntos de atención.
- Detectar información faltante.
- Generar una síntesis estructurada para el gestor o comité.
- Documentar el racional de análisis.
- Mejorar la trazabilidad del proceso previo a la decisión.
- Servir como demostrador conceptual de una solución multiagente aplicada a inversiones.

---

## 4. Qué no está dentro del alcance

InvestCopilot no debe utilizarse para:

- Ejecutar operaciones.
- Enviar órdenes al mercado.
- Comprar o vender activos.
- Automatizar decisiones de inversión.
- Sustituir al gestor.
- Sustituir al comité de inversión.
- Emitir recomendaciones automáticas.
- Validar definitivamente una decisión.
- Aprobar operaciones.
- Sustituir procesos internos de control.
- Sustituir validaciones de riesgos, cumplimiento normativo u operaciones.
- Actuar como fuente única de verdad.
- Presentar datos simulados como datos reales.
- Eliminar la necesidad de revisión humana.

---

## 5. Alcance funcional

Desde el punto de vista funcional, el prototipo debe cubrir los siguientes bloques.

### 5.1 Entrada de una hipótesis de inversión

El usuario podrá introducir una hipótesis de análisis, por ejemplo:

- Incrementar exposición a tecnología estadounidense.
- Reducir duración en renta fija.
- Aumentar exposición a crédito investment grade.
- Reducir exposición a mercados emergentes.
- Comparar dos alternativas de cartera.
- Evaluar una propuesta frente al Asset Allocation estratégico.

La hipótesis debe formularse como una pregunta de análisis, no como una orden de ejecución.

Ejemplo correcto:

```markdown
Evaluar si tiene sentido incrementar en 3 % la exposición a tecnología estadounidense en una cartera multiactivo.
```

Ejemplo incorrecto:

```markdown
Comprar tecnología estadounidense hasta subir la exposición un 3 %.
```

---

### 5.2 Análisis por agentes especializados

El sistema debe permitir que distintos agentes analicen la hipótesis desde su ámbito específico.

Cada agente debe limitarse a su dominio y evitar conclusiones que correspondan a otros agentes.

Por ejemplo:

- El Agente Research analiza tesis y argumentos.
- El Agente Macro analiza coherencia con el House View.
- El Agente Riesgo analiza impacto cuantitativo.
- El Agente Mandatos valida límites y restricciones.
- El Agente Síntesis consolida las conclusiones.

---

### 5.3 Identificación de riesgos y trade-offs

El prototipo debe ayudar a hacer visibles los principales riesgos y compensaciones asociados a una hipótesis de inversión.

Puede identificar, entre otros:

- Riesgo de concentración.
- Aumento de volatilidad.
- Incremento de VaR.
- Mayor exposición a una región, sector o divisa.
- Riesgo de incumplimiento de límites.
- Desalineación con el House View.
- Dependencia de determinados escenarios macro.
- Falta de información suficiente para concluir.

---

### 5.4 Validación preliminar de mandatos y límites

El prototipo puede realizar validaciones preliminares frente a límites o reglas disponibles.

Puede indicar si una hipótesis:

- Cumple.
- Cumple pero tensiona algún límite.
- Se aproxima a una zona de alerta.
- No cumple con una restricción conocida.
- Requiere validación adicional.

Esta validación no debe interpretarse como una aprobación definitiva.

---

### 5.5 Síntesis final

El prototipo debe generar una síntesis final que integre las perspectivas de los agentes.

La síntesis puede incluir:

- Resumen de la hipótesis.
- Análisis de cada agente.
- Puntos de acuerdo.
- Puntos de tensión.
- Riesgos principales.
- Información faltante.
- Alertas relevantes.
- Preguntas pendientes.
- Conclusión prudente y no automática.

La síntesis debe ser útil para preparar una conversación de inversión, pero no debe convertirse en una recomendación de inversión.

---

## 6. Alcance de datos

El prototipo puede trabajar con diferentes tipos de datos, siempre que se identifique claramente su naturaleza.

### 6.1 Datos reales

Pueden utilizarse datos reales si están disponibles y son adecuados para el prototipo.

Ejemplos:

- Carteras reales o de referencia.
- Series históricas.
- Datos de fondos.
- Benchmarks.
- Mandatos.
- Límites.
- Documentos de estrategia.
- Documentos de research.
- House View.

Cuando se utilicen datos reales, debe indicarse la fuente y la fecha si están disponibles.

---

### 6.2 Datos simplificados

Pueden utilizarse datos simplificados para facilitar la demostración.

Ejemplos:

- Carteras reducidas.
- Universo limitado de fondos.
- Escenarios macro resumidos.
- Rangos de mandato simplificados.
- Métricas de riesgo calculadas de forma aproximada.

Los datos simplificados deben identificarse como tales.

---

### 6.3 Datos simulados

Pueden utilizarse datos simulados cuando no exista información real disponible o cuando sea necesario construir un caso demostrativo.

Ejemplos:

- Escenarios macro ficticios.
- Carteras ejemplo.
- Límites inventados para la demo.
- Métricas calculadas sobre datos generados.
- Tesis de inversión creadas para el prototipo.

Los datos simulados nunca deben presentarse como datos reales.

Cuando se utilicen, debe incluirse una advertencia como:

```markdown
Este análisis utiliza datos simulados con fines demostrativos. No debe utilizarse como base para una decisión real de inversión.
```

---

## 7. Alcance por agente

### 7.1 Agente Research

Dentro del alcance:

- Analizar tesis de inversión.
- Identificar argumentos a favor y en contra.
- Resumir research disponible.
- Detectar catalizadores.
- Identificar riesgos cualitativos.
- Señalar información faltante.

Fuera del alcance:

- Calcular métricas de riesgo.
- Validar límites de mandato.
- Emitir recomendaciones de compra o venta.
- Sustituir el juicio del gestor.

---

### 7.2 Agente Macro / House View

Dentro del alcance:

- Evaluar coherencia con el escenario central.
- Analizar sensibilidad a escenarios alternativos.
- Identificar variables macro relevantes.
- Señalar catalizadores macro.
- Detectar posibles contradicciones con la visión de la casa.

Fuera del alcance:

- Validar límites de cartera.
- Evaluar cumplimiento normativo.
- Calcular métricas de riesgo.
- Decidir si una operación debe ejecutarse.

---

### 7.3 Agente Riesgo

Dentro del alcance:

- Estimar impacto en volatilidad.
- Estimar impacto en VaR.
- Analizar drawdowns.
- Evaluar tracking error.
- Medir concentración.
- Analizar sensibilidad por activo, sector, región o divisa.
- Identificar puntos de vulnerabilidad.

Fuera del alcance:

- Emitir opinión macro.
- Decidir si una tesis de inversión es atractiva.
- Aprobar operaciones.
- Sustituir al equipo de riesgos.

---

### 7.4 Agente Mandatos / Asset Allocation

Dentro del alcance:

- Revisar límites disponibles.
- Evaluar rangos permitidos.
- Identificar incumplimientos preliminares.
- Detectar proximidad a límites.
- Analizar coherencia con el Asset Allocation estratégico.
- Señalar restricciones relevantes.

Fuera del alcance:

- Sustituir validación normativa oficial.
- Sustituir validación operativa.
- Emitir una recomendación de mercado.
- Aprobar la decisión de inversión.

---

### 7.5 Agente Síntesis / Comité Virtual

Dentro del alcance:

- Integrar conclusiones de otros agentes.
- Resumir argumentos clave.
- Identificar discrepancias.
- Mostrar tensiones entre perspectivas.
- Señalar información faltante.
- Preparar una visión de apoyo para el gestor.

Fuera del alcance:

- Ocultar discrepancias.
- Emitir una recomendación automática.
- Tomar una decisión final.
- Convertir el análisis en una orden de ejecución.

---

## 8. Alcance de las respuestas

Las respuestas generadas por InvestCopilot deben ser:

- Claras.
- Estructuradas.
- Trazables.
- Prudentes.
- Orientadas a análisis.
- Comprensibles para un gestor o comité.
- Limitadas al ámbito del agente.
- Explícitas respecto a datos utilizados y datos faltantes.

Las respuestas deben evitar:

- Lenguaje excesivamente categórico.
- Recomendaciones automáticas.
- Instrucciones de ejecución.
- Supuestos no declarados.
- Datos inventados presentados como reales.
- Conclusiones fuera del ámbito del agente.

---

## 9. No alcance operativo

InvestCopilot no tiene alcance operativo en esta fase.

Esto significa que no debe:

- Enviar órdenes.
- Conectarse a sistemas de ejecución.
- Modificar carteras reales.
- Registrar operaciones.
- Lanzar instrucciones a back office.
- Generar tickets operativos.
- Sustituir workflows internos.
- Activar procesos de contratación o suscripción.
- Actualizar sistemas oficiales.

El prototipo trabaja únicamente en el plano analítico y demostrativo.

---

## 10. No alcance regulatorio o normativo

InvestCopilot no sustituye validaciones regulatorias, normativas ni de cumplimiento.

El prototipo no debe considerarse una herramienta definitiva para validar:

- Idoneidad.
- Conveniencia.
- Cumplimiento normativo.
- Restricciones regulatorias.
- Límites legales.
- Documentación contractual.
- Políticas internas.
- Reglas específicas por producto.
- Restricciones comerciales o de distribución.

Cualquier aspecto regulatorio debe ser revisado por los equipos correspondientes.

---

## 11. No alcance de recomendación de inversión

InvestCopilot no debe emitir recomendaciones automáticas.

Debe evitar expresiones como:

- "Comprar".
- "Vender".
- "Ejecutar".
- "Debe incrementarse".
- "La decisión correcta es".
- "La mejor opción es".
- "Se recomienda operar".

Debe utilizar expresiones prudentes como:

- "Desde el punto de vista del análisis..."
- "Con la información disponible..."
- "La hipótesis parece..."
- "La decisión podría..."
- "Sería necesario validar..."
- "El principal riesgo identificado es..."
- "Queda pendiente revisar..."

---

## 12. No alcance de sustitución humana

InvestCopilot no sustituye:

- Al gestor de inversiones.
- Al comité de inversión.
- Al equipo de riesgos.
- Al equipo de cumplimiento.
- Al equipo de Asset Allocation.
- Al equipo de operaciones.
- A las fuentes oficiales de datos.
- A los procesos internos de aprobación.

La responsabilidad final de cualquier decisión permanece siempre en las personas y órganos establecidos.

---

## 13. Criterios para considerar una respuesta dentro de alcance

Una respuesta está dentro del alcance si:

- Analiza una hipótesis, no ejecuta una decisión.
- Se limita al dominio del agente.
- Explica los supuestos utilizados.
- Indica datos disponibles y faltantes.
- Identifica riesgos y trade-offs.
- No emite órdenes de inversión.
- No sustituye la decisión humana.
- Mantiene un tono prudente.
- Favorece la trazabilidad.
- Puede ser revisada por el gestor.

---

## 14. Criterios para considerar una respuesta fuera de alcance

Una respuesta está fuera de alcance si:

- Ordena comprar o vender.
- Presenta una conclusión como decisión automática.
- Oculta información faltante.
- Inventa datos y los presenta como reales.
- Valida definitivamente un mandato sin fuente suficiente.
- Sustituye al gestor o al comité.
- Emite una recomendación categórica.
- Mezcla dominios sin distinguirlos.
- Da una instrucción operativa.
- No permite trazar el racional.

---

## 15. Ejemplos de uso dentro de alcance

### Ejemplo 1

```markdown
Analizar el impacto de incrementar en 3 % la exposición a tecnología estadounidense en una cartera multiactivo.
```

Dentro de alcance porque se formula como análisis, no como orden.

---

### Ejemplo 2

```markdown
Evaluar si reducir duración en renta fija es coherente con el escenario macro actual.
```

Dentro de alcance porque pide una evaluación macro, no una ejecución.

---

### Ejemplo 3

```markdown
Comparar dos alternativas de cartera desde el punto de vista de riesgo, mandatos y House View.
```

Dentro de alcance porque solicita comparación estructurada.

---

## 16. Ejemplos fuera de alcance

### Ejemplo 1

```markdown
Comprar tecnología estadounidense hasta alcanzar un 10 % de la cartera.
```

Fuera de alcance porque es una instrucción de ejecución.

---

### Ejemplo 2

```markdown
Aprueba esta operación.
```

Fuera de alcance porque implica validación definitiva.

---

### Ejemplo 3

```markdown
Dime qué activo debo comprar.
```

Fuera de alcance porque pide una recomendación directa.

---

### Ejemplo 4

```markdown
Ejecuta la rotación de cartera.
```

Fuera de alcance porque implica acción operativa.

---

## 17. Relación entre análisis y decisión

InvestCopilot trabaja en la fase previa a la decisión.

Su función es ayudar a responder preguntas como:

- ¿Qué argumentos apoyan esta hipótesis?
- ¿Qué riesgos aparecen?
- ¿Qué impacto podría tener en cartera?
- ¿Encaja con el House View?
- ¿Cumple los límites disponibles?
- ¿Qué información falta?
- ¿Qué debería revisar el gestor antes de decidir?

No debe responder como si tuviera autoridad para decidir.

---

## 18. Nivel de madurez esperado

En esta fase, el prototipo no necesita estar conectado a todos los sistemas reales ni disponer de todos los datos definitivos.

Es aceptable que utilice:

- Datos de ejemplo.
- Datos simplificados.
- Datos simulados.
- Casos de uso predefinidos.
- Archivos preparados para la demo.
- Supuestos explícitos.

Lo importante es demostrar:

- La lógica de funcionamiento.
- La separación de agentes.
- La trazabilidad.
- La utilidad del análisis estructurado.
- La supervisión humana.
- El potencial del enfoque multiagente.

---

## 19. Mensaje clave

El alcance de InvestCopilot es apoyar, estructurar y documentar el análisis previo a una decisión de inversión.

El no alcance es decidir, recomendar automáticamente, ejecutar, aprobar o sustituir procesos humanos y controles internos.

InvestCopilot debe ayudar al gestor a analizar mejor, no decidir por él.