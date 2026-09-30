# Roadmap de tools — InvestCopilot en uso real

Contexto: hoy el prototipo cubre 1 fondo con datos reales (BAM, renta variable
USA), pero **ya no está limitado a 1 hipótesis fija**: desde el 2026-06-30
cualquier gestor puede plantear su propia hipótesis de inversión a discreción
(formulario "Nueva decisión" en la web), y los 5 agentes la analizan de verdad
en vez de seguir un guion precalculado (los prompts dejaron de tener
DECISION_001/tecnología hardcodeado como respuesta esperada). Para que
gestores reales de distintas clases de activo (macro, riesgo, asset
allocation, renta fija, multiactivo) lo usen de verdad sobre datos reales,
faltan tools y datos en varias direcciones. Pensado "out of the box" — no
solo "más de lo mismo" sectorial.

---

## Fase 1 — Generalizar el cálculo (sigue siendo prototipo, pero ya útil multiactivo)

Objetivo: que la tool de escenarios deje de ser "solo equity USA, solo
sector" y cubra lo mínimo que un gestor multiactivo necesita.

- [x] **Tool de riesgo sectorial ad-hoc (equity)** — `calcular_escenario_riesgo_sectorial`, cualquier sector/delta_pp, function calling real de Gemini. Hecho.
- [x] **Tool de duración/curva para renta fija** — `calcular_escenario_renta_fija` (shock de tipos paralelo o de spread de crédito, duración modificada + OAS). Hecho con **datos sintéticos**; pendiente sustituir por extracto real de Bloomberg (ver `04_portfolio_riesgo/renta_fija/README_renta_fija.md` para los campos exactos a pedir).
- [x] **Agente Research** — `research_agent.py`, integrado en orquestador (paso no bloqueante) y en el chat. Hecho con notas de ejemplo; pendiente conectar research real.
- [x] **Escenario multi-dimensional**: `calcular_escenario_multisector` — cambiar
  varios sectores/activos a la vez en una sola llamada. Hecho, cableado en
  Risk y Mandates (verificado 2026-07-13).
- [ ] **Tool de exposición FX**: impacto de divisa en carteras internacionales
  (relevante en cuanto se salga de un fondo 100% USD).
- [ ] **Tool de stress test histórico**: aplicar shocks de eventos reales (2008,
  taper tantrum 2013, COVID 2020, 2022 subida de tipos) a la cartera actual,
  no solo escenarios sintéticos sector+pp.
- [ ] **Tool de descomposición por factores**: value/growth/momentum/quality,
  beta, duración, spread de crédito — más informativo que solo sector GICS.
- [ ] **RAG sobre research/notas internas**: ingestión de PDFs/notas de research
  reales para que Research (y Macro) citen fuentes reales, no solo la nota
  de ejemplo actual.

**Esfuerzo**: medio. Reutiliza el patrón ya validado (función pura +
function calling). El RAG sobre research real es el salto de complejidad
que queda pendiente en esta fase.

---

## Fase 2 — Conectar a sistemas reales (la frontera prototipo → preproducción)

Objetivo: dejar de depender de CSVs congelados a fecha fija y de un único
fondo hardcodeado.

- **Conector de datos de mercado en vivo** (precios, índices, benchmarks) —
  hoy todo es estático a 2026-06-29.
  **Conector OMS/custodio**: posiciones reales de cartera en vez de
  `cartera_real_fondmapfre_bolsa_america.csv` mantenido a mano.
- **Conector de compliance/límites reales**: hoy `reglas_control_prototipo_bam.json`
  es un archivo de reglas escrito a mano y marcado como "no sustituye el
  mandato oficial". En producción esto tiene que venir del motor de
  compliance real, o el output es legalmente inútil.
- [~] **Soporte multi-fondo / multi-cartera (arquitectura lista, datos pendientes)**: el orquestador, los 5 agentes y la web ya aceptan cualquier `decision_id` y un selector de fondo desde `01_decision_input/fondos_disponibles.json` (2026-06-30) — un gestor ya puede plantear su propia hipótesis sobre el fondo que elija, no solo DECISION_001/BAM. Lo que falta de verdad: **datos cuantitativos reales de más de un fondo**. Hoy solo BAM tiene cartera/métricas/benchmark cargados; añadir un fondo nuevo es cuestión de datos (mismo formato que BAM), no de tocar código.
- **Comparador multi-escenario**: correr A/B/C en paralelo y comparar lado a
  lado (hoy es un escenario a la vez).
- **Tool de rebalanceo sugerido**: dado un target (SAA o TAA), proponer qué
  operaciones lo acercan, sujeto a límites — sigue siendo "apoyo", nunca
  ejecuta, pero hoy ni siquiera sugiere trades.

**Esfuerzo**: alto. Esta fase es la que de verdad cuesta dinero/tiempo de
integración (no es código nuevo, es conectar con sistemas de la casa).

---

## Fase 3 — Gobierno, trazabilidad y multiusuario

Objetivo: lo que un comité de inversión y compliance exigirían antes de
confiar en esto, no solo que "funcione".

- [~] **Registro de decisiones con aprobación humana (básico hecho, falta firma/versión formal)**: `{decision_id}_aprobacion.json` con timestamp + "revisado por" ya se guarda desde la web (botón "Marcar revisado"). Falta: firma real (no solo string fijo "gestor (sesión web)"), versionado de qué análisis exacto se aprobó.
- **Roles y permisos** (gestor / risk officer / CIO / compliance) — quién
  puede pedir qué análisis, quién aprueba.
- **Alertas proactivas**: notificar cuando una cartera se acerca a un límite,
  sin esperar a que alguien pregunte.
- **Explicabilidad/lineage**: por cada cifra mostrada, poder trazar de qué
  archivo/cálculo/fecha de datos viene (parcialmente ya existe vía
  `context_files_used`, pero no está expuesto al usuario final).
- **Versionado de modelos**: qué modelo (Gemini X.Y) y qué prompt generaron
  cada análisis — auditable a posteriori, relevante en un banco/gestora.

**Esfuerzo**: medio-alto, pero más "producto" que "modelo".

---

## Fase 4 — Expansión y diferenciación

Objetivo: una vez sólido lo anterior, lo que lo convierte en algo realmente
diferencial frente a "otro dashboard de riesgo".

- **Backtesting del propio InvestCopilot**: ¿qué tan bien han envejecido sus
  análisis pasados? Cierra el loop de confianza.
- **Agregación de riesgo de grupo** (multi-fondo, exposición consolidada a
  un emisor/sector a nivel de toda la gestora).
- **ESG/sostenibilidad como dimensión de análisis**, no solo riesgo/retorno.
- **Soporte de derivados y carteras alternativas** (cobertura, opciones,
  ilíquidos) — otro mundo de métricas (griegas, NAV con lag, etc.).
- **Tool registry dinámico para MCP**: que añadir una tool nueva (p.ej. de
  renta fija) no requiera tocar el orquestador a mano — hoy cada tool se
  cablea manualmente en `tools.py` y en el system prompt del chat.

**Esfuerzo**: variable, pero esto ya es roadmap de producto, no de
prototipo.

---

## Mi opinión: ¿qué hay que cruzar para "superar el MVP"?

El MVP actual demuestra la arquitectura y, desde hoy, demuestra que puede
calcular (no solo narrar) sobre datos reales. Pero sigue siendo **de un solo
fondo, un solo tipo de activo (equity), datos congelados a una fecha, y sin
ningún control de gobierno**. Para mí, las tres líneas que de verdad separan
"prototipo bonito" de "algo que un gestor usa cada semana" son:

1. **Datos vivos, no CSVs congelados** (Fase 2, conectores). Sin esto, todo
   lo demás es una demo, por buena que sea la IA.
2. **Multiactivo real, empezando por renta fija** (Fase 1). Un sistema que
   solo entiende sectores de equity USA no sirve a un gestor macro ni a un
   gestor de renta fija — y la propuesta de InvestCopilot es justo para
   "gestores de inversión" en general.
3. **Gobierno/aprobación humana como flujo, no como frase en el prompt**
   (Fase 3). Ahora mismo "la decisión final es humana" es una advertencia de
   texto. En un entorno real tiene que ser un paso de workflow con firma.

Lo demás (Fase 4, multi-fondo avanzado, ESG, derivados) es expansión de
producto una vez los tres puntos anteriores están resueltos — no haría falta
para una primera versión "real" usada por un equipo piloto.

---

## Priorización propuesta (a validar)

**Ejecución detallada del corto plazo (bugs + hardening) → ver
[PLAN_DE_TRABAJO.md](PLAN_DE_TRABAJO.md), que tiene precedencia sobre esta
tabla para lo inmediato.** Esta tabla es la vista estratégica por fases;
revisada 2026-07-13 para reflejar lo ya hecho.

| Prioridad | Item | Fase | Estado | Por qué |
|---|---|---|---|---|
| — | Tool de duración/curva (renta fija) | 1 | ✅ Hecha (datos sintéticos; no cableada en Risk/Mandates aún → PLAN_DE_TRABAJO P0-1) | Sin esto no sirve a la mitad de los gestores objetivo |
| — | Agente Research | 1 | ✅ Hecho | Falta de los 5 agentes originales, ya señalado en el diseño |
| — | Escenario multi-dimensional | 1 | ✅ Hecho | Extiende la tool ya construida, esfuerzo bajo/medio |
| — | Registro de decisiones con aprobación humana | 3 | ✅ Básico hecho, falta firma/versión formal | Requisito de gobierno antes de confiar en producción |
| P0 | Conector de datos de mercado en vivo | 2 | Sin empezar | Sin datos vivos todo lo demás es demo |
| P1 | Soporte multi-fondo | 2 | Arquitectura lista, datos pendientes | Falta cargar datos reales de más fondos |
| P1 | Cloud-readiness (secretos, retries, logging) | — | Sin empezar → PLAN_DE_TRABAJO P1 | Requisito antes de piloto real, no solo prototipo |
| P2 | Stress test histórico | 1 | Sin empezar | Alto valor, pero el escenario sintético ya cubre algo |
| P2 | RAG sobre research real | 1 | Sin empezar | Notas de ejemplo siguen siendo el límite del agente Research |
| P2 | Conector OMS/custodio y compliance real | 2 | Sin empezar | Alto coste de integración, depende de sistemas internos |
| P2 | Rebalanceo sugerido | 2 | Sin empezar | Valioso pero sensible (cerca de "recomendar"), requiere cuidado de diseño |
| P3 | Roles/permisos, alertas, explicabilidad expuesta | 3 | Sin empezar | Importante pero no bloqueante para un piloto cerrado |
| P3 | Fase 4 completa | 4 | Sin empezar | Expansión, no urgente |

Esto sigue siendo una propuesta a validar contigo, no una decisión cerrada —
en particular el orden P0/P1 del corto plazo.
