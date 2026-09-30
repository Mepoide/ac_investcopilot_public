# README MCP Server - InvestCopilot

## 1. Propósito del documento

Este documento explica cómo probar y utilizar el servidor MCP mínimo de InvestCopilot.

La carpeta `mcp_server` contiene una implementación local y sencilla de un servidor tipo MCP/stdin-stdout para la demo.

El objetivo es exponer herramientas controladas para que los agentes o un cliente compatible puedan:

- listar archivos;
- leer Markdown;
- leer JSON;
- leer CSV;
- guardar outputs;
- leer outputs de agentes;
- ejecutar el orquestador completo de DECISION_001;
- validar la estructura del proyecto;
- obtener un resumen rápido de la decisión.

Esta versión está pensada para demo y trazabilidad, no para producción.

---

## 2. Ubicación del servidor

El servidor está en:

```plaintext
08_agents_mcp/mcp_server/
```

Archivos principales:

```plaintext
08_agents_mcp/mcp_server/tools.py
08_agents_mcp/mcp_server/server.py
08_agents_mcp/mcp_server/mcp_config.json
08_agents_mcp/mcp_server/README_mcp_server.md
```

---

## 3. Qué contiene cada archivo

### tools.py

Contiene las funciones reutilizables que actúan como herramientas.

Tools disponibles:

```plaintext
listar_tools_disponibles
listar_archivos
leer_texto
leer_json
leer_csv
guardar_texto
guardar_json
leer_output_agente
ejecutar_orquestador_decision_001
validar_estructura_proyecto
resumen_rapido_decision_001
```

### server.py

Expone las tools mediante una interfaz JSON-RPC mínima por stdin/stdout.

Soporta métodos:

```plaintext
initialize
tools/list
tools/call
ping
```

### mcp_config.json

Documenta la configuración del servidor MCP mínimo:

- nombre del servidor;
- ruta del proyecto;
- tools disponibles;
- agentes;
- orquestador;
- limitaciones;
- mensaje de IA responsable.

---

## 4. Probar tools.py directamente

Para probar las tools sin servidor, ejecutar desde PowerShell:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
python tools.py
```

Si se usa un Python específico:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe tools.py
```

Resultado esperado:

- debe mostrar el listado de tools disponibles;
- debe ejecutar `validar_estructura_proyecto`;
- debe indicar si falta alguna ruta clave.

---

## 5. Probar server.py en modo test

La forma más sencilla de validar el servidor es usar el modo test:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
python server.py --test
```

O con Python específico:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe server.py --test
```

Este modo ejecuta pruebas internas de:

```plaintext
initialize
tools/list
validar_estructura_proyecto
resumen_rapido_decision_001
```

Resultado esperado:

- varios bloques JSON;
- `initialize` debe devolver información del servidor;
- `tools/list` debe devolver las tools disponibles;
- `validar_estructura_proyecto` debe revisar las rutas clave;
- `resumen_rapido_decision_001` debe leer la síntesis final.

---

## 6. Probar server.py en modo servidor

Si se ejecuta sin `--test`, el servidor espera recibir líneas JSON-RPC por stdin.

Ejecutar:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
python server.py
```

O:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe server.py
```

Después pegar una línea JSON-RPC y pulsar Enter.

---

## 7. Ejemplo: initialize

Entrada:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

Resultado esperado:

El servidor devuelve:

- nombre del servidor;
- versión;
- capacidades;
- notas de demo.

---

## 8. Ejemplo: listar tools

Entrada:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}
```

Resultado esperado:

El servidor devuelve la lista de tools disponibles y sus esquemas de entrada.

---

## 9. Ejemplo: validar estructura del proyecto

Entrada:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"validar_estructura_proyecto","arguments":{}}}
```

Resultado esperado:

El servidor devuelve si la estructura principal está completa.

Campos relevantes:

```plaintext
estructura_ok
numero_rutas_revisadas
numero_faltantes
faltantes
```

Si `estructura_ok` es `true`, la estructura esperada está presente.

---

## 10. Ejemplo: obtener resumen rápido de DECISION_001

Entrada:

```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"resumen_rapido_decision_001","arguments":{}}}
```

Resultado esperado:

El servidor devuelve un resumen de la síntesis final:

```plaintext
id_decision
hipotesis
clasificacion_consolidada
resumen_clasificacion
conclusion
alertas_consolidadas
informacion_faltante_consolidada
preguntas_revision_humana
```

---

## 11. Ejemplo: leer output de un agente

### Leer output JSON del Agente Macro

Entrada:

```json
{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"macro","formato":"json"}}}
```

### Leer output Markdown del Agente Riesgo

Entrada:

```json
{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"riesgo","formato":"md"}}}
```

### Leer output JSON del Agente Mandatos

Entrada:

```json
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"mandatos","formato":"json"}}}
```

### Leer output Markdown de Síntesis

Entrada:

```json
{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"sintesis","formato":"md"}}}
```

---

## 12. Ejemplo: listar archivos

Entrada:

```json
{"jsonrpc":"2.0","id":9,"method":"tools/call","params":{"name":"listar_archivos","arguments":{"ruta":"06_sintesis_comite","patron":"*.md","recursivo":false}}}
```

Resultado esperado:

El servidor lista los archivos `.md` en la carpeta de síntesis.

---

## 13. Ejemplo: leer un JSON específico

Entrada:

```json
{"jsonrpc":"2.0","id":10,"method":"tools/call","params":{"name":"leer_json","arguments":{"ruta":"06_sintesis_comite/DECISION_001_sintesis.json"}}}
```

Resultado esperado:

Devuelve el contenido estructurado de la síntesis final.

---

## 14. Ejemplo: leer un CSV

Entrada:

```json
{"jsonrpc":"2.0","id":11,"method":"tools/call","params":{"name":"leer_csv","arguments":{"ruta":"04_portfolio_riesgo/metricas/metricas_riesgo_bam_vs_escenario.csv","max_filas":5}}}
```

Resultado esperado:

Devuelve:

- número total de filas;
- columnas;
- primeras filas del CSV.

---

## 15. Ejemplo: ejecutar el orquestador completo

Entrada:

```json
{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"ejecutar_orquestador_decision_001","arguments":{}}}
```

Resultado esperado:

Ejecuta el flujo completo:

```plaintext
Macro Agent
Risk Agent
Mandates Agent
Synthesis Agent
```

Y genera o actualiza:

```plaintext
08_agents_mcp/orchestrator/run_DECISION_001_summary.json
08_agents_mcp/orchestrator/run_DECISION_001_summary.md
```

---

## 16. Error habitual: Error parseando JSON

Si aparece un error como:

```json
{
  "code": -32700,
  "message": "Error parseando JSON."
}
```

normalmente significa que el servidor recibió una línea que no era JSON.

Ejemplo incorrecto:

```plaintext
& C:/Python314/python.exe "<ruta_repo>/08_agents_mcp/mcp_server/server.py"
```

Eso es un comando de PowerShell, no una petición JSON-RPC.

Para probar sin introducir JSON manualmente, usar:

```powershell
python server.py --test
```

---

## 17. Flujo recomendado de pruebas

Orden recomendado:

### 1. Probar tools.py

```powershell
python tools.py
```

### 2. Probar server.py en modo test

```powershell
python server.py --test
```

### 3. Probar server.py en modo servidor

```powershell
python server.py
```

Y enviar:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

### 4. Probar ejecución del orquestador vía tool

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"ejecutar_orquestador_decision_001","arguments":{}}}
```

---

## 18. Qué demuestra esta capa MCP

Esta capa demuestra que InvestCopilot puede exponer herramientas controladas para:

- leer información;
- consultar outputs;
- validar estructura;
- ejecutar el flujo completo;
- generar resumen de la decisión.

Aunque todavía es una versión mínima, ya muestra la lógica de una arquitectura MCP:

```plaintext
Cliente / agente
→ llama tool
→ tool accede a datos o ejecuta flujo
→ devuelve respuesta estructurada
```

---

## 19. Qué no hace todavía

Esta versión no hace todavía:

- llamadas reales a LLM;
- integración con librería MCP externa;
- autenticación;
- control avanzado de permisos;
- logging productivo;
- conexión a sistemas reales;
- ejecución de operaciones;
- validación oficial de riesgos o mandatos.

---

## 20. Próximo paso recomendado

Después de validar `tools.py`, `server.py` y `mcp_config.json`, el siguiente paso sería preparar una capa opcional de LLM:

```plaintext
08_agents_mcp/llm_client/
└── llm_client.py
```

Esa capa permitiría que los agentes funcionen en dos modos:

```plaintext
modo_script
modo_llm
```

Donde:

- `modo_script`: usa los scripts deterministas actuales.
- `modo_llm`: usa prompt + contexto + llamada a modelo.

---

## 21. Mensaje clave

El servidor MCP mínimo no decide.

El servidor MCP mínimo expone herramientas.

Las herramientas permiten que el flujo sea más trazable, modular y controlado.

InvestCopilot analiza.

La persona decide.