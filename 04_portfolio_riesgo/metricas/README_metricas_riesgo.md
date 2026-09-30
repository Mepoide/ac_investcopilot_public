# README métricas de riesgo - InvestCopilot

## 1. Propósito del documento

Este documento define las métricas de riesgo que se utilizarán en el prototipo InvestCopilot para analizar carteras, escenarios y decisiones de inversión.

Su objetivo es servir como guía para el Agente Riesgo, explicando qué métricas se calculan, cómo se interpretan, qué datos necesitan y qué limitaciones tienen.

Este documento no sustituye una metodología oficial de riesgos. Su finalidad es apoyar el prototipo y facilitar una lectura estructurada, prudente y trazable.

---

## 2. Alcance de las métricas

Las métricas descritas en este documento se utilizarán para analizar:

- La cartera real de Fondmapfre Bolsa América.
- La cartera modelo de Renta Variable USA.
- Escenarios de modificación de cartera, como el incremento de tecnología estadounidense en +3 p.p.
- Diferencias entre cartera actual y cartera propuesta.
- Concentración sectorial.
- Concentración por posición.
- Riesgo histórico estimado.
- Sensibilidad a sectores, estilos o temáticas.

Las métricas se calculan con datos históricos de precios y rentabilidades de los componentes disponibles.

---

## 3. Archivos de entrada necesarios

Para calcular métricas de riesgo, los archivos principales son:

```plaintext
04_portfolio_riesgo/
├── carteras/
│   ├── cartera_modelo_rv_usa.csv
│   ├── cartera_real_fondmapfre_bolsa_america.csv
│   ├── comparativa_modelo_vs_bam.csv
│   └── comparativa_modelo_vs_bam_pesos_sector.csv
│
├── metricas/
│   ├── resumen_riesgo_bam_vs_modelo.md
│   ├── escenario_tecnologia_plus3.md
│   ├── escenario_bam_tecnologia_plus3_pesos_sector.csv
│   └── escenario_bam_tecnologia_plus3_posiciones.csv
│
└── series_historicas/
    ├── mapping_isin_ticker_gics.csv
    ├── precios_bam_componentes.csv
    ├── rentabilidades_bam_componentes.csv
    ├── precios_bam_componentes_enriquecido.csv
    └── rentabilidades_bam_componentes_enriquecido.csv
```

Los archivos más relevantes para el cálculo cuantitativo son:

```plaintext
rentabilidades_bam_componentes_enriquecido.csv
cartera_real_fondmapfre_bolsa_america.csv
escenario_bam_tecnologia_plus3_posiciones.csv
mapping_isin_ticker_gics.csv
```

---

## 4. Principios generales de cálculo

Las métricas de riesgo deben calcularse siguiendo estos principios:

1. Utilizar rentabilidades, no precios, para métricas de riesgo.
2. Alinear fechas entre todos los activos.
3. Eliminar o tratar valores nulos de forma controlada.
4. Trabajar con pesos expresados en tanto por uno para cálculos matemáticos.
5. Documentar si se usan datos reales, estimados o simulados.
6. Distinguir métricas históricas de métricas prospectivas.
7. Evitar presentar resultados como oficiales si no han sido validados.
8. Indicar siempre el periodo de cálculo utilizado.
9. Indicar si la métrica está anualizada o no.
10. Mantener una interpretación prudente.

---

## 5. Rentabilidad diaria por activo

### Definición

La rentabilidad diaria mide la variación porcentual del precio de un activo entre dos fechas consecutivas.

### Fórmula

```markdown
retorno_diario_t = precio_t / precio_{t-1} - 1
```

### Uso en InvestCopilot

Se utiliza como base para calcular:

- Volatilidad.
- Correlaciones.
- Matriz de covarianzas.
- VaR histórico.
- Drawdown.
- Rentabilidad de cartera.
- Tracking error.

### Interpretación

Una rentabilidad diaria positiva indica subida del activo en la fecha correspondiente.  
Una rentabilidad diaria negativa indica caída del activo.

---

## 6. Rentabilidad diaria de cartera

### Definición

La rentabilidad diaria de cartera es la suma ponderada de las rentabilidades diarias de los activos que componen la cartera.

### Fórmula

```markdown
R_cartera_t = Σ peso_i × retorno_i,t
```

Donde:

```markdown
peso_i = peso del activo i en la cartera
retorno_i,t = rentabilidad del activo i en la fecha t
```

### Uso en InvestCopilot

Permite construir la serie histórica de rentabilidades de:

- BAM actual.
- Cartera modelo.
- Escenario tecnología +3 p.p.
- Cualquier cartera propuesta.

### Interpretación

Esta métrica permite comparar el comportamiento histórico estimado de distintas carteras bajo los pesos definidos.

---

## 7. Rentabilidad acumulada

### Definición

La rentabilidad acumulada muestra la evolución de una inversión a partir de una serie de rentabilidades.

### Fórmula

```markdown
Rentabilidad acumulada_t = Π(1 + R_cartera_t) - 1
```

También puede expresarse como índice base 100:

```markdown
Índice_t = 100 × Π(1 + R_cartera_t)
```

### Uso en InvestCopilot

Se utiliza para visualizar la evolución histórica de:

- Cartera actual.
- Cartera propuesta.
- Benchmark.
- Escenario alternativo.

### Interpretación

Permite observar periodos de subida, caídas acumuladas y recuperación posterior.

---

## 8. Volatilidad diaria

### Definición

La volatilidad diaria mide la variabilidad de las rentabilidades diarias.

### Fórmula

```markdown
volatilidad_diaria = desviación estándar de las rentabilidades diarias
```

### Uso en InvestCopilot

Sirve para comparar la variabilidad diaria de:

- Activos individuales.
- Sectores.
- Cartera actual.
- Cartera propuesta.
- Benchmark.

### Interpretación

Una volatilidad diaria más alta indica mayor variabilidad de los retornos diarios.

---

## 9. Volatilidad anualizada

### Definición

La volatilidad anualizada transforma la volatilidad diaria en una métrica anual comparable.

### Fórmula

```markdown
volatilidad_anualizada = volatilidad_diaria × sqrt(252)
```

Se utiliza 252 como aproximación del número de sesiones bursátiles en un año.

### Uso en InvestCopilot

Es una de las principales métricas para comparar el riesgo de distintas carteras o escenarios.

### Interpretación

Si el escenario tecnología +3 p.p. tiene una volatilidad anualizada superior a BAM actual, el escenario sería más volátil con los datos históricos utilizados.

---

## 10. Varianza de cartera

### Definición

La varianza de cartera mide el riesgo total considerando pesos, volatilidades y correlaciones entre activos.

### Fórmula matricial

```markdown
varianza_cartera = w' × Σ × w
```

Donde:

```markdown
w = vector de pesos
Σ = matriz de covarianzas de retornos
```

### Uso en InvestCopilot

Permite calcular la volatilidad de cartera teniendo en cuenta la relación entre activos.

### Interpretación

La varianza aumenta si:

- Aumentan los pesos en activos más volátiles.
- Aumentan las correlaciones entre activos.
- Aumenta la concentración en posiciones de alto riesgo.

---

## 11. Matriz de correlaciones

### Definición

La matriz de correlaciones mide cómo se mueven conjuntamente los activos.

### Rango

```markdown
-1 a +1
```

Interpretación:

- +1: movimiento perfectamente conjunto.
- 0: relación débil o inexistente.
- -1: movimiento perfectamente opuesto.

### Uso en InvestCopilot

Permite analizar:

- Diversificación.
- Concentraciones ocultas.
- Grupos de activos que se comportan parecido.
- Riesgo de que varias posiciones caigan a la vez.

### Interpretación

Si los activos tecnológicos tienen correlaciones altas entre sí, aumentar tecnología puede reducir la diversificación efectiva de la cartera.

---

## 12. Matriz de covarianzas

### Definición

La matriz de covarianzas combina volatilidad y correlación entre activos.

### Uso

Es necesaria para calcular:

- Varianza de cartera.
- Volatilidad de cartera.
- Contribución marginal al riesgo.
- Contribución porcentual al riesgo.

### Interpretación

Una matriz de covarianzas permite pasar de un análisis de pesos a un análisis de riesgo agregado.

---

## 13. VaR histórico

### Definición

El VaR histórico estima la pérdida potencial de una cartera a partir de la distribución histórica de sus rentabilidades.

### Fórmula conceptual

```markdown
VaR al 95 % = percentil 5 % de la distribución histórica de rentabilidades
```

Si se expresa como pérdida positiva:

```markdown
VaR 95 % = - percentil 5 % de retornos
```

### Uso en InvestCopilot

Permite comparar la pérdida histórica estimada entre:

- Cartera actual.
- Cartera modelo.
- Escenario tecnología +3 p.p.

### Interpretación

Un VaR mayor implica mayor pérdida histórica estimada para el nivel de confianza utilizado.

### Advertencia

El VaR histórico depende del periodo utilizado y no garantiza pérdidas futuras máximas.

---

## 14. VaR anualizado

### Definición

El VaR anualizado aproxima el VaR para un horizonte anual a partir del VaR diario.

### Fórmula simplificada

```markdown
VaR_anualizado = VaR_diario × sqrt(252)
```

### Uso en InvestCopilot

Permite expresar el riesgo en una escala anual comparable con otras métricas de cartera.

### Advertencia

La anualización por raíz de tiempo es una aproximación y asume condiciones simplificadas. Debe utilizarse con prudencia.

---

## 15. Drawdown

### Definición

El drawdown mide la caída desde un máximo histórico hasta un valor posterior inferior.

### Fórmula conceptual

```markdown
drawdown_t = índice_t / máximo_acumulado_t - 1
```

### Uso en InvestCopilot

Permite analizar la profundidad de las pérdidas históricas de una cartera o escenario.

### Interpretación

Un drawdown de -20 % significa que la cartera cayó un 20 % desde su máximo anterior.

---

## 16. Máximo drawdown

### Definición

El máximo drawdown es la mayor caída observada durante el periodo analizado.

### Uso en InvestCopilot

Sirve para comparar la severidad histórica de pérdidas entre:

- BAM actual.
- Escenario tecnología +3 p.p.
- Benchmark.

### Interpretación

Un máximo drawdown más negativo indica una pérdida histórica más profunda.

---

## 17. Tracking error

### Definición

El tracking error mide la volatilidad de la diferencia entre la rentabilidad de la cartera y la rentabilidad del benchmark.

### Fórmula

```markdown
tracking_error_diario = desviación estándar (R_cartera - R_benchmark)
tracking_error_anualizado = tracking_error_diario × sqrt(252)
```

### Uso en InvestCopilot

Permite evaluar cuánto se desvía BAM o un escenario respecto a su referencia.

### Interpretación

Un tracking error más alto indica mayor desviación frente al benchmark.

---

## 18. Beta frente a benchmark

### Definición

La beta mide la sensibilidad de la cartera frente a un benchmark.

### Fórmula

```markdown
beta = covarianza(R_cartera, R_benchmark) / varianza(R_benchmark)
```

### Uso en InvestCopilot

Permite estimar si la cartera es más o menos sensible que el benchmark.

### Interpretación

- Beta > 1: cartera más sensible que el benchmark.
- Beta < 1: cartera menos sensible que el benchmark.
- Beta cercana a 1: sensibilidad similar al benchmark.

---

## 19. Alpha histórico

### Definición

El alpha histórico mide la rentabilidad de la cartera no explicada por su beta frente al benchmark.

### Fórmula simplificada

```markdown
alpha = rentabilidad_cartera - beta × rentabilidad_benchmark
```

### Uso en InvestCopilot

Puede utilizarse como métrica complementaria, aunque no debe ser prioritaria en esta fase del prototipo.

### Advertencia

El alpha depende del benchmark, periodo y metodología utilizada.

---

## 20. Concentración por posición

### Definición

La concentración por posición mide cuánto pesa cada activo dentro de la cartera.

### Uso en InvestCopilot

Ayuda a identificar posiciones dominantes o fuentes relevantes de riesgo específico.

### Ejemplos de alerta

```markdown
Una posición supera el 5 % de la cartera.
Una posición explica una parte relevante del riesgo total.
Una posición aumenta significativamente en un escenario.
```

### Interpretación

Una alta concentración por posición puede aumentar el riesgo idiosincrático.

---

## 21. Concentración sectorial

### Definición

La concentración sectorial mide el peso agregado de una cartera por sector o grupo GICS.

### Uso en InvestCopilot

Es clave para analizar la hipótesis de incrementar tecnología estadounidense.

### Ejemplo

```markdown
Information Technology actual BAM: 41,10 %
Information Technology escenario +3 p.p.: 44,10 %
```

### Interpretación

Un aumento de concentración sectorial puede reducir la diversificación y aumentar la sensibilidad a factores comunes.

---

## 22. Concentración temática

### Definición

La concentración temática mide exposición a un tema que puede atravesar varios sectores.

Ejemplos:

- Inteligencia artificial.
- Semiconductores.
- Cloud.
- Ciberseguridad.
- Software.
- Pagos digitales.
- Tecnología defensiva.
- Tecnología cíclica.

### Uso en InvestCopilot

Es especialmente relevante porque algunas compañías clasificadas fuera de Information Technology pueden tener exposición económica a tecnología.

Ejemplos:

- Alphabet está clasificada como Communication Services.
- Amazon está clasificada como Retailing o Consumer Discretionary, pero tiene exposición relevante a cloud e inteligencia artificial.

### Interpretación

El análisis sectorial puede infraestimar o sobrestimar la exposición económica real a tecnología.

---

## 23. Contribución al riesgo

### Definición

La contribución al riesgo mide cuánto aporta cada activo, sector o bloque a la volatilidad total de la cartera.

### Uso en InvestCopilot

Permite distinguir entre:

- Activos con mucho peso.
- Activos con mucha volatilidad.
- Activos muy correlacionados.
- Activos que realmente explican el riesgo total.

### Interpretación

Una posición puede tener peso moderado pero alta contribución al riesgo si es volátil y está correlacionada con otros activos de riesgo.

---

## 24. Riesgo incremental del escenario

### Definición

El riesgo incremental mide cuánto cambia una métrica de riesgo al pasar de la cartera actual a una cartera propuesta.

### Fórmula conceptual

```markdown
riesgo_incremental = métrica_escenario - métrica_actual
```

Ejemplos:

```markdown
incremento_volatilidad = volatilidad_escenario - volatilidad_actual
incremento_VaR = VaR_escenario - VaR_actual
incremento_tracking_error = TE_escenario - TE_actual
```

### Uso en InvestCopilot

Permite evaluar el efecto de incrementar tecnología +3 p.p.

### Interpretación

Si el escenario aumenta volatilidad, VaR y concentración, el Agente Riesgo debe señalarlo como punto de atención.

---

## 25. Métricas mínimas para la demo

Para una primera versión del prototipo, las métricas mínimas recomendadas son:

```plaintext
1. Peso por sector.
2. Peso por posición.
3. Diferencia BAM vs cartera modelo.
4. Peso actual de Information Technology.
5. Peso escenario de Information Technology.
6. Volatilidad anualizada de BAM.
7. Volatilidad anualizada del escenario.
8. VaR histórico de BAM.
9. VaR histórico del escenario.
10. Máximo drawdown de BAM.
11. Máximo drawdown del escenario.
```

Si se dispone de benchmark:

```plaintext
12. Tracking error de BAM.
13. Tracking error del escenario.
14. Beta frente al benchmark.
```

---

## 26. Métricas avanzadas para fases posteriores

En una versión posterior podrían añadirse:

- Contribución al riesgo por activo.
- Contribución al riesgo por sector.
- Risk parity aproximado.
- Stress testing.
- Escenarios históricos.
- Sensibilidad a tipos reales.
- Sensibilidad a Nasdaq / growth.
- Exposición a factores.
- Análisis de liquidez.
- Análisis de divisa.
- Expected Shortfall.
- Marginal VaR.
- Component VaR.

Estas métricas no son imprescindibles para la primera demo.

---

## 27. Interpretación específica para tecnología +3 p.p.

Para el caso de uso:

```markdown
Incrementar tecnología estadounidense en +3 p.p. en BAM.
```

El Agente Riesgo debe revisar:

- Peso actual de Information Technology.
- Peso propuesto de Information Technology.
- Diferencia frente a la cartera modelo.
- Posiciones tecnológicas que más aumentan.
- Exposición a semiconductores.
- Exposición a software.
- Posiciones con mayor peso individual.
- Cambio de volatilidad.
- Cambio de VaR.
- Cambio de drawdown.
- Cambio de tracking error si hay benchmark.
- Reducción de sectores no tecnológicos.
- Pérdida de diversificación sectorial.

---

## 28. Advertencias metodológicas

Las métricas calculadas dentro del prototipo deben interpretarse con cautela.

Posibles limitaciones:

- Periodo histórico limitado.
- Datos faltantes.
- Tickers sin mapping completo.
- Cambios corporativos no ajustados.
- Pesos de cartera estáticos.
- No consideración de costes.
- No consideración de liquidez.
- No consideración de divisa si los precios están en USD y la cartera se evalúa en EUR.
- Benchmark pendiente de validación.
- Cálculos no validados por metodología oficial de riesgos.

---

## 29. Regla de comunicación del Agente Riesgo

El Agente Riesgo debe comunicar las métricas así:

```markdown
Con la información disponible y utilizando datos históricos del prototipo, la volatilidad anualizada estimada de la cartera actual es X %, frente a Y % en el escenario. Esto supone un incremento de Z p.p. La métrica debe interpretarse de forma preliminar y requiere validación con metodología oficial antes de cualquier decisión.
```

Debe evitar expresiones como:

```markdown
La cartera es segura.
La operación debe realizarse.
El riesgo es aceptable.
No hay riesgo.
```

---

## 30. Formato recomendado para salida del Agente Riesgo

```markdown
# Análisis del Agente Riesgo

## 1. Hipótesis analizada

## 2. Datos utilizados

## 3. Concentración sectorial

## 4. Concentración por posición

## 5. Métricas históricas calculadas

## 6. Comparativa cartera actual vs escenario

## 7. Alertas de riesgo

## 8. Información faltante

## 9. Conclusión prudente
```

---

## 31. Mensaje clave

Las métricas de riesgo no deciden por el gestor.

Su función es hacer visible cómo cambia el perfil de riesgo de una cartera ante una hipótesis de inversión.

En InvestCopilot, el Agente Riesgo debe aportar claridad, trazabilidad y prudencia.

La IA ayuda a analizar.

La persona decide.