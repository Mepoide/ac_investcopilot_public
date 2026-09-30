# Glosario de inversión - InvestCopilot

## 1. Propósito de este documento

Este documento recoge los principales términos de inversión, riesgo, Asset Allocation y análisis de carteras que pueden aparecer en el prototipo InvestCopilot.

Su objetivo es facilitar que los agentes utilicen un lenguaje homogéneo, claro y coherente al analizar hipótesis de inversión.

El glosario está pensado como material de contexto para el prototipo. No pretende sustituir definiciones oficiales, regulatorias o metodológicas, sino servir como referencia común para los agentes y usuarios.

---

## 2. Asset Allocation

El Asset Allocation es la distribución de una cartera entre distintas clases de activo, como renta variable, renta fija, liquidez, crédito, alternativos u otros bloques de inversión.

Puede definirse a distintos niveles:

- Estratégico.
- Táctico.
- Por clase de activo.
- Por región.
- Por divisa.
- Por sector.
- Por estilo de inversión.

En InvestCopilot, el Asset Allocation sirve como referencia para evaluar si una hipótesis de inversión encaja con la asignación objetivo o si genera desviaciones relevantes.

---

## 3. Asset Allocation estratégico

El Asset Allocation estratégico es la distribución de referencia de una cartera a medio o largo plazo.

Define la estructura objetivo que se considera adecuada para el perfil de inversión, mandato o política de inversión correspondiente.

En el prototipo, una decisión puede analizarse frente al Asset Allocation estratégico para comprobar si:

- Está alineada.
- Introduce una desviación táctica.
- Tensiona un rango permitido.
- Se aleja de la arquitectura objetivo.

---

## 4. Asset Allocation táctico

El Asset Allocation táctico recoge desviaciones temporales respecto al Asset Allocation estratégico.

Estas desviaciones suelen responder a una visión de mercado, oportunidades concretas o cambios en el entorno macroeconómico.

Ejemplo:

```markdown
Sobreponderar renta variable estadounidense frente al peso estratégico por considerar que el contexto de beneficios y crecimiento es favorable.
```

En InvestCopilot, una hipótesis táctica debe analizarse desde varias perspectivas: research, macro, riesgo, mandatos y límites.

---

## 5. Benchmark

Un benchmark es un índice o referencia frente a la cual se compara la evolución o composición de una cartera, fondo o estrategia.

Puede utilizarse para medir:

- Rentabilidad relativa.
- Tracking error.
- Beta.
- Desviaciones de cartera.
- Contribución relativa al riesgo.
- Coherencia con el mandato.

Ejemplo:

```markdown
Una cartera de renta variable europea puede compararse frente a un índice europeo como benchmark.
```

---

## 6. House View

El House View es la visión de mercado de la casa o entidad.

Suele recoger la opinión sobre:

- Crecimiento económico.
- Inflación.
- Tipos de interés.
- Política monetaria.
- Regiones.
- Clases de activo.
- Riesgos principales.
- Escenarios alternativos.

En InvestCopilot, el Agente Macro / House View evalúa si una hipótesis de inversión está alineada o no con esa visión.

---

## 7. Escenario central

El escenario central es la hipótesis macroeconómica considerada más probable o de referencia.

Puede incluir supuestos sobre:

- Crecimiento.
- Inflación.
- Tipos de interés.
- Beneficios empresariales.
- Mercado laboral.
- Política monetaria.
- Divisas.
- Riesgos geopolíticos.

Una hipótesis de inversión puede estar alineada con el escenario central, pero seguir siendo vulnerable a escenarios alternativos.

---

## 8. Escenario alternativo

Un escenario alternativo es una hipótesis distinta al escenario central.

Puede ser:

- Positivo.
- Negativo.
- De estrés.
- De recesión.
- De inflación persistente.
- De tipos más altos durante más tiempo.
- De desaceleración.
- De recuperación económica.

En InvestCopilot, los escenarios alternativos ayudan a analizar bajo qué condiciones una decisión funcionaría mejor o peor.

---

## 9. Escenario adverso

Un escenario adverso es una situación negativa para la cartera o para la hipótesis analizada.

Puede implicar:

- Caídas de mercado.
- Aumento de volatilidad.
- Ampliación de spreads.
- Subidas de tipos.
- Deterioro macroeconómico.
- Revisiones negativas de beneficios.
- Eventos geopolíticos.
- Problemas de liquidez.

El análisis de escenarios adversos ayuda a identificar vulnerabilidades.

---

## 10. Research

El research es el análisis cualitativo o cuantitativo utilizado para fundamentar una tesis de inversión.

Puede incluir:

- Análisis sectorial.
- Análisis por compañía.
- Análisis macro.
- Comentarios de mercado.
- Valoraciones.
- Riesgos.
- Catalizadores.
- Comparables.
- Recomendaciones internas o externas, si existen.

En InvestCopilot, el Agente Research no decide, sino que organiza los argumentos a favor y en contra de una hipótesis.

---

## 11. Tesis de inversión

La tesis de inversión es el razonamiento que justifica una hipótesis de inversión.

Debe explicar:

- Qué se quiere hacer.
- Por qué se plantea.
- Qué factores la apoyan.
- Qué riesgos existen.
- Qué condiciones deberían cumplirse.
- Qué podría invalidarla.

Ejemplo:

```markdown
Incrementar exposición a tecnología estadounidense porque se espera crecimiento sostenido de beneficios, aunque con riesgo de valoración elevada y concentración sectorial.
```

---

## 12. Catalizador

Un catalizador es un evento o factor que puede favorecer que una tesis de inversión se materialice.

Ejemplos:

- Mejora de beneficios.
- Bajada de tipos.
- Cambio regulatorio positivo.
- Reducción de inflación.
- Mejora de márgenes.
- Revisión positiva de expectativas.
- Flujo comprador hacia una clase de activo.

Los catalizadores ayudan a entender qué podría hacer que una hipótesis funcione.

---

## 13. Factor que invalida la tesis

Un factor que invalida la tesis es un evento o condición que debilita o contradice el razonamiento inicial de inversión.

Ejemplos:

- Deterioro macro.
- Subida inesperada de tipos.
- Caída de beneficios.
- Aumento de riesgo regulatorio.
- Incumplimiento de límites.
- Mayor concentración de la esperada.
- Cambio en el House View.
- Falta de liquidez.

InvestCopilot debe ayudar a identificar estos factores de forma explícita.

---

## 14. Mandato de inversión

El mandato de inversión define las reglas, objetivos y restricciones bajo las que se gestiona una cartera, fondo o vehículo.

Puede incluir:

- Objetivo de inversión.
- Universo permitido.
- Límites por activo.
- Límites por clase de activo.
- Límites por región.
- Límites por divisa.
- Límites por rating.
- Límites de duración.
- Restricciones regulatorias.
- Benchmarks.
- Rango de tracking error.
- Restricciones de liquidez.

En InvestCopilot, el Agente Mandatos / Asset Allocation revisa si una hipótesis es compatible con el mandato disponible.

---

## 15. Restricción de inversión

Una restricción de inversión es una regla que limita lo que puede hacerse en una cartera.

Puede ser:

- Interna.
- Regulatoria.
- Comercial.
- Operativa.
- Derivada del mandato.
- Derivada de política de riesgos.
- Derivada de criterios ESG.

Ejemplo:

```markdown
No superar un determinado porcentaje en una clase de activo, región, sector, emisor o rating.
```

---

## 16. Límite

Un límite es un umbral máximo o mínimo permitido para una determinada exposición, métrica o característica de cartera.

Ejemplos:

- Peso máximo en renta variable.
- Peso mínimo en liquidez.
- Duración máxima.
- Volatilidad máxima.
- Rating mínimo.
- Exposición máxima a divisa.
- Concentración máxima por emisor.
- Tracking error máximo.

En el prototipo, los límites pueden ser reales, simplificados o simulados, pero siempre deben identificarse correctamente.

---

## 17. Zona de alerta

Una zona de alerta es una situación en la que una métrica o exposición no incumple aún un límite, pero se aproxima a él.

Ejemplo:

```markdown
La exposición a renta variable se mantiene dentro del rango permitido, pero queda próxima al límite superior.
```

Las zonas de alerta deben mostrarse claramente porque pueden requerir revisión humana.

---

## 18. Cumple

Una hipótesis cumple cuando, con la información disponible, se mantiene dentro de los límites o restricciones aplicables.

En InvestCopilot, “cumple” debe entenderse como validación preliminar salvo que se haya comprobado contra fuentes oficiales completas.

---

## 19. Cumple tensionando

Una hipótesis cumple tensionando cuando no rompe un límite, pero se aproxima a él o reduce el margen disponible.

Ejemplo:

```markdown
La hipótesis no supera el límite de renta variable, pero deja la exposición muy próxima al máximo permitido.
```

Esta situación debe marcarse como punto de atención.

---

## 20. No cumple

Una hipótesis no cumple cuando supera un límite, contradice una restricción o no se ajusta al mandato disponible.

En ese caso, el agente debe indicar:

- Qué límite se incumple.
- Qué dato se ha utilizado.
- Qué validación adicional sería necesaria.
- Que el punto requiere revisión humana.

---

## 21. Cartera

Una cartera es el conjunto de activos, fondos, instrumentos o posiciones mantenidas dentro de una estrategia o vehículo de inversión.

Puede analizarse por:

- Peso por activo.
- Clase de activo.
- Región.
- Sector.
- Divisa.
- Rating.
- Duración.
- Liquidez.
- Riesgo.
- Rentabilidad.
- Contribución a resultados.

---

## 22. Cartera actual

La cartera actual es la composición vigente o de referencia antes de analizar una hipótesis.

Es necesaria para medir el impacto de una decisión.

Sin cartera actualizada, cualquier análisis de impacto debe considerarse preliminar.

---

## 23. Cartera propuesta

La cartera propuesta es la composición resultante si se implementara la hipótesis analizada.

Comparar cartera actual y cartera propuesta permite medir:

- Cambios de peso.
- Cambios de riesgo.
- Cambios de concentración.
- Cambios de exposición.
- Posibles tensiones con límites.
- Desviaciones frente al benchmark o Asset Allocation.

---

## 24. Peso

El peso es el porcentaje que representa un activo, fondo, clase de activo, región o sector dentro de una cartera.

Ejemplo:

```markdown
Si una cartera tiene un 10 % en tecnología estadounidense, ese es el peso de esa exposición dentro de la cartera.
```

---

## 25. Sobreponderación

Una sobreponderación se produce cuando una cartera tiene más peso en un activo, región, sector o clase de activo que su referencia, benchmark o nivel estratégico.

Ejemplo:

```markdown
Una cartera está sobreponderada en renta variable estadounidense si su peso es superior al definido en el Asset Allocation estratégico o benchmark.
```

---

## 26. Infraponderación

Una infraponderación se produce cuando una cartera tiene menos peso en un activo, región, sector o clase de activo que su referencia, benchmark o nivel estratégico.

Ejemplo:

```markdown
Una cartera está infraponderada en renta fija si su peso es inferior al definido como referencia.
```

---

## 27. Desviación

Una desviación es la diferencia entre el peso de una cartera y el peso de referencia.

Puede medirse frente a:

- Benchmark.
- Asset Allocation estratégico.
- Mandato.
- Cartera modelo.
- Peso anterior.

Ejemplo:

```markdown
Si el peso estratégico en renta variable es 40 % y la cartera tiene 45 %, la desviación es +5 puntos porcentuales.
```

---

## 28. Volatilidad

La volatilidad mide la variabilidad de las rentabilidades de un activo o cartera.

Suele utilizarse como medida de riesgo.

Una mayor volatilidad implica que las rentabilidades pueden fluctuar más, aunque no necesariamente implica pérdidas.

En InvestCopilot, el Agente Riesgo puede analizar si una hipótesis aumenta o reduce la volatilidad estimada.

---

## 29. VaR

El VaR, o Value at Risk, es una medida que estima la pérdida máxima esperada bajo ciertas condiciones, para un nivel de confianza y horizonte temporal determinados.

Ejemplo conceptual:

```markdown
Un VaR anual al 95 % intenta estimar una pérdida que no se superaría en el 95 % de los casos, según la metodología utilizada.
```

El VaR depende de:

- Periodo histórico.
- Nivel de confianza.
- Horizonte temporal.
- Distribución asumida.
- Metodología de cálculo.
- Calidad de los datos.

En el prototipo, cualquier VaR calculado con datos simulados debe considerarse ilustrativo.

---

## 30. Drawdown

El drawdown mide la caída desde un máximo hasta un mínimo posterior en el valor de una inversión o cartera.

Permite analizar pérdidas acumuladas durante periodos adversos.

Ejemplo:

```markdown
Si una cartera cae de 100 a 85, el drawdown es del -15 %.
```

El drawdown ayuda a entender la profundidad de las pérdidas en escenarios negativos.

---

## 31. Máximo drawdown

El máximo drawdown es la mayor caída observada desde un máximo hasta un mínimo durante un periodo determinado.

Es una medida relevante para evaluar pérdidas históricas severas.

En InvestCopilot, puede utilizarse para comparar el perfil de riesgo de distintas alternativas.

---

## 32. Tracking error

El tracking error mide la desviación de la rentabilidad de una cartera frente a su benchmark.

Un tracking error alto indica que la cartera se comporta de forma más diferente respecto a su referencia.

Puede ser deseado o no, dependiendo del mandato y del tipo de gestión.

---

## 33. Beta

La beta mide la sensibilidad de un activo o cartera frente a un mercado o benchmark.

Una beta superior a 1 indica mayor sensibilidad que el mercado de referencia.

Una beta inferior a 1 indica menor sensibilidad.

La beta debe interpretarse siempre respecto a un benchmark concreto.

---

## 34. Alpha

El alpha mide la rentabilidad adicional de una cartera o activo respecto a lo que cabría esperar dado su riesgo frente a un benchmark.

En términos simples, puede interpretarse como rentabilidad no explicada por la exposición al mercado, aunque depende de la metodología utilizada.

---

## 35. Correlación

La correlación mide el grado en que dos activos o series de rentabilidad se mueven conjuntamente.

Puede tomar valores entre -1 y 1.

- Correlación cercana a 1: se mueven de forma similar.
- Correlación cercana a 0: relación débil o inexistente.
- Correlación cercana a -1: se mueven en sentido contrario.

La correlación es clave para analizar diversificación.

---

## 36. Matriz de correlaciones

La matriz de correlaciones muestra la correlación entre varios activos, fondos o factores.

Permite identificar:

- Activos muy relacionados.
- Potenciales fuentes de diversificación.
- Concentraciones ocultas.
- Comportamientos similares entre fondos.

---

## 37. Concentración

La concentración mide cuánto peso tiene una cartera en determinados activos, sectores, regiones, emisores, divisas o factores.

Una cartera muy concentrada puede tener mayor sensibilidad a eventos específicos.

Ejemplos de concentración:

- Peso elevado en un sector.
- Peso elevado en una región.
- Peso elevado en pocos emisores.
- Peso elevado en una divisa.
- Peso elevado en un único factor de riesgo.

---

## 38. Diversificación

La diversificación consiste en repartir la inversión entre distintas fuentes de rentabilidad y riesgo.

Su objetivo es reducir la dependencia de un único activo, región, sector, emisor o escenario.

La diversificación no elimina el riesgo, pero puede ayudar a mejorar el perfil de la cartera.

---

## 39. Riesgo de mercado

El riesgo de mercado es el riesgo de pérdida derivado de movimientos en los precios de los activos financieros.

Puede estar relacionado con:

- Renta variable.
- Tipos de interés.
- Crédito.
- Divisas.
- Materias primas.
- Volatilidad.
- Liquidez.

---

## 40. Riesgo de tipos de interés

El riesgo de tipos de interés es el riesgo de que cambios en los tipos afecten al valor de los activos, especialmente instrumentos de renta fija.

Cuando suben los tipos, el precio de los bonos existentes suele verse presionado, aunque el impacto depende de la duración, cupón, vencimiento y otros factores.

---

## 41. Duración

La duración mide la sensibilidad aproximada del precio de un bono o cartera de bonos ante cambios en los tipos de interés.

Una duración mayor implica mayor sensibilidad a movimientos de tipos.

En InvestCopilot, una hipótesis como “reducir duración” debería ser analizada por el Agente Macro, el Agente Riesgo y el Agente Mandatos / Asset Allocation.

---

## 42. Riesgo de crédito

El riesgo de crédito es el riesgo de pérdida derivado de cambios en la calidad crediticia de un emisor o de un posible incumplimiento.

Puede manifestarse mediante:

- Impago.
- Rebaja de rating.
- Ampliación de spreads.
- Deterioro de fundamentales.
- Riesgo de concentración por emisor o sector.

---

## 43. Spread de crédito

El spread de crédito es la diferencia de rentabilidad entre un activo con riesgo de crédito y un activo considerado de referencia o menor riesgo.

Un aumento de spreads suele implicar deterioro de percepción de riesgo crediticio.

Una compresión de spreads suele reflejar mejora de apetito por riesgo o percepción de menor riesgo.

---

## 44. Rating

El rating es una calificación de calidad crediticia asignada a un emisor o instrumento por una agencia de rating o por una metodología interna.

Se utiliza para evaluar riesgo de crédito.

Puede influir en:

- Universo permitido.
- Límites de inversión.
- Riesgo de cartera.
- Coste de financiación.
- Mandatos.

---

## 45. Investment Grade

Investment Grade hace referencia a emisores o instrumentos con una calidad crediticia considerada relativamente alta según escalas de rating.

Suele tener menor riesgo de crédito que high yield, aunque no está libre de riesgo.

---

## 46. High Yield

High Yield hace referencia a emisores o instrumentos con menor calidad crediticia y mayor riesgo de crédito.

Suelen ofrecer mayor rentabilidad esperada para compensar el mayor riesgo.

También pueden presentar mayor volatilidad, riesgo de impago y sensibilidad a condiciones de liquidez.

---

## 47. Riesgo de liquidez

El riesgo de liquidez es el riesgo de no poder comprar o vender un activo en el momento deseado, en el volumen deseado o sin afectar significativamente al precio.

Puede ser relevante en activos menos líquidos, mercados tensionados o vehículos con restricciones de reembolso.

---

## 48. Riesgo de divisa

El riesgo de divisa es el riesgo derivado de movimientos en tipos de cambio.

Afecta a inversiones denominadas en monedas distintas a la divisa base de la cartera.

Puede estar cubierto o no cubierto, dependiendo de la política de inversión.

---

## 49. Cobertura de divisa

La cobertura de divisa busca reducir o neutralizar la exposición a movimientos de tipo de cambio.

Puede utilizar instrumentos derivados u otras estrategias.

En InvestCopilot, el impacto de divisa puede requerir un agente específico en futuras versiones.

---

## 50. Renta variable

La renta variable representa inversión en acciones o instrumentos similares.

Está asociada a participación en compañías y suele tener mayor riesgo y potencial de rentabilidad que activos más defensivos, aunque depende del mercado y periodo analizado.

Puede clasificarse por:

- Región.
- Sector.
- Capitalización.
- Estilo.
- Divisa.
- Factor.

---

## 51. Renta fija

La renta fija representa inversión en instrumentos de deuda, como bonos soberanos, corporativos u otros activos de crédito.

Sus riesgos incluyen:

- Tipos de interés.
- Crédito.
- Liquidez.
- Divisa.
- Duración.
- Inflación.

---

## 52. Crédito investment grade

El crédito investment grade es deuda emitida por entidades con calificación crediticia relativamente alta.

Puede ofrecer más rentabilidad que deuda pública, pero con mayor riesgo de crédito y sensibilidad a spreads.

---

## 53. Deuda pública

La deuda pública es deuda emitida por gobiernos o entidades públicas.

Suele utilizarse como componente defensivo o de referencia, aunque también tiene riesgos de tipos, inflación, divisa y crédito soberano.

---

## 54. Mercado emergente

Un mercado emergente es un mercado financiero o economía en desarrollo con características distintas a los mercados desarrollados.

Puede ofrecer mayor potencial de crecimiento, pero también mayores riesgos:

- Volatilidad.
- Divisa.
- Liquidez.
- Riesgo político.
- Riesgo regulatorio.
- Riesgo de gobernanza.

---

## 55. Tecnología estadounidense

La tecnología estadounidense se refiere a compañías del sector tecnológico cotizadas en Estados Unidos o con exposición relevante a ese mercado.

Puede incluir áreas como:

- Software.
- Semiconductores.
- Inteligencia artificial.
- Servicios digitales.
- Plataformas.
- Hardware.
- Infraestructura tecnológica.

Una hipótesis de aumento de exposición a tecnología estadounidense suele implicar revisar concentración sectorial, valoración, sensibilidad a tipos, beneficios y dependencia de grandes compañías.

---

## 56. Trade-off

Un trade-off es una compensación entre ventajas e inconvenientes.

En inversión, muchas decisiones implican aceptar un riesgo a cambio de un potencial beneficio.

Ejemplo:

```markdown
Aumentar renta variable puede mejorar el potencial de rentabilidad, pero también aumentar volatilidad y drawdown.
```

InvestCopilot debe hacer visibles estos trade-offs.

---

## 57. Racional de inversión

El racional de inversión es la explicación estructurada que justifica una hipótesis o decisión.

Debe incluir:

- Objetivo.
- Argumentos.
- Datos utilizados.
- Supuestos.
- Riesgos.
- Alternativas.
- Límites.
- Condiciones de validez.

Uno de los objetivos de InvestCopilot es mejorar la documentación del racional.

---

## 58. Hipótesis de inversión

Una hipótesis de inversión es una idea planteada para ser analizada.

No es una orden ni una decisión.

Ejemplo:

```markdown
Evaluar si tiene sentido aumentar exposición a crédito investment grade europeo frente a deuda pública.
```

InvestCopilot debe tratar siempre las entradas como hipótesis de análisis, no como instrucciones de ejecución.

---

## 59. Decisión de inversión

Una decisión de inversión es la determinación final adoptada por el gestor o por el órgano correspondiente, tras analizar la información disponible.

InvestCopilot puede apoyar el análisis previo, pero no debe tomar la decisión final.

---

## 60. Comité de inversión

Un comité de inversión es un órgano o reunión donde se analizan, discuten o validan decisiones de inversión.

InvestCopilot puede ayudar a preparar materiales, estructurar argumentos y documentar riesgos, pero no sustituye al comité.

---

## 61. Comité virtual

En el contexto de InvestCopilot, el comité virtual es la combinación de agentes especializados que analizan una hipótesis desde distintas perspectivas.

No es un órgano formal de decisión.

Es una arquitectura analítica para apoyar al gestor.

---

## 62. Agente

Un agente es un componente especializado del sistema que realiza una función concreta.

En InvestCopilot, cada agente tiene:

- Un dominio.
- Una pregunta principal.
- Fuentes de información.
- Reglas de respuesta.
- Límites de actuación.
- Formato de salida.

---

## 63. Agente Síntesis

El Agente Síntesis integra las respuestas de los agentes especializados y genera una visión consolidada.

Debe reflejar:

- Coincidencias.
- Discrepancias.
- Riesgos.
- Información faltante.
- Alertas.
- Preguntas para el gestor.

No debe emitir una recomendación automática.

---

## 64. Agente Macro

El Agente Macro evalúa la coherencia de una hipótesis con el House View, el escenario central y escenarios alternativos.

No debe calcular métricas de riesgo ni validar mandatos.

---

## 65. Agente Riesgo

El Agente Riesgo analiza el impacto cuantitativo de una hipótesis sobre la cartera.

Puede revisar volatilidad, VaR, drawdown, concentración, tracking error y sensibilidades.

No debe decidir si la inversión es atractiva desde el punto de vista fundamental.

---

## 66. Agente Mandatos

El Agente Mandatos revisa si una hipótesis cumple, tensiona o incumple límites y restricciones disponibles.

Su validación debe considerarse preliminar salvo que se base en fuentes oficiales completas y actualizadas.

---

## 67. Agente Research

El Agente Research analiza argumentos cualitativos, tesis de inversión, catalizadores y riesgos de mercado.

No debe validar límites ni calcular impacto cuantitativo salvo que esa información se le proporcione expresamente.

---

## 68. Datos simulados

Los datos simulados son datos creados para fines demostrativos.

No proceden necesariamente de fuentes reales.

Deben identificarse claramente.

Ejemplo de advertencia:

```markdown
Este análisis utiliza datos simulados con fines demostrativos. No debe utilizarse como base para una decisión real de inversión.
```

---

## 69. Datos simplificados

Los datos simplificados son datos reales o inventados que se reducen o adaptan para facilitar una demostración.

Ejemplo:

```markdown
Una cartera con solo diez activos para representar una cartera real más compleja.
```

Deben utilizarse con prudencia.

---

## 70. Fuente oficial

Una fuente oficial es una fuente validada y reconocida dentro del proceso correspondiente.

Puede incluir sistemas internos, documentos aprobados, informes validados o datos proporcionados por áreas responsables.

En el prototipo, si una fuente no es oficial, debe indicarse.

---

## 71. Información faltante

La información faltante es cualquier dato, documento, validación o contexto necesario para completar el análisis con mayor robustez.

Los agentes deben señalarla explícitamente.

Ejemplos:

- Falta cartera actualizada.
- Falta mandato vigente.
- Falta benchmark.
- Falta House View actualizado.
- Falta serie histórica.
- Faltan límites por activo.
- Falta confirmación de datos reales.

---

## 72. Alerta

Una alerta es una señal de atención que indica un riesgo, límite tensionado, información insuficiente o posible problema relevante.

Las alertas deben ser claras, visibles y revisables.

Ejemplo:

```markdown
Alerta: la hipótesis incrementa la exposición a un sector ya concentrado y requiere revisión adicional.
```

---

## 73. Revisión humana

La revisión humana es la evaluación posterior realizada por una persona cualificada.

En InvestCopilot, toda salida relevante debe poder ser revisada antes de utilizarse en una decisión real.

---

## 74. No recomendación automática

La no recomendación automática implica que InvestCopilot no debe presentar una salida como instrucción de inversión.

Debe evitar fórmulas como:

- Comprar.
- Vender.
- Ejecutar.
- La mejor opción es.
- Debe hacerse.

Debe utilizar fórmulas prudentes como:

- Con la información disponible.
- Esta hipótesis podría.
- Sería necesario validar.
- Desde el punto de vista de este agente.

---

## 75. No ejecución

La no ejecución implica que InvestCopilot no puede realizar operaciones ni enviar instrucciones operativas.

El sistema trabaja en la fase de análisis previo.

---

## 76. Trazabilidad

La trazabilidad es la capacidad de reconstruir cómo se ha llegado a una conclusión.

Incluye:

- Hipótesis analizada.
- Datos utilizados.
- Fuentes.
- Supuestos.
- Métricas.
- Límites.
- Respuestas de agentes.
- Síntesis final.
- Información faltante.

La trazabilidad es uno de los objetivos principales de InvestCopilot.

---

## 77. Explicabilidad

La explicabilidad es la capacidad de entender una respuesta, sus fundamentos y sus límites.

Una respuesta explicable debe ser clara, estructurada y comprensible para un gestor o comité.

---

## 78. Supervisión humana

La supervisión humana implica que una persona mantiene el control del proceso y revisa los resultados antes de cualquier uso relevante.

En InvestCopilot, la supervisión humana es obligatoria.

---

## 79. IA responsable

La IA responsable implica diseñar y utilizar sistemas de inteligencia artificial de forma prudente, transparente, controlada y alineada con principios de supervisión humana, trazabilidad, explicabilidad y no automatización de decisiones críticas.

En InvestCopilot, la IA responsable es un principio central del proyecto.

---

## 80. Mensaje clave

Este glosario debe ayudar a que los agentes de InvestCopilot utilicen un lenguaje común, claro y prudente.

El objetivo no es complicar el análisis, sino facilitar que todos los agentes entiendan los conceptos de la misma manera.

InvestCopilot analiza.

La persona decide.