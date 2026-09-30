from pathlib import Path
import json
import runpy
import sys

_AGENTS_MCP_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_MCP_DIR))
try:
    from log_util import log as _log
except ImportError:
    def _log(*args, **kwargs): pass


class RiskAgent:
    """
    Risk Agent / Agente Riesgo - InvestCopilot

    Modos disponibles:

    1. script
       Usa el script determinista existente:
       04_portfolio_riesgo/outputs_riesgo/generar_output_decision_001_riesgo.py

    2. llm
       Usa risk_agent_prompt.md + contexto + llm_client.py

    Esta versión es más robusta:
    - solo exige los archivos críticos;
    - trata otros archivos como contexto opcional;
    - no falla si falta algún archivo auxiliar;
    - mantiene modo script estable;
    - permite probar modo llm en mock.
    """

    def __init__(self, project_dir: Path | None = None, decision_id: str = "DECISION_001"):
        if project_dir is None:
            self.project_dir = Path(__file__).resolve().parents[2]
        else:
            self.project_dir = Path(project_dir)

        self.decision_id = decision_id

        if decision_id == "DECISION_001":
            self.decision_path = self.project_dir / "01_decision_input" / "decision_actual.json"
        else:
            self.decision_path = self.project_dir / "01_decision_input" / "decisiones" / f"{decision_id}.json"

        self.agent_dir = self.project_dir / "08_agents_mcp"
        self.prompts_dir = self.agent_dir / "prompts"
        self.prompt_path = self.prompts_dir / "risk_agent_prompt.md"

        self.llm_client_dir = self.agent_dir / "llm_client"
        self.llm_client_path = self.llm_client_dir / "llm_client.py"

        self.risk_dir = self.project_dir / "04_portfolio_riesgo"
        self.carteras_dir = self.risk_dir / "carteras"
        self.series_dir = self.risk_dir / "series_historicas"
        self.metricas_dir = self.risk_dir / "metricas"
        self.outputs_dir = self.risk_dir / "outputs_riesgo"

        self.generator_script = self.outputs_dir / "generar_output_decision_001_riesgo.py"

        self.output_md = self.outputs_dir / f"{decision_id}_riesgo.md"
        self.output_json = self.outputs_dir / f"{decision_id}_riesgo.json"

        self.output_llm_md = self.outputs_dir / f"{decision_id}_riesgo_llm.md"
        self.output_llm_json = self.outputs_dir / f"{decision_id}_riesgo_llm.json"
        self.output_llm_data_json = self.outputs_dir / f"{decision_id}_riesgo_llm_data.json"

        # Archivos mínimos para modo script.
        # El propio script generador ya se encargará de usar los datos que necesite.
        self.required_inputs_script = [
            self.prompt_path,
            self.generator_script,
        ]

        # Archivos mínimos para modo LLM.
        self.required_inputs_llm = [
            self.prompt_path,
            self.llm_client_path,
        ]

        # Archivos de contexto. Si alguno falta, no rompemos el agente.
        self.context_files = [
            self.decision_path,

            self.carteras_dir / "cartera_real_fondmapfre_bolsa_america.csv",
            self.carteras_dir / "cartera_modelo_rv_usa.csv",
            self.carteras_dir / "comparativa_modelo_vs_bam.csv",
            self.carteras_dir / "comparativa_modelo_vs_bam_pesos_sector.csv",

            self.series_dir / "mapping_isin_ticker_gics.csv",
            self.series_dir / "precios_bam_componentes_enriquecido.csv",
            self.series_dir / "rentabilidades_bam_componentes_enriquecido.csv",

            self.metricas_dir / "README_metricas_riesgo.md",
            self.metricas_dir / "resumen_riesgo_bam_vs_modelo.md",
            self.metricas_dir / "escenario_tecnologia_plus3.md",
            self.metricas_dir / "escenario_bam_tecnologia_plus3_posiciones.csv",
            self.metricas_dir / "escenario_bam_tecnologia_plus3_pesos_sector.csv",
            self.metricas_dir / "metricas_riesgo_bam_vs_escenario.csv",
            self.metricas_dir / "resumen_metricas_riesgo_bam_vs_escenario.md",
        ]

    # ============================================================
    # LECTURA Y VALIDACIÓN
    # ============================================================

    def read_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"No se encuentra el prompt del Risk Agent: {self.prompt_path}")

        return self.prompt_path.read_text(encoding="utf-8", errors="ignore")

    def validate_inputs(self, mode: str = "script") -> dict:
        mode = mode.lower().strip()

        if mode == "script":
            required = self.required_inputs_script
        elif mode == "llm":
            required = self.required_inputs_llm
        else:
            return {
                "agent": "risk_agent",
                "status": "error",
                "message": "Modo no reconocido.",
                "mode": mode,
                "valid_modes": ["script", "llm"]
            }

        missing_required = [str(path) for path in required if not path.exists()]
        missing_context = [str(path) for path in self.context_files if not path.exists()]

        return {
            "agent": "risk_agent",
            "mode": mode,
            "status": "ok" if not missing_required else "missing_required_inputs",
            "missing_required_inputs": missing_required,
            "missing_optional_context_files": missing_context,
            "required_inputs": [str(path) for path in required],
            "prompt_path": str(self.prompt_path),
        }

    # ============================================================
    # MODO SCRIPT
    # ============================================================

    def run_script_mode(self) -> dict:
        if self.decision_id != "DECISION_001":
            return {
                "agent": "risk_agent",
                "mode": "script",
                "status": "error",
                "message": (
                    "El modo script solo está disponible para DECISION_001 (caso de demo "
                    "precalculado). Para cualquier otra decisión, usa mode='llm'."
                ),
                "decision_id": self.decision_id,
            }

        validation = self.validate_inputs(mode="script")

        if validation["status"] != "ok":
            return {
                "agent": "risk_agent",
                "mode": "script",
                "status": "error",
                "message": "Faltan inputs críticos para ejecutar el Agente Riesgo en modo script.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "risk_agent",
                "mode": "script",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Riesgo.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        try:
            runpy.run_path(str(self.generator_script), run_name="__main__")
        except Exception as e:
            return {
                "agent": "risk_agent",
                "mode": "script",
                "status": "error",
                "message": "Error ejecutando el script generador de riesgo.",
                "generator_script": str(self.generator_script),
                "error": str(e),
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "missing_optional_context_files": validation.get("missing_optional_context_files", []),
            }

        if not self.output_md.exists() or not self.output_json.exists():
            return {
                "agent": "risk_agent",
                "mode": "script",
                "status": "error",
                "message": "El script se ejecutó, pero no se generaron todos los outputs esperados.",
                "expected_outputs": [
                    str(self.output_md),
                    str(self.output_json),
                ],
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "missing_optional_context_files": validation.get("missing_optional_context_files", []),
            }

        with open(self.output_json, "r", encoding="utf-8") as f:
            output_data = json.load(f)

        return {
            "agent": "risk_agent",
            "mode": "script",
            "status": "success",
            "message": "Agente Riesgo ejecutado correctamente en modo script.",
            "prompt_used": str(self.prompt_path),
            "prompt_characters": len(prompt_text),
            "outputs": {
                "markdown": str(self.output_md),
                "json": str(self.output_json),
            },
            "summary": {
                "id_decision": output_data.get("id_decision"),
                "resultado": output_data.get("resultado"),
                "cartera": output_data.get("cartera"),
                "escenario": output_data.get("escenario"),
                "lectura_principal": output_data.get("lectura_principal"),
                "alertas": output_data.get("alertas", []),
                "informacion_faltante": output_data.get("informacion_faltante", []),
            },
            "missing_optional_context_files": validation.get("missing_optional_context_files", []),
        }

    # ============================================================
    # MODO LLM
    # ============================================================

    def run_llm_mode(
        self,
        llm_mode: str = "mock",
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 10000
    ) -> dict:
        validation = self.validate_inputs(mode="llm")

        if validation["status"] != "ok":
            return {
                "agent": "risk_agent",
                "mode": "llm",
                "status": "error",
                "message": "Faltan inputs críticos para ejecutar el Agente Riesgo en modo LLM.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "risk_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Riesgo.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        risk_tool_dir = self.project_dir / "04_portfolio_riesgo" / "metricas"
        if str(risk_tool_dir) not in sys.path:
            sys.path.insert(0, str(risk_tool_dir))

        rf_tool_dir = self.project_dir / "04_portfolio_riesgo" / "renta_fija"
        if str(rf_tool_dir) not in sys.path:
            sys.path.insert(0, str(rf_tool_dir))

        if str(self.llm_client_dir) not in sys.path:
            sys.path.append(str(self.llm_client_dir))

        try:
            from llm_client import call_llm_with_tools, build_context_from_files, extract_json_block
        except Exception as e:
            return {
                "agent": "risk_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido importar llm_client.",
                "llm_client_path": str(self.llm_client_path),
                "error": str(e),
            }

        # Tool declarations para cálculo cuantitativo ad-hoc
        RISK_TOOLS = [{"functionDeclarations": [
            {
                "name": "calcular_escenario_sectorial",
                "description": (
                    "Calcula el impacto real en métricas de riesgo (volatilidad anualizada, "
                    "VaR histórico 95%, máximo drawdown, tracking error, beta) de cambiar el "
                    "peso de UN sector GICS de la cartera BAM en +/- delta_pp puntos "
                    "porcentuales. LLAMA a esta tool siempre que la hipótesis implique un "
                    "cambio en un solo sector de la cartera de renta variable."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "sector": {"type": "STRING", "description": "Nombre sector GICS (p.ej. 'Health Care', 'Information Technology')."},
                        "delta_pp": {"type": "NUMBER", "description": "Cambio en p.p. Negativo=reducir, positivo=aumentar."},
                    },
                    "required": ["sector", "delta_pp"],
                },
            },
            {
                "name": "calcular_escenario_multisector",
                "description": (
                    "Calcula el impacto real en métricas de riesgo de cambiar VARIOS sectores "
                    "a la vez. El resto de cartera financia el neto pro-rata. LLAMA a esta "
                    "tool cuando la hipótesis implique movimientos simultáneos en más de un sector."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "cambios": {
                            "type": "ARRAY",
                            "description": "Lista de cambios: [{sector, delta_pp}, ...]",
                            "items": {
                                "type": "OBJECT",
                                "properties": {
                                    "sector": {"type": "STRING"},
                                    "delta_pp": {"type": "NUMBER"},
                                },
                                "required": ["sector", "delta_pp"],
                            },
                        },
                    },
                    "required": ["cambios"],
                },
            },
            {
                "name": "calcular_escenario_renta_fija",
                "description": (
                    "Calcula el impacto en la cartera de renta fija de un shock de tipos de "
                    "interés (movimiento paralelo de la curva) o de spread de crédito, usando "
                    "duración modificada y OAS por posición. LLAMA a esta tool cuando la "
                    "hipótesis implique bonos, deuda pública o privada, tipos de interés, "
                    "spread de crédito, duración, o cualquier activo de renta fija."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "tipo_shock": {
                            "type": "STRING",
                            "description": "Tipo de shock: 'tipos_paralelo' (movimiento paralelo de la curva) o 'spread_credito' (widening/tightening de spread).",
                        },
                        "magnitud_pb": {
                            "type": "NUMBER",
                            "description": "Magnitud del shock en puntos básicos. Positivo = subida de tipos/spread, negativo = bajada.",
                        },
                    },
                    "required": ["tipo_shock", "magnitud_pb"],
                },
            },
        ]}]

        def _ejecutar_tool_riesgo(nombre: str, args: dict) -> dict:
            try:
                if nombre == "calcular_escenario_renta_fija":
                    from fixed_income_scenario_tool import calcular_escenario_renta_fija as _calc_rf
                    return _calc_rf(
                        tipo_shock=args.get("tipo_shock", "tipos_paralelo"),
                        magnitud_pb=float(args.get("magnitud_pb", 0)),
                    )
                from risk_scenario_tool import calcular_escenario_sectorial, calcular_escenario_multisector
                if nombre == "calcular_escenario_sectorial":
                    return calcular_escenario_sectorial(
                        sector=args.get("sector", ""),
                        delta_pp=float(args.get("delta_pp", 0)),
                    )
                if nombre == "calcular_escenario_multisector":
                    return calcular_escenario_multisector(cambios=args.get("cambios", []))
            except Exception as e:
                return {"status": "error", "error": str(e)}
            return {"error": f"Tool no reconocida: {nombre}"}

        try:
            existing_context_files = [p for p in self.context_files if p.exists()]

            context = build_context_from_files(
                files=existing_context_files,
                title=f"Contexto Risk Agent - {self.decision_id}",
                max_chars_per_file=5000
            )

            llm_response = call_llm_with_tools(
                system_prompt=prompt_text,
                user_context=context,
                tools=RISK_TOOLS,
                tool_executor_fn=_ejecutar_tool_riesgo,
                mode=llm_mode,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_context_chars=30000,
            )

        except Exception as e:
            return {
                "agent": "risk_agent",
                "mode": "llm",
                "status": "error",
                "message": "Error construyendo contexto o llamando al LLM.",
                "error": str(e),
            }

        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        if llm_response.get("status") == "success":
            response_text = llm_response.get("data", {}).get("response_text", "")

            self.output_llm_md.write_text(response_text, encoding="utf-8")

            parsed_data = extract_json_block(response_text)

            if parsed_data is not None:
                with open(self.output_llm_data_json, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2, default=str)

            output_json_data = {
                "id_decision": self.decision_id,
                "agent": "risk_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "context_characters": len(context),
                "context_files_used": [str(path) for path in existing_context_files],
                "missing_optional_context_files": validation.get("missing_optional_context_files", []),
                "output_markdown": str(self.output_llm_md),
                "output_data_json": str(self.output_llm_data_json) if parsed_data is not None else None,
                "parsed_output_ok": parsed_data is not None,
                "response_text_preview": response_text[:1000],
                "raw_llm_response": llm_response,
                "advertencia": (
                    "Este output ha sido generado mediante llm_client. "
                    "En modo mock no se llama a ningún modelo externo. "
                    "No constituye recomendación de inversión ni validación oficial de riesgo."
                )
            }

            with open(self.output_llm_json, "w", encoding="utf-8") as f:
                json.dump(output_json_data, f, ensure_ascii=False, indent=2, default=str)

            return {
                "agent": "risk_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "message": "Agente Riesgo ejecutado correctamente en modo LLM.",
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "context_characters": len(context),
                "outputs": {
                    "markdown": str(self.output_llm_md),
                    "json": str(self.output_llm_json),
                    "data_json": str(self.output_llm_data_json) if parsed_data is not None else None,
                },
                "summary": {
                    "id_decision": self.decision_id,
                    "llm_mode": llm_mode,
                    "response_preview": response_text[:500],
                },
                "missing_optional_context_files": validation.get("missing_optional_context_files", []),
            }

        error_json_data = {
            "id_decision": self.decision_id,
            "agent": "risk_agent",
            "mode": "llm",
            "llm_mode": llm_mode,
            "status": "error",
            "prompt_used": str(self.prompt_path),
            "prompt_characters": len(prompt_text),
            "context_characters": len(context),
            "missing_optional_context_files": validation.get("missing_optional_context_files", []),
            "raw_llm_response": llm_response,
        }

        with open(self.output_llm_json, "w", encoding="utf-8") as f:
            json.dump(error_json_data, f, ensure_ascii=False, indent=2, default=str)

        return {
            "agent": "risk_agent",
            "mode": "llm",
            "llm_mode": llm_mode,
            "status": "error",
            "message": "El LLM devolvió error.",
            "prompt_used": str(self.prompt_path),
            "outputs": {
                "json": str(self.output_llm_json),
            },
            "llm_response": llm_response,
        }

    # ============================================================
    # RUN GENERAL
    # ============================================================

    def run(
        self,
        mode: str = "script",
        llm_mode: str = "mock",
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 10000
    ) -> dict:
        mode = mode.lower().strip()
        _log("INFO", "agent_start", agent="risk_agent", decision_id=self.decision_id, mode=mode, llm_mode=llm_mode)

        if mode == "script":
            result = self.run_script_mode()
        elif mode == "llm":
            result = self.run_llm_mode(llm_mode=llm_mode, model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            result = {"agent": "risk_agent", "status": "error",
                      "message": "Modo de ejecución no reconocido.",
                      "mode_received": mode, "valid_modes": ["script", "llm"]}

        _log("INFO" if result.get("status") == "success" else "ERROR", "agent_end",
             agent="risk_agent", decision_id=self.decision_id, status=result.get("status"))
        return result


def run_risk_agent(
    project_dir: str | Path | None = None,
    decision_id: str = "DECISION_001",
    mode: str = "script",
    llm_mode: str = "mock",
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 6000
) -> dict:
    agent = RiskAgent(project_dir=Path(project_dir) if project_dir else None, decision_id=decision_id)
    return agent.run(
        mode=mode,
        llm_mode=llm_mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


if __name__ == "__main__":
    result = run_risk_agent(mode="script")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
