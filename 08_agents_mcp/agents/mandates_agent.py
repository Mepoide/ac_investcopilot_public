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


class MandatesAgent:
    """
    Mandates Agent / Agente Mandatos & Asset Allocation - InvestCopilot

    Modos disponibles:

    1. script
       Usa el script determinista existente:
       05_mandatos_asset_allocation/outputs_mandatos/generar_output_decision_001_mandatos.py

    2. llm
       Usa mandates_agent_prompt.md + contexto + llm_client.py

    Esta versión:
    - lee el prompt interno;
    - valida solo archivos críticos;
    - trata otros archivos como contexto opcional;
    - mantiene modo script estable;
    - permite probar modo llm en mock;
    - no aprueba operaciones;
    - no sustituye mandato oficial ni revisión humana.
    """

    def __init__(self, project_dir: Path | None = None, decision_id: str = "DECISION_001"):
        if project_dir is None:
            # Este archivo está en:
            # 08_agents_mcp/agents/mandates_agent.py
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
        self.prompt_path = self.prompts_dir / "mandates_agent_prompt.md"

        self.llm_client_dir = self.agent_dir / "llm_client"
        self.llm_client_path = self.llm_client_dir / "llm_client.py"

        self.mandates_dir = self.project_dir / "05_mandatos_asset_allocation"
        self.benchmark_dir = self.mandates_dir / "benchmark"
        self.outputs_dir = self.mandates_dir / "outputs_mandatos"

        self.risk_dir = self.project_dir / "04_portfolio_riesgo"
        self.risk_outputs_dir = self.risk_dir / "outputs_riesgo"
        self.risk_metricas_dir = self.risk_dir / "metricas"

        self.generator_script = self.outputs_dir / "generar_output_decision_001_mandatos.py"

        self.output_md = self.outputs_dir / f"{decision_id}_mandatos.md"
        self.output_json = self.outputs_dir / f"{decision_id}_mandatos.json"

        self.output_llm_md = self.outputs_dir / f"{decision_id}_mandatos_llm.md"
        self.output_llm_json = self.outputs_dir / f"{decision_id}_mandatos_llm.json"
        self.output_llm_data_json = self.outputs_dir / f"{decision_id}_mandatos_llm_data.json"

        self.required_inputs_script = [
            self.prompt_path,
            self.generator_script,
        ]

        self.required_inputs_llm = [
            self.prompt_path,
            self.llm_client_path,
        ]

        self.context_files = [
            self.decision_path,

            self.mandates_dir / "marco_control_prototipo_bam.md",
            self.mandates_dir / "reglas_control_prototipo_bam.json",

            self.benchmark_dir / "benchmark_stoxx_usa_900_tr_pesos.csv",
            self.benchmark_dir / "benchmark_stoxx_usa_900_tr_pesos_sector.csv",
            self.benchmark_dir / "comparativa_bam_vs_stoxx_usa_900_tr.csv",
            self.benchmark_dir / "comparativa_bam_vs_stoxx_usa_900_tr_sector.csv",
            self.benchmark_dir / "validacion_benchmark_stoxx_usa_900_tr.md",

            self.risk_metricas_dir / "escenario_bam_tecnologia_plus3_posiciones.csv",
            self.risk_metricas_dir / "escenario_bam_tecnologia_plus3_pesos_sector.csv",
            self.risk_metricas_dir / "metricas_riesgo_bam_vs_escenario.csv",

            self.risk_outputs_dir / f"{decision_id}_riesgo.md",
            self.risk_outputs_dir / f"{decision_id}_riesgo.json",
        ]

    # ============================================================
    # LECTURA Y VALIDACIÓN
    # ============================================================

    def read_prompt(self) -> str:
        """
        Lee el prompt interno del Agente Mandatos.
        """

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"No se encuentra el prompt del Mandates Agent: {self.prompt_path}"
            )

        return self.prompt_path.read_text(encoding="utf-8", errors="ignore")

    def validate_inputs(self, mode: str = "script") -> dict:
        """
        Valida inputs críticos y detecta archivos opcionales faltantes.
        """

        mode = mode.lower().strip()

        if mode == "script":
            required = self.required_inputs_script
        elif mode == "llm":
            required = self.required_inputs_llm
        else:
            return {
                "agent": "mandates_agent",
                "status": "error",
                "message": "Modo no reconocido.",
                "mode": mode,
                "valid_modes": ["script", "llm"],
            }

        missing_required = [
            str(path)
            for path in required
            if not path.exists()
        ]

        missing_context = [
            str(path)
            for path in self.context_files
            if not path.exists()
        ]

        return {
            "agent": "mandates_agent",
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
        """
        Ejecuta el agente en modo script determinista.
        """
        if self.decision_id != "DECISION_001":
            return {
                "agent": "mandates_agent",
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
                "agent": "mandates_agent",
                "mode": "script",
                "status": "error",
                "message": "Faltan inputs críticos para ejecutar el Agente Mandatos en modo script.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "mandates_agent",
                "mode": "script",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Mandatos.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        try:
            runpy.run_path(str(self.generator_script), run_name="__main__")
        except Exception as e:
            return {
                "agent": "mandates_agent",
                "mode": "script",
                "status": "error",
                "message": "Error ejecutando el script generador de mandatos.",
                "generator_script": str(self.generator_script),
                "error": str(e),
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "missing_optional_context_files": validation.get("missing_optional_context_files", []),
            }

        if not self.output_md.exists() or not self.output_json.exists():
            return {
                "agent": "mandates_agent",
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

        try:
            with open(self.output_json, "r", encoding="utf-8") as f:
                output_data = json.load(f)
        except Exception as e:
            return {
                "agent": "mandates_agent",
                "mode": "script",
                "status": "error",
                "message": "Se generó el JSON de mandatos, pero no se pudo leer.",
                "json_path": str(self.output_json),
                "error": str(e),
            }

        return {
            "agent": "mandates_agent",
            "mode": "script",
            "status": "success",
            "message": "Agente Mandatos ejecutado correctamente en modo script.",
            "prompt_used": str(self.prompt_path),
            "prompt_characters": len(prompt_text),
            "outputs": {
                "markdown": str(self.output_md),
                "json": str(self.output_json),
            },
            "summary": {
                "id_decision": output_data.get("id_decision"),
                "resultado_preliminar": output_data.get("resultado_preliminar"),
                "fondo": output_data.get("fondo"),
                "benchmark": output_data.get("benchmark"),
                "validacion_regla_real_conocida": output_data.get("validacion_regla_real_conocida"),
                "peso_it_actual_bam": output_data.get("peso_it_actual_bam"),
                "peso_it_escenario_bam": output_data.get("peso_it_escenario_bam"),
                "peso_benchmark_tecnologia": output_data.get("peso_benchmark_tecnologia"),
                "desviacion_it_actual_vs_benchmark": output_data.get("desviacion_it_actual_vs_benchmark"),
                "desviacion_it_escenario_vs_benchmark": output_data.get("desviacion_it_escenario_vs_benchmark"),
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
        max_tokens: int = 6000
    ) -> dict:
        """
        Ejecuta el agente en modo LLM usando llm_client.
        """

        validation = self.validate_inputs(mode="llm")

        if validation["status"] != "ok":
            return {
                "agent": "mandates_agent",
                "mode": "llm",
                "status": "error",
                "message": "Faltan inputs críticos para ejecutar el Agente Mandatos en modo LLM.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "mandates_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Mandatos.",
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
                "agent": "mandates_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido importar llm_client.",
                "llm_client_path": str(self.llm_client_path),
                "error": str(e),
            }

        risk_outputs_dir = self.project_dir / "04_portfolio_riesgo" / "outputs_riesgo"

        MANDATES_TOOLS = [{"functionDeclarations": [
            {
                "name": "leer_output_riesgo",
                "description": (
                    "Lee el análisis ya generado por el Agente Riesgo para esta decisión. "
                    "Úsalo para ver las métricas de riesgo calculadas (VaR, vol, tracking error, "
                    "drawdown) antes de evaluar el cumplimiento de mandato."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "calcular_escenario_sectorial",
                "description": (
                    "Calcula el impacto real en tracking error, beta y otras métricas de riesgo "
                    "de cambiar el peso de UN sector GICS de la cartera BAM en +/- delta_pp "
                    "puntos porcentuales. Úsala para cuantificar desviación vs benchmark tras "
                    "el cambio propuesto."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "sector": {"type": "STRING"},
                        "delta_pp": {"type": "NUMBER"},
                    },
                    "required": ["sector", "delta_pp"],
                },
            },
            {
                "name": "calcular_escenario_multisector",
                "description": (
                    "Calcula el impacto en tracking error y riesgo de cambiar VARIOS sectores "
                    "a la vez. Úsala cuando la hipótesis implique movimientos en más de un sector."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "cambios": {
                            "type": "ARRAY",
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
                    "interés o spread de crédito, usando duración modificada y OAS. "
                    "Úsala cuando la hipótesis implique bonos, deuda pública o privada, "
                    "tipos de interés, spread de crédito, o duración."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "tipo_shock": {
                            "type": "STRING",
                            "description": "Tipo de shock: 'tipos_paralelo' o 'spread_credito'.",
                        },
                        "magnitud_pb": {
                            "type": "NUMBER",
                            "description": "Magnitud del shock en puntos básicos. Positivo = subida, negativo = bajada.",
                        },
                    },
                    "required": ["tipo_shock", "magnitud_pb"],
                },
            },
        ]}]

        def _ejecutar_tool_mandatos(nombre: str, args: dict) -> dict:
            try:
                if nombre == "leer_output_riesgo":
                    path = risk_outputs_dir / f"{self.decision_id}_riesgo_llm.md"
                    if not path.exists():
                        path = risk_outputs_dir / f"{self.decision_id}_riesgo.md"
                    if not path.exists():
                        return {"error": "Output del Agente Riesgo no disponible aún."}
                    return {"contenido": path.read_text(encoding="utf-8", errors="ignore")[:10000]}
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
                title=f"Contexto Mandates Agent - {self.decision_id}",
                max_chars_per_file=5000,
            )

            llm_response = call_llm_with_tools(
                system_prompt=prompt_text,
                user_context=context,
                tools=MANDATES_TOOLS,
                tool_executor_fn=_ejecutar_tool_mandatos,
                mode=llm_mode,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_context_chars=30000,
            )

        except Exception as e:
            return {
                "agent": "mandates_agent",
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
                "agent": "mandates_agent",
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
                    "No constituye aprobación, recomendación de inversión ni validación oficial de mandato."
                ),
            }

            with open(self.output_llm_json, "w", encoding="utf-8") as f:
                json.dump(output_json_data, f, ensure_ascii=False, indent=2, default=str)

            return {
                "agent": "mandates_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "message": "Agente Mandatos ejecutado correctamente en modo LLM.",
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
            "agent": "mandates_agent",
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
            "agent": "mandates_agent",
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
        max_tokens: int = 6000
    ) -> dict:
        """
        Ejecuta el agente en modo script o llm.
        """

        mode = mode.lower().strip()
        _log("INFO", "agent_start", agent="mandates_agent", decision_id=self.decision_id, mode=mode, llm_mode=llm_mode)

        if mode == "script":
            result = self.run_script_mode()
        elif mode == "llm":
            result = self.run_llm_mode(llm_mode=llm_mode, model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            result = {
                "agent": "mandates_agent",
                "status": "error",
                "message": "Modo de ejecución no reconocido.",
                "mode_received": mode,
                "valid_modes": ["script", "llm"],
            }

        _log("INFO" if result.get("status") == "success" else "ERROR", "agent_end",
             agent="mandates_agent", decision_id=self.decision_id, status=result.get("status"))
        return result


def run_mandates_agent(
    project_dir: str | Path | None = None,
    decision_id: str = "DECISION_001",
    mode: str = "script",
    llm_mode: str = "mock",
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 6000
) -> dict:
    """
    Función auxiliar para ejecutar MandatesAgent desde otros scripts.
    """

    agent = MandatesAgent(project_dir=Path(project_dir) if project_dir else None, decision_id=decision_id)

    return agent.run(
        mode=mode,
        llm_mode=llm_mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


if __name__ == "__main__":
    result = run_mandates_agent(mode="script")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
