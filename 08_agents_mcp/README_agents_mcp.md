# README Agents & MCP - InvestCopilot

## 1. Propósito de esta carpeta

Esta carpeta contiene la capa agentic del prototipo InvestCopilot.

Hasta ahora el proyecto tiene datos, documentos, scripts de cálculo y outputs generados para cada agente. Esta carpeta define cómo convertir esa base en una arquitectura de agentes conectados mediante herramientas MCP.

El objetivo es separar claramente:

- Conocimiento y datos del prototipo.
- Agentes especializados.
- Prompts de cada agente.
- Herramientas disponibles para los agentes.
- Servidor MCP.
- Orquestador del flujo de decisión.

Esta capa permite que InvestCopilot deje de ser solo una colección de archivos y scripts, y pase a comportarse como un flujo multiagente ejecutable.

---

## 2. Qué tenemos hasta ahora

El prototipo ya contiene las siguientes capas:

```plaintext
InvestCopilot_AI_Summit/
├── 00_contexto/
├── 01_decision_input/
├── 03_macro_houseview/
├── 04_portfolio_riesgo/
├── 05_mandatos_asset_allocation/
├── 06_sintesis_comite/
└── 07_demo_final/
```

Estas carpetas contienen:

- Contexto del proyecto.
- Reglas generales de respuesta.
- Hipótesis de decisión.
- House View base.
- Escenarios macro.
- Carteras.
- Benchmark.
- Series históricas.
- Métricas de riesgo.
- Outputs de agentes.
- Síntesis final.
- Materiales de demo.

Esta base ya permite explicar el caso DECISION_001, pero todavía no constituye por sí sola una arquitectura MCP.

---

## 3. Qué añade la carpeta 08_agents_mcp

La carpeta `08_agents_mcp` añade la capa de ejecución agentic.

Estructura propuesta:

```plaintext
08_agents_mcp/
├── README_agents_mcp.md
├── agents/
│   ├── macro_agent.py
│   ├── risk_agent.py
│   ├── mandates_agent.py
│   └── synthesis_agent.py
├── prompts/
│   ├── macro_agent_prompt.md
│   ├── risk_agent_prompt.md
│   ├── mandates_agent_prompt.md
│   └── synthesis_agent_prompt.md
├── mcp_server/
│   ├── server.py
│   ├── tools.py
│   └── mcp_config.json
└── orchestrator/
    └── run_decision_001.py
```

---

## 4. Objetivo de la arquitectura agentic

La arquitectura agentic debe permitir que una decisión se procese así:

```plaintext
1. El usuario plantea una hipótesis.
2. El orquestador lee decision_actual.json.
3. El Agente Macro analiza la hipótesis.
4. El Agente Riesgo analiza impacto en cartera.
5. El Agente Mandatos revisa benchmark y reglas de control.
6. El Agente Síntesis integra las conclusiones.
7. Se generan outputs .md y .json.
```

La idea es que cada agente tenga:

- Un prompt propio.
- Un ámbito de actuación.
- Un conjunto de herramientas.
- Unos inputs definidos.
- Un output esperado.
- Límites claros.

---

## 5. Principio clave

Los agentes no deben decidir.

Los agentes deben analizar.

El diseño debe mantener siempre esta regla:

```plaintext
InvestCopilot analiza.
La persona decide.
```

Por tanto, ningún agente debe:

- Emitir una recomendación automática.
- Decir que una operación debe ejecutarse.
- Aprobar una decisión.
- Validar oficialmente mandatos.
- Sustituir al gestor.
- Sustituir al equipo de riesgos.
- Sustituir al equipo de cumplimiento.

---

## 6. Agentes previstos

El prototipo tendrá inicialmente cuatro agentes:

```plaintext
macro_agent
risk_agent
mandates_agent
synthesis_agent
```

Cada agente corresponde a una perspectiva ya construida en las carpetas anteriores.

---

## 7. Agente Macro / House View

### Archivo previsto

```plaintext
08_agents_mcp/agents/macro_agent.py
```

### Prompt asociado

```plaintext
08_agents_mcp/prompts/macro_agent_prompt.md
```

### Objetivo

Analizar la hipótesis desde el punto de vista macro y House View.

### Inputs principales

```plaintext
01_decision_input/decision_actual.json
03_macro_houseview/house_view_base.md
03_macro_houseview/escenarios_macro.json
03_macro_houseview/indicadores_macro.csv
03_macro_houseview/supuestos_macro.json
03_macro_houseview/notas_macro/nota_tecnologia_usa.md
```

### Outputs esperados

```plaintext
03_macro_houseview/outputs_macro/DECISION_001_macro.md
03_macro_houseview/outputs_macro/DECISION_001_macro.json
```

### Preguntas que debe responder

- ¿La hipótesis está alineada con el escenario central?
- ¿Qué argumentos macro la apoyan?
- ¿Qué argumentos macro la cuestionan?
- ¿En qué escenarios funcionaría mejor?
- ¿En qué escenarios funcionaría peor?
- ¿Qué variables deben monitorizarse?
- ¿Qué información falta?

### Límites

El Agente Macro no debe:

- Calcular métricas de riesgo.
- Validar mandatos.
- Aprobar operaciones.
- Emitir recomendaciones de inversión.
- Sustituir el House View oficial.

---

## 8. Agente Riesgo

### Archivo previsto

```plaintext
08_agents_mcp/agents/risk_agent.py
```

### Prompt asociado

```plaintext
08_agents_mcp/prompts/risk_agent_prompt.md
```

### Objetivo

Analizar el impacto de la hipótesis sobre la cartera y sus métricas de riesgo.

### Inputs principales

```plaintext
04_portfolio_riesgo/carteras/cartera_real_fondmapfre_bolsa_america.csv
04_portfolio_riesgo/carteras/cartera_modelo_rv_usa.csv
04_portfolio_riesgo/series_historicas/rentabilidades_bam_componentes_enriquecido.csv
04_portfolio_riesgo/metricas/escenario_bam_tecnologia_plus3_posiciones.csv
04_portfolio_riesgo/metricas/escenario_bam_tecnologia_plus3_pesos_sector.csv
04_portfolio_riesgo/metricas/metricas_riesgo_bam_vs_escenario.csv
```

### Outputs esperados

```plaintext
04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.md
04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.json
```

### Preguntas que debe responder

- ¿Cómo cambia la exposición sectorial?
- ¿Cómo cambia la concentración por posición?
- ¿Qué valores explican más el cambio?
- ¿Qué métricas de riesgo cambian?
- ¿Aumenta volatilidad?
- ¿Aumenta VaR?
- ¿Aumenta drawdown?
- ¿Aumenta tracking error?
- ¿Qué alertas deben revisarse?

### Límites

El Agente Riesgo no debe:

- Emitir recomendación de compra o venta.
- Validar cumplimiento de mandato.
- Aprobar la hipótesis.
- Sustituir metodología oficial de riesgos.
- Presentar métricas del prototipo como métricas oficiales.

---

## 9. Agente Mandatos / Asset Allocation

### Archivo previsto

```plaintext
08_agents_mcp/agents/mandates_agent.py
```

### Prompt asociado

```plaintext
08_agents_mcp/prompts/mandates_agent_prompt.md
```

### Objetivo

Evaluar la compatibilidad preliminar de la hipótesis con la información conocida del fondo, el benchmark y las reglas de control del prototipo.

### Inputs principales

```plaintext
05_mandatos_asset_allocation/marco_control_prototipo_bam.md
05_mandatos_asset_allocation/reglas_control_prototipo_bam.json
05_mandatos_asset_allocation/benchmark/benchmark_stoxx_usa_900_tr_pesos.csv
05_mandatos_asset_allocation/benchmark/benchmark_stoxx_usa_900_tr_pesos_sector.csv
05_mandatos_asset_allocation/benchmark/comparativa_bam_vs_stoxx_usa_900_tr.csv
05_mandatos_asset_allocation/benchmark/comparativa_bam_vs_stoxx_usa_900_tr_sector.csv
04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.json
```

### Outputs esperados

```plaintext
05_mandatos_asset_allocation/outputs_mandatos/DECISION_001_mandatos.md
05_mandatos_asset_allocation/outputs_mandatos/DECISION_001_mandatos.json
```

### Preguntas que debe responder

- ¿Existe incumplimiento evidente con la información real conocida?
- ¿Qué benchmark se utiliza?
- ¿Qué desviaciones frente al benchmark aparecen?
- ¿La hipótesis aumenta concentración tecnológica?
- ¿La hipótesis tensiona reglas de control del prototipo?
- ¿Qué límites faltan para validar completamente?
- ¿Qué información debe revisar el gestor?

### Límites

El Agente Mandatos no debe:

- Decir que la operación está aprobada.
- Decir que cumple el mandato completo si no se dispone de él.
- Convertir reglas de prototipo en límites oficiales.
- Sustituir a cumplimiento, riesgos o al gestor.
- Emitir recomendación de inversión.

---

## 10. Agente Síntesis / Comité Virtual

### Archivo previsto

```plaintext
08_agents_mcp/agents/synthesis_agent.py
```

### Prompt asociado

```plaintext
08_agents_mcp/prompts/synthesis_agent_prompt.md
```

### Objetivo

Integrar las conclusiones de Macro, Riesgo y Mandatos en una síntesis orientada a comité.

### Inputs principales

```plaintext
03_macro_houseview/outputs_macro/DECISION_001_macro.json
04_portfolio_riesgo/outputs_riesgo/DECISION_001_riesgo.json
05_mandatos_asset_allocation/outputs_mandatos/DECISION_001_mandatos.json
```

### Outputs esperados

```plaintext
06_sintesis_comite/DECISION_001_sintesis.md
06_sintesis_comite/DECISION_001_sintesis.json
```

### Preguntas que debe responder

- ¿Qué puntos apoyan la hipótesis?
- ¿Qué riesgos aparecen?
- ¿Qué dicen los agentes?
- ¿Dónde hay acuerdo?
- ¿Dónde hay tensión?
- ¿Qué información falta?
- ¿Qué preguntas debe revisar el gestor?
- ¿Cuál es la conclusión prudente?

### Límites

El Agente Síntesis no debe:

- Decidir.
- Recomendar operación.
- Aprobar hipótesis.
- Ocultar tensiones entre agentes.
- Presentar una conclusión como instrucción de ejecución.

---

## 11. Qué es MCP en este prototipo

MCP se utilizará como capa de herramientas.

La idea es que los agentes no accedan directamente a todos los archivos de forma desordenada, sino mediante tools.

Ejemplo de herramientas MCP:

```plaintext
leer_archivo_texto
leer_json
leer_csv
listar_archivos
guardar_markdown
guardar_json
calcular_metricas_riesgo
generar_output_macro
generar_output_riesgo
generar_output_mandatos
generar_sintesis
```

Estas herramientas permiten que los agentes trabajen de forma más controlada y trazable.

---

## 12. Herramientas MCP previstas

### leer_archivo_texto

Lee archivos `.md` o `.txt`.

Uso esperado:

```plaintext
leer house_view_base.md
leer nota_tecnologia_usa.md
leer marco_control_prototipo_bam.md
```

---

### leer_json

Lee archivos `.json`.

Uso esperado:

```plaintext
leer decision_actual.json
leer escenarios_macro.json
leer reglas_control_prototipo_bam.json
leer outputs de agentes
```

---

### leer_csv

Lee archivos `.csv`.

Uso esperado:

```plaintext
leer indicadores_macro.csv
leer cartera_real_fondmapfre_bolsa_america.csv
leer metricas_riesgo_bam_vs_escenario.csv
leer comparativa_bam_vs_stoxx_usa_900_tr.csv
```

---

### guardar_markdown

Guarda outputs `.md`.

Uso esperado:

```plaintext
guardar DECISION_001_macro.md
guardar DECISION_001_riesgo.md
guardar DECISION_001_mandatos.md
guardar DECISION_001_sintesis.md
```

---

### guardar_json

Guarda outputs `.json`.

Uso esperado:

```plaintext
guardar DECISION_001_macro.json
guardar DECISION_001_riesgo.json
guardar DECISION_001_mandatos.json
guardar DECISION_001_sintesis.json
```

---

### calcular_metricas_riesgo

Ejecuta o encapsula el cálculo de métricas de riesgo.

Uso esperado:

```plaintext
calcular volatilidad, VaR, drawdown, beta y tracking error para BAM actual y escenario
```

---

### generar_output_macro

Genera el output del Agente Macro.

---

### generar_output_riesgo

Genera el output del Agente Riesgo.

---

### generar_output_mandatos

Genera el output del Agente Mandatos.

---

### generar_sintesis

Genera el output consolidado del Comité Virtual.

---

## 13. Carpeta mcp_server

La carpeta prevista es:

```plaintext
08_agents_mcp/mcp_server/
├── server.py
├── tools.py
└── mcp_config.json
```

### server.py

Archivo principal del servidor MCP.

Responsabilidades:

- Registrar herramientas.
- Exponer herramientas a Cursor o al cliente compatible.
- Gestionar entradas y salidas.
- Mantener rutas relativas del proyecto.

### tools.py

Archivo con la implementación de las herramientas.

Debe contener funciones como:

```plaintext
leer_archivo_texto
leer_json
leer_csv
guardar_markdown
guardar_json
listar_archivos
```

### mcp_config.json

Archivo de configuración para conectar el servidor MCP al entorno de trabajo.

---

## 14. Carpeta orchestrator

La carpeta prevista es:

```plaintext
08_agents_mcp/orchestrator/
└── run_decision_001.py
```

Este script debe lanzar el flujo completo:

```plaintext
1. Leer decision_actual.json.
2. Ejecutar macro_agent.
3. Ejecutar risk_agent.
4. Ejecutar mandates_agent.
5. Ejecutar synthesis_agent.
6. Guardar outputs finales.
```

El orquestador permite repetir la demo con una única ejecución.

---

## 15. Diferencia entre scripts actuales y agentes MCP

Los scripts actuales generan outputs directamente.

Ejemplo actual:

```plaintext
generar_output_decision_001_macro.py
generar_output_decision_001_riesgo.py
generar_output_decision_001_mandatos.py
generar_sintesis_decision_001.py
```

La capa MCP debe convertir esta lógica en herramientas reutilizables y agentes coordinados.

Diferencia clave:

```plaintext
Scripts actuales:
- Ejecutan una tarea concreta.

Agentes + MCP:
- El agente decide qué herramientas usar dentro de su ámbito.
- MCP proporciona herramientas controladas.
- El orquestador coordina el flujo.
```

---

## 16. Modo demo vs modo producción

### Modo demo

En modo demo, los agentes pueden apoyarse en archivos preparados y scripts ya construidos.

Características:

- Datos locales.
- Outputs predecibles.
- Decisión DECISION_001.
- Reglas de prototipo.
- Sin conexión real a sistemas productivos.
- Sin ejecución de operaciones.

### Modo producción

En modo producción haría falta:

- Conexión a fuentes oficiales.
- Mandatos completos.
- Límites reales.
- Validación de permisos.
- Trazabilidad avanzada.
- Logging.
- Control de versiones.
- Workflow de aprobación humana.
- Seguridad y gobierno de datos.

---

## 17. Flujo previsto para DECISION_001

El flujo concreto para DECISION_001 sería:

```plaintext
Input:
01_decision_input/decision_actual.json

Macro Agent:
lee contexto macro
genera DECISION_001_macro.md/json

Risk Agent:
lee cartera, series y métricas
genera DECISION_001_riesgo.md/json

Mandates Agent:
lee benchmark, reglas y output de riesgo
genera DECISION_001_mandatos.md/json

Synthesis Agent:
lee macro/riesgo/mandatos
genera DECISION_001_sintesis.md/json
```

---

## 18. Inputs y outputs esperados por agente

### Macro Agent

Inputs:

```plaintext
decision_actual.json
house_view_base.md
escenarios_macro.json
indicadores_macro.csv
supuestos_macro.json
nota_tecnologia_usa.md
```

Outputs:

```plaintext
DECISION_001_macro.md
DECISION_001_macro.json
```

---

### Risk Agent

Inputs:

```plaintext
cartera_real_fondmapfre_bolsa_america.csv
escenario_bam_tecnologia_plus3_posiciones.csv
rentabilidades_bam_componentes_enriquecido.csv
metricas_riesgo_bam_vs_escenario.csv
```

Outputs:

```plaintext
DECISION_001_riesgo.md
DECISION_001_riesgo.json
```

---

### Mandates Agent

Inputs:

```plaintext
marco_control_prototipo_bam.md
reglas_control_prototipo_bam.json
benchmark_stoxx_usa_900_tr_pesos.csv
comparativa_bam_vs_stoxx_usa_900_tr.csv
DECISION_001_riesgo.json
```

Outputs:

```plaintext
DECISION_001_mandatos.md
DECISION_001_mandatos.json
```

---

### Synthesis Agent

Inputs:

```plaintext
DECISION_001_macro.json
DECISION_001_riesgo.json
DECISION_001_mandatos.json
```

Outputs:

```plaintext
DECISION_001_sintesis.md
DECISION_001_sintesis.json
```

---

## 19. Estado actual

Estado después de construir las carpetas 00 a 06:

```plaintext
Base documental: creada.
Datos de cartera: creados.
Series históricas: transformadas.
Benchmark: transformado.
Métricas: calculadas.
Outputs simulados de agentes: generados.
Demo final: documentada.
```

Estado pendiente:

```plaintext
Crear carpeta agents.
Crear prompts internos de agentes.
Crear servidor MCP.
Crear herramientas MCP.
Crear orquestador.
Probar ejecución completa mediante run_decision_001.py.
```

---

## 20. Próximos archivos a crear

Orden recomendado:

```plaintext
08_agents_mcp/prompts/macro_agent_prompt.md
08_agents_mcp/prompts/risk_agent_prompt.md
08_agents_mcp/prompts/mandates_agent_prompt.md
08_agents_mcp/prompts/synthesis_agent_prompt.md

08_agents_mcp/agents/macro_agent.py
08_agents_mcp/agents/risk_agent.py
08_agents_mcp/agents/mandates_agent.py
08_agents_mcp/agents/synthesis_agent.py

08_agents_mcp/mcp_server/tools.py
08_agents_mcp/mcp_server/server.py
08_agents_mcp/mcp_server/mcp_config.json

08_agents_mcp/orchestrator/run_decision_001.py
```

---

## 21. Mensaje clave

Las carpetas 00 a 06 preparan el conocimiento y los outputs del prototipo.

La carpeta 07 convierte ese trabajo en una arquitectura agentic conectada a herramientas.

El objetivo no es que la IA decida.

El objetivo es que los agentes puedan analizar de forma trazable, coordinada y prudente.

InvestCopilot analiza.

La persona decide.
``