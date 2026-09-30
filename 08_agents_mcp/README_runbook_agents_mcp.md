# Runbook Agents & MCP - InvestCopilot

## 1. Propósito del runbook

Este documento recoge los comandos necesarios para probar la capa agentic y MCP de InvestCopilot.

La carpeta `08_agents_mcp` contiene:

- prompts internos de agentes;
- agentes wrapper;
- cliente LLM;
- servidor MCP mínimo;
- tools MCP;
- orquestador completo de `DECISION_001`.

El objetivo de este runbook es poder comprobar rápidamente que todo funciona.

---

## 2. Estructura esperada

La estructura esperada es:

```plaintext
08_agents_mcp/
├── README_agents_mcp.md
├── README_runbook_agents_mcp.md
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
├── llm_client/
│   ├── llm_client.py
│   └── llm_client_test_output.md
├── mcp_server/
│   ├── tools.py
│   ├── server.py
│   ├── mcp_config.json
│   └── README_mcp_server.md
└── orchestrator/
    ├── run_decision_001.py
    ├── run_DECISION_001_summary.json
    └── run_DECISION_001_summary.md
```

---

## 3. Mensaje clave

Esta capa permite probar dos niveles:

```plaintext
modo script = flujo estable, determinista y reproducible
modo llm mock = arquitectura preparada para LLM sin llamar a modelo externo
```

En ambos casos:

```plaintext
InvestCopilot analiza.
La persona decide.
```

---

## 4. Abrir PowerShell en la raíz del proyecto

Ruta raíz esperada:

```plaintext
<ruta_repo>
```

Comando:

```powershell
cd "<ruta_repo>"
```

Si se usa Python específico:

```powershell
& C:/Python314/python.exe --version
```

---

## 5. Probar Macro Agent

### Modo script

```powershell
cd "<ruta_repo>\08_agents_mcp\agents"
& C:/Python314/python.exe macro_agent.py
```

Resultado esperado:

```plaintext
status: success
mode: script
DECISION_001_macro.md generado
DECISION_001_macro.json generado
```

### Modo LLM mock

Para probar modo LLM mock, cambiar temporalmente la última línea de `macro_agent.py` a:

```python
result = run_macro_agent(mode="llm", llm_mode="mock")
```

Después ejecutar:

```powershell
& C:/Python314/python.exe macro_agent.py
```

Resultado esperado:

```plaintext
DECISION_001_macro_llm.md
DECISION_001_macro_llm.json
```

Después de la prueba, volver a dejar:

```python
result = run_macro_agent(mode="script")
```

---

## 6. Probar Risk Agent

### Modo script

```powershell
cd "<ruta_repo>\08_agents_mcp\agents"
& C:/Python314/python.exe risk_agent.py
```

Resultado esperado:

```plaintext
status: success
mode: script
DECISION_001_riesgo.md generado
DECISION_001_riesgo.json generado
```

Si aparece `missing_optional_context_files`, no necesariamente es error. Solo indica archivos de contexto opcional que no se han encontrado.

### Modo LLM mock

Cambiar temporalmente la última línea de `risk_agent.py` a:

```python
result = run_risk_agent(mode="llm", llm_mode="mock")
```

Ejecutar:

```powershell
& C:/Python314/python.exe risk_agent.py
```

Resultado esperado:

```plaintext
DECISION_001_riesgo_llm.md
DECISION_001_riesgo_llm.json
```

Después de la prueba, volver a:

```python
result = run_risk_agent(mode="script")
```

---

## 7. Probar Mandates Agent

### Modo script

```powershell
cd "<ruta_repo>\08_agents_mcp\agents"
& C:/Python314/python.exe mandates_agent.py
```

Resultado esperado:

```plaintext
status: success
mode: script
DECISION_001_mandatos.md generado
DECISION_001_mandatos.json generado
```

### Modo LLM mock

Cambiar temporalmente la última línea de `mandates_agent.py` a:

```python
result = run_mandates_agent(mode="llm", llm_mode="mock")
```

Ejecutar:

```powershell
& C:/Python314/python.exe mandates_agent.py
```

Resultado esperado:

```plaintext
DECISION_001_mandatos_llm.md
DECISION_001_mandatos_llm.json
```

Después de la prueba, volver a:

```python
result = run_mandates_agent(mode="script")
```

---

## 8. Probar Synthesis Agent

### Modo script

```powershell
cd "<ruta_repo>\08_agents_mcp\agents"
& C:/Python314/python.exe synthesis_agent.py
```

Resultado esperado:

```plaintext
status: success
mode: script
DECISION_001_sintesis.md generado
DECISION_001_sintesis.json generado
```

### Modo LLM mock

Cambiar temporalmente la última línea de `synthesis_agent.py` a:

```python
result = run_synthesis_agent(mode="llm", llm_mode="mock")
```

Ejecutar:

```powershell
& C:/Python314/python.exe synthesis_agent.py
```

Resultado esperado:

```plaintext
DECISION_001_sintesis_llm.md
DECISION_001_sintesis_llm.json
```

Después de la prueba, volver a:

```python
result = run_synthesis_agent(mode="script")
```

---

## 9. Probar LLM Client

Ruta:

```plaintext
08_agents_mcp\llm_client
```

Comando:

```powershell
cd "<ruta_repo>\08_agents_mcp\llm_client"
& C:/Python314/python.exe llm_client.py
```

Resultado esperado:

```plaintext
status: success
mode: mock
llm_client_test_output.md generado
```

Archivo esperado:

```plaintext
08_agents_mcp\llm_client\llm_client_test_output.md
```

---

## 10. Probar Orquestador en modo script

Ruta:

```plaintext
08_agents_mcp\orchestrator
```

Comando:

```powershell
cd "<ruta_repo>\08_agents_mcp\orchestrator"
& C:/Python314/python.exe run_decision_001.py --mode script
```

Resultado esperado:

```plaintext
macro_agent success
risk_agent success
mandates_agent success
synthesis_agent success
workflow status success
```

Archivos generados:

```plaintext
08_agents_mcp\orchestrator\run_DECISION_001_summary.json
08_agents_mcp\orchestrator\run_DECISION_001_summary.md
```

Este es el modo más estable para enseñar la demo.

---

## 11. Probar Orquestador en modo LLM mock

Comando:

```powershell
cd "<ruta_repo>\08_agents_mcp\orchestrator"
& C:/Python314/python.exe run_decision_001.py --mode llm --llm-mode mock
```

Resultado esperado:

```plaintext
macro_agent success
risk_agent success
mandates_agent success
synthesis_agent success
workflow status success
```

Archivos LLM mock esperados:

```plaintext
03_macro_houseview\outputs_macro\DECISION_001_macro_llm.md
03_macro_houseview\outputs_macro\DECISION_001_macro_llm.json

04_portfolio_riesgo\outputs_riesgo\DECISION_001_riesgo_llm.md
04_portfolio_riesgo\outputs_riesgo\DECISION_001_riesgo_llm.json

05_mandatos_asset_allocation\outputs_mandatos\DECISION_001_mandatos_llm.md
05_mandatos_asset_allocation\outputs_mandatos\DECISION_001_mandatos_llm.json

06_sintesis_comite\DECISION_001_sintesis_llm.md
06_sintesis_comite\DECISION_001_sintesis_llm.json
```

Nota:

```plaintext
En llm_mode=mock no se llama a ningún modelo externo.
```

---

## 12. Probar Tools MCP

Ruta:

```plaintext
08_agents_mcp\mcp_server
```

Comando:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe tools.py
```

Resultado esperado:

```plaintext
listar_tools_disponibles
validar_estructura_proyecto
```

Si `estructura_ok` es `true`, la estructura principal está correcta.

---

## 13. Probar Server MCP en modo test

Comando:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe server.py --test
```

Resultado esperado:

```plaintext
initialize
tools/list
validar_estructura_proyecto
resumen_rapido_decision_001
```

Si estos bloques devuelven JSON correctamente, el servidor mínimo funciona.

---

## 14. Probar Server MCP en modo stdin/stdout

Ejecutar:

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe server.py
```

Después pegar una petición JSON-RPC y pulsar Enter:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

Otra prueba:

```json
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"validar_estructura_proyecto","arguments":{}}}
```

Otra prueba:

```json
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"resumen_rapido_decision_001","arguments":{}}}
```

---

## 15. Probar lectura de outputs mediante MCP

Con `server.py` ejecutándose en modo stdin/stdout, se pueden probar estas llamadas.

### Leer output Macro en JSON

```json
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"macro","formato":"json"}}}
```

### Leer output Riesgo en Markdown

```json
{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"riesgo","formato":"md"}}}
```

### Leer output Mandatos en JSON

```json
{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"mandatos","formato":"json"}}}
```

### Leer output Síntesis en Markdown

```json
{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"leer_output_agente","arguments":{"nombre_agente":"sintesis","formato":"md"}}}
```

---

## 16. Ejecutar el orquestador desde MCP

Con `server.py` en modo stdin/stdout, enviar:

```json
{"jsonrpc":"2.0","id":8,"method":"tools/call","params":{"name":"ejecutar_orquestador_decision_001","arguments":{}}}
```

Resultado esperado:

```plaintext
Se ejecuta el flujo Macro -> Riesgo -> Mandatos -> Síntesis.
Se actualizan los summaries del orquestador.
```

Archivos esperados:

```plaintext
08_agents_mcp\orchestrator\run_DECISION_001_summary.json
08_agents_mcp\orchestrator\run_DECISION_001_summary.md
```

---

## 17. Error habitual: comando PowerShell dentro de Python

No pegar comandos como este dentro de un archivo `.py`:

```powershell
python run_decision_001.py --mode llm
```

Eso debe ir en PowerShell, no dentro del código.

Dentro de un archivo Python solo deben ir instrucciones Python, por ejemplo:

```python
import os
from pathlib import Path
```

Si aparece algo como:

```python
run_decision_001.py --mode llmimport os
```

hay que borrarlo y dejar los imports correctos.

---

## 18. Error habitual: Error parseando JSON

Si el servidor MCP devuelve:

```plaintext
Error parseando JSON
```

normalmente significa que se ha pegado un comando de PowerShell donde el servidor esperaba JSON.

Incorrecto dentro del servidor:

```plaintext
& C:/Python314/python.exe server.py
```

Correcto para probar sin JSON manual:

```powershell
& C:/Python314/python.exe server.py --test
```

Correcto en modo servidor:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

---

## 19. Error habitual: archivo opcional faltante

Algunos agentes pueden devolver:

```plaintext
missing_optional_context_files
```

Esto no siempre es error.

Significa que el agente está avisando de que falta un archivo de contexto que puede enriquecer la respuesta, pero que no es crítico para ejecutar el flujo.

Si el estado general es:

```plaintext
status: success
```

el agente ha funcionado correctamente.

---

## 20. Error habitual: modo LLM real sin variables de entorno

Si se ejecuta:

```powershell
& C:/Python314/python.exe run_decision_001.py --mode llm --llm-mode azure_openai
```

sin variables de entorno, el cliente LLM puede devolver error indicando variables faltantes.

Variables esperadas para Azure OpenAI:

```plaintext
AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_VERSION
```

Variables esperadas para endpoint compatible OpenAI:

```plaintext
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
```

Para la demo segura, usar:

```powershell
& C:/Python314/python.exe run_decision_001.py --mode llm --llm-mode mock
```

---

## 21. Validación rápida final

Para validar todo rápidamente, ejecutar en este orden:

### 1. LLM Client

```powershell
cd "<ruta_repo>\08_agents_mcp\llm_client"
& C:/Python314/python.exe llm_client.py
```

### 2. Tools MCP

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe tools.py
```

### 3. Server MCP test

```powershell
cd "<ruta_repo>\08_agents_mcp\mcp_server"
& C:/Python314/python.exe server.py --test
```

### 4. Orquestador modo script

```powershell
cd "<ruta_repo>\08_agents_mcp\orchestrator"
& C:/Python314/python.exe run_decision_001.py --mode script
```

### 5. Orquestador modo LLM mock

```powershell
cd "<ruta_repo>\08_agents_mcp\orchestrator"
& C:/Python314/python.exe run_decision_001.py --mode llm --llm-mode mock
```

---

## 22. Qué significa que todo esté correcto

Si todo funciona, deberíamos tener:

```plaintext
Agentes script funcionando
Agentes llm mock funcionando
llm_client funcionando
tools MCP funcionando
server MCP test funcionando
orquestador script funcionando
orquestador llm mock funcionando
outputs .md y .json actualizados
```

---

## 23. Estado final esperado

Estado final esperado de la capa 07:

```plaintext
08_agents_mcp/
├── prompts/          OK
├── agents/           OK
├── llm_client/       OK
├── mcp_server/       OK
└── orchestrator/     OK
```

---

## 24. Qué tenemos y qué no tenemos

### Tenemos

```plaintext
Base documental
Datos
Scripts de cálculo
Prompts internos
Agentes wrapper
Modo script
Modo LLM mock
Cliente LLM preparado
Tools MCP
Servidor MCP mínimo
Orquestador
Runbook
```

### No tenemos todavía por defecto

```plaintext
Llamada real a LLM activada
Integración con librería MCP externa
Autenticación
Permisos avanzados
Logging productivo
Workflow formal de aprobación
Conexión a sistemas productivos
```

---

## 25. Modos recomendados para demo

### Demo estable

Usar:

```powershell
& C:/Python314/python.exe run_decision_001.py --mode script
```

Este modo es reproducible y usa los scripts deterministas.

### Demo arquitectura LLM

Usar:

```powershell
& C:/Python314/python.exe run_decision_001.py --mode llm --llm-mode mock
```

Este modo demuestra que la arquitectura está preparada para LLM, pero sin llamar a ningún modelo externo.

---

## 26. Mensaje final

Esta capa deja preparado InvestCopilot para explicar tres niveles de madurez:

```plaintext
1. Base documental y datos
2. Agentes wrapper deterministas
3. Arquitectura preparada para LLM y MCP
```

Todavía no estamos usando un LLM real por defecto.

Estamos demostrando que la arquitectura está preparada, pero mantenemos una demo estable, reproducible y segura.

InvestCopilot analiza.

La persona decide.