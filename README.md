# InvestCopilot

Prototipo de copiloto multiagente de apoyo a decisiones de inversión, desarrollado para el AI Summit.

> **InvestCopilot analiza. La persona decide.**  
> No ejecuta operaciones, no emite recomendaciones automáticas y no sustituye al gestor. La decisión final es siempre humana — restricción presente en todos los prompts de agente.

---

## ¿Qué hace?

El gestor plantea una hipótesis de inversión en lenguaje natural (ej. *"¿tiene sentido subir 2pp en Consumer Staples ante una desaceleración?"*) y el sistema lanza en paralelo cinco agentes especializados que analizan la hipótesis desde distintos ángulos y la sintetizan en un informe de comité virtual.

La interfaz es un chat: el gestor puede preguntar libremente sobre los outputs de los agentes, pedir métricas concretas o proponer refinamientos de escenario que se lanzan como nuevas decisiones.

---

## Arquitectura

```
09_web_app_chat/app.py          ← UI Streamlit (chat + nueva decisión)
08_agents_mcp/
  orchestrator/run_decision.py  ← Orquestador (paralelo + síntesis)
  agents/
    research_agent.py           ← Agente Research (cualitativo)
    macro_agent.py              ← Agente Macro / House View
    risk_agent.py               ← Agente Riesgo (VaR, vol, TE)
    mandates_agent.py           ← Agente Mandatos / Asset Allocation
    synthesis_agent.py          ← Síntesis / Comité Virtual
  prompts/                      ← Comportamiento de cada agente (prompt-driven)
  llm_client/llm_client.py      ← Cliente LLM unificado (mock / vertex_ai)
  mcp_server/tools.py           ← Tools MCP (escenario sectorial, RF)
  test_integracion.py           ← Test de integración end-to-end
01_decision_input/
  decision_actual.json          ← Caso demo DECISION_001
  decisiones/                   ← Hipótesis creadas desde la web
04_portfolio_riesgo/
  metricas/risk_scenario_tool.py          ← Tool cálculo equity sectorial
  renta_fija/fixed_income_scenario_tool.py ← Tool RF (datos sintéticos)
```

**Flujo de ejecución:**

```
Research ─┐
Macro    ─┼─ (paralelo, ~40s) ──→ Mandatos ──→ Síntesis
Risk     ─┘                         ↑
                                (depende de Risk)
```

---

## Instalación

### Requisitos

- Python 3.11+
- Cuenta Google Cloud con Vertex AI habilitado (`gemini-2.5-flash` + `gemini-2.5-pro`)
- `gcloud` CLI instalado y autenticado

### Setup

```bash
git clone https://github.com/Mepoide/ac_investcopilot
cd ac_investcopilot

pip install -r requirements.txt   # o: pip install streamlit google-cloud-aiplatform

# Configurar credenciales
gcloud auth application-default login

# Copiar y ajustar variables de entorno
cp .env.example .env
# Editar .env: GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, INVESTCOPILOT_LLM_MODE
```

### Variables de entorno (`.env`)

| Variable | Valor típico | Descripción |
|---|---|---|
| `INVESTCOPILOT_LLM_MODE` | `vertex_ai` | `mock` para desarrollo sin LLM |
| `GOOGLE_CLOUD_PROJECT` | `mi-proyecto-gcp` | Proyecto GCP con Vertex AI |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | Región de Vertex AI |
| `GOOGLE_VERTEX_MODEL` | `gemini-2.5-flash` | Modelo para agentes de dominio |

---

## Uso

### Interfaz web (modo principal)

```bash
python3 -m streamlit run 09_web_app_chat/app.py
```

Abre `http://localhost:8501`. Desde ahí:

1. Haz clic en **＋ Nueva decisión** (arriba a la derecha)
2. Escribe tu hipótesis en lenguaje natural y elige el fondo
3. El orquestador lanza los 5 agentes con progreso en vivo (~90-120s con LLM real)
4. Usa los botones post-ejecución o el chat libre para explorar los resultados

### Orquestador CLI

```bash
# Caso demo DECISION_001
python3 08_agents_mcp/orchestrator/run_decision.py

# Cualquier decisión creada desde la web
python3 08_agents_mcp/orchestrator/run_decision.py --decision-id DEC_20260707_165309
```

### Test de integración

```bash
# Mock (~2s, valida plomería)
python3 08_agents_mcp/test_integracion.py --mode mock

# Vertex AI real (~4-5min, valida tool calling y métricas)
python3 08_agents_mcp/test_integracion.py --mode vertex_ai
```

---

## Fondo de datos de referencia

Hoy solo hay datos reales de **Fondmapfre Bolsa América (BAM)**:

- Cartera de renta variable actual, benchmark (S&P 500), pesos sectoriales
- Métricas de riesgo: volatilidad, tracking error, correlaciones sectoriales
- Mandato y política de inversión del folleto
- Datos de renta fija: **sintéticos** (pendiente de Bloomberg real)

Soporte multi-fondo es Fase 2 del roadmap.

---

## Estado del proyecto

| Componente | Estado |
|---|---|
| 5 agentes (Research, Macro, Risk, Mandates, Synthesis) | ✅ Implementados, vertex_ai |
| Orquestador paralelo con progreso en vivo | ✅ |
| UI Streamlit con chat libre y multi-turn | ✅ |
| Tool de escenario equity sectorial | ✅ |
| Tool de escenario renta fija | ⚠️ Implementada, datos sintéticos |
| Risk agent para hipótesis de deuda | 🐛 No invoca tool RF (bug en backlog) |
| Datos Bloomberg reales (RF) | ❌ Pendiente |
| Soporte multi-fondo | ❌ Fase 2 |

---

## Principios de IA responsable

Ver `00_contexto/02_contexto/principios_ia_responsable.md` para el detalle completo.

Los puntos no negociables implementados en código:

- Ningún agente emite una recomendación de compra/venta directa
- El agente de síntesis expone tensiones y preguntas abiertas, no una conclusión automática
- El chat incluye la frase *"InvestCopilot analiza. La persona decide."* en cada respuesta de análisis
- El paso de aprobación humana queda registrado en `{decision_id}_aprobacion.json`

---

## Roadmap

Ver `TOOLS_ROADMAP.md` para el plan faseado de tools y `BACKLOG.md` para bugs y mejoras pendientes.

---

## Nota sobre esta versión pública

Este repositorio contiene solo el código, los prompts y la documentación del prototipo. **No incluye datos**: ni carteras reales, ni series de precios, ni pesos de benchmark, ni notas de research de terceros, ni outputs generados. Todo eso está sujeto a confidencialidad o licencia. Para ejecutarlo hay que aportar datos propios con la misma estructura de archivos que esperan los agentes. Los únicos datos incluidos son los de renta fija sintética de `04_portfolio_riesgo/renta_fija/`.
