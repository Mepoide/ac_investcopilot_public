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


class SynthesisAgent:
    """
    Synthesis Agent / Agente Sintesis / Comite Virtual - InvestCopilot.

    Modos disponibles:

    1. script
       Usa el script determinista existente:
       06_sintesis_comite/generar_sintesis_decision_001.py

    2. llm
       Usa synthesis_agent_prompt.md + contexto + llm_client.py

    Esta version:
    - lee el prompt interno;
    - valida solo archivos criticos;
    - trata otros archivos como contexto opcional;
    - mantiene modo script estable;
    - permite probar modo llm en mock;
    - no recomienda inversiones;
    - no aprueba operaciones;
    - no sustituye al gestor ni al comite.
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
        self.prompt_path = self.prompts_dir / "synthesis_agent_prompt.md"

        self.llm_client_dir = self.agent_dir / "llm_client"
        self.llm_client_path = self.llm_client_dir / "llm_client.py"

        self.research_outputs_dir = self.project_dir / "02_research" / "outputs_research"
        self.macro_outputs_dir = self.project_dir / "03_macro_houseview" / "outputs_macro"
        self.risk_outputs_dir = self.project_dir / "04_portfolio_riesgo" / "outputs_riesgo"
        self.mandates_outputs_dir = self.project_dir / "05_mandatos_asset_allocation" / "outputs_mandatos"

        self.synthesis_dir = self.project_dir / "06_sintesis_comite"

        self.generator_script = self.synthesis_dir / "generar_sintesis_decision_001.py"

        self.output_md = self.synthesis_dir / f"{decision_id}_sintesis.md"
        self.output_json = self.synthesis_dir / f"{decision_id}_sintesis.json"

        self.output_llm_md = self.synthesis_dir / f"{decision_id}_sintesis_llm.md"
        self.output_llm_json = self.synthesis_dir / f"{decision_id}_sintesis_llm.json"
        self.output_llm_data_json = self.synthesis_dir / f"{decision_id}_sintesis_llm_data.json"

        self.required_inputs_script = [
            self.prompt_path,
            self.generator_script,
        ]

        self.required_inputs_llm = [
            self.prompt_path,
            self.llm_client_path,
        ]

        # Se incluyen tanto los outputs de script (solo existen para
        # DECISION_001) como los de LLM (existen para cualquier decision_id):
        # los que no existan se omiten del contexto sin romper el agente.
        self.context_files = [
            self.decision_path,

            self.research_outputs_dir / f"{decision_id}_research_llm_data.json",

            self.macro_outputs_dir / f"{decision_id}_macro.md",
            self.macro_outputs_dir / f"{decision_id}_macro.json",
            self.macro_outputs_dir / f"{decision_id}_macro_llm_data.json",

            self.risk_outputs_dir / f"{decision_id}_riesgo.md",
            self.risk_outputs_dir / f"{decision_id}_riesgo.json",
            self.risk_outputs_dir / f"{decision_id}_riesgo_llm_data.json",

            self.mandates_outputs_dir / f"{decision_id}_mandatos.md",
            self.mandates_outputs_dir / f"{decision_id}_mandatos.json",
            self.mandates_outputs_dir / f"{decision_id}_mandatos_llm_data.json",

            self.project_dir / "00_contexto" / "03_resumen_para_agentes" / "contexto_base_para_agentes.md",
            self.project_dir / "00_contexto" / "03_resumen_para_agentes" / "reglas_generales_de_respuesta.md",
            self.project_dir / "00_contexto" / "03_resumen_para_agentes" / "limitaciones_del_prototipo.md",
        ]

    # ============================================================
    # LECTURA Y VALIDACION
    # ============================================================

    def read_prompt(self) -> str:
        """
        Lee el prompt interno del Agente Sintesis.
        """

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"No se encuentra el prompt del Synthesis Agent: {self.prompt_path}"
            )

        return self.prompt_path.read_text(encoding="utf-8", errors="ignore")

    def validate_inputs(self, mode: str = "script") -> dict:
        """
        Valida inputs criticos y detecta archivos opcionales faltantes.
        """

        mode = mode.lower().strip()

        if mode == "script":
            required = self.required_inputs_script
        elif mode == "llm":
            required = self.required_inputs_llm
        else:
            return {
                "agent": "synthesis_agent",
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
            "agent": "synthesis_agent",
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
                "agent": "synthesis_agent",
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
                "agent": "synthesis_agent",
                "mode": "script",
                "status": "error",
                "message": "Faltan inputs criticos para ejecutar el Agente Sintesis en modo script.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "synthesis_agent",
                "mode": "script",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Sintesis.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        self.synthesis_dir.mkdir(parents=True, exist_ok=True)

        try:
            runpy.run_path(str(self.generator_script), run_name="__main__")
        except Exception as e:
            return {
                "agent": "synthesis_agent",
                "mode": "script",
                "status": "error",
                "message": "Error ejecutando el script generador de sintesis.",
                "generator_script": str(self.generator_script),
                "error": str(e),
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "missing_optional_context_files": validation.get("missing_optional_context_files", []),
            }

        if not self.output_md.exists() or not self.output_json.exists():
            return {
                "agent": "synthesis_agent",
                "mode": "script",
                "status": "error",
                "message": "El script se ejecuto, pero no se generaron todos los outputs esperados.",
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
                "agent": "synthesis_agent",
                "mode": "script",
                "status": "error",
                "message": "Se genero el JSON de sintesis, pero no se pudo leer.",
                "json_path": str(self.output_json),
                "error": str(e),
            }

        return {
            "agent": "synthesis_agent",
            "mode": "script",
            "status": "success",
            "message": "Agente Sintesis ejecutado correctamente en modo script.",
            "prompt_used": str(self.prompt_path),
            "prompt_characters": len(prompt_text),
            "outputs": {
                "markdown": str(self.output_md),
                "json": str(self.output_json),
            },
            "summary": {
                "id_decision": output_data.get("id_decision"),
                "clasificacion_consolidada": output_data.get("clasificacion_consolidada"),
                "resumen_clasificacion": output_data.get("resumen_clasificacion"),
                "alertas_consolidadas": output_data.get("alertas_consolidadas", []),
                "informacion_faltante_consolidada": output_data.get("informacion_faltante_consolidada", []),
                "conclusion": output_data.get("conclusion"),
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
        max_tokens: int = 8000
    ) -> dict:
        """
        Ejecuta el agente en modo LLM usando llm_client.
        """

        validation = self.validate_inputs(mode="llm")

        if validation["status"] != "ok":
            return {
                "agent": "synthesis_agent",
                "mode": "llm",
                "status": "error",
                "message": "Faltan inputs criticos para ejecutar el Agente Sintesis en modo LLM.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "synthesis_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Sintesis.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        if str(self.llm_client_dir) not in sys.path:
            sys.path.append(str(self.llm_client_dir))

        try:
            from llm_client import call_llm_with_tools, build_context_from_files, extract_json_block
        except Exception as e:
            return {
                "agent": "synthesis_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido importar llm_client.",
                "llm_client_path": str(self.llm_client_path),
                "error": str(e),
            }

        # Rutas de outputs de agentes de dominio (para que Synthesis pueda
        # releer bajo demanda en vez de solo lo preinyectado en contexto).
        _agent_output_dirs = {
            "research": self.research_outputs_dir,
            "macro": self.macro_outputs_dir,
            "risk": self.risk_outputs_dir,
            "mandates": self.mandates_outputs_dir,
        }
        _decision_id = self.decision_id
        _project_dir = self.project_dir

        SYNTHESIS_TOOLS = [{"functionDeclarations": [
            {
                "name": "leer_output_agente",
                "description": (
                    "Lee el output markdown de un agente de dominio ya ejecutado. "
                    "Úsalo para releer en detalle el análisis de research, macro, risk o mandates "
                    "cuando necesites más detalle del que tienes en contexto. "
                    "agente: 'research' | 'macro' | 'risk' | 'mandates'."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "agente": {
                            "type": "STRING",
                            "description": "Nombre del agente: research, macro, risk o mandates.",
                        }
                    },
                    "required": ["agente"],
                },
            },
            {
                "name": "leer_archivo_texto",
                "description": (
                    "Lee el contenido de cualquier archivo de texto o markdown del proyecto. "
                    "Rutas relativas a la raíz del proyecto."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "ruta": {"type": "STRING", "description": "Ruta relativa al directorio raíz del proyecto."}
                    },
                    "required": ["ruta"],
                },
            },
        ]}]

        _output_file_map = {
            "research": _agent_output_dirs["research"] / f"{_decision_id}_research_llm.md",
            "macro": _agent_output_dirs["macro"] / f"{_decision_id}_macro_llm.md",
            "risk": _agent_output_dirs["risk"] / f"{_decision_id}_riesgo_llm.md",
            "mandates": _agent_output_dirs["mandates"] / f"{_decision_id}_mandatos_llm.md",
        }

        def _ejecutar_tool_synthesis(nombre: str, args: dict) -> dict:
            try:
                if nombre == "leer_output_agente":
                    agente = args.get("agente", "").lower()
                    path = _output_file_map.get(agente)
                    if path is None:
                        return {"error": f"Agente no reconocido: {agente}. Válidos: research, macro, risk, mandates."}
                    if not path.exists():
                        return {"error": f"Output de {agente} no disponible aún: {path.name}"}
                    return {"agente": agente, "contenido": path.read_text(encoding="utf-8", errors="ignore")[:10000]}
                if nombre == "leer_archivo_texto":
                    ruta = _project_dir / args.get("ruta", "")
                    if not ruta.exists():
                        return {"error": f"Archivo no encontrado: {args.get('ruta')}"}
                    return {"contenido": ruta.read_text(encoding="utf-8", errors="ignore")[:8000]}
            except Exception as e:
                return {"error": str(e)}
            return {"error": f"Tool no reconocida: {nombre}"}

        try:
            existing_context_files = [
                path
                for path in self.context_files
                if path.exists()
            ]

            context = build_context_from_files(
                files=existing_context_files,
                title=f"Contexto Synthesis Agent - {self.decision_id}",
                max_chars_per_file=5000,
            )

            llm_response = call_llm_with_tools(
                system_prompt=prompt_text,
                user_context=context,
                tools=SYNTHESIS_TOOLS,
                tool_executor_fn=_ejecutar_tool_synthesis,
                mode=llm_mode,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_context_chars=35000,
            )

        except Exception as e:
            return {
                "agent": "synthesis_agent",
                "mode": "llm",
                "status": "error",
                "message": "Error construyendo contexto o llamando al LLM.",
                "error": str(e),
            }

        self.synthesis_dir.mkdir(parents=True, exist_ok=True)

        if llm_response.get("status") == "success":
            response_text = llm_response.get("data", {}).get("response_text", "")

            self.output_llm_md.write_text(response_text, encoding="utf-8")

            parsed_data = extract_json_block(response_text)

            if parsed_data is not None:
                with open(self.output_llm_data_json, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2, default=str)

            output_json_data = {
                "id_decision": self.decision_id,
                "agent": "synthesis_agent",
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
                    "En modo mock no se llama a ningun modelo externo. "
                    "No constituye recomendacion, aprobacion ni instruccion de ejecucion."
                ),
            }

            with open(self.output_llm_json, "w", encoding="utf-8") as f:
                json.dump(output_json_data, f, ensure_ascii=False, indent=2, default=str)

            return {
                "agent": "synthesis_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "message": "Agente Sintesis ejecutado correctamente en modo LLM.",
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
            "agent": "synthesis_agent",
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
            "agent": "synthesis_agent",
            "mode": "llm",
            "llm_mode": llm_mode,
            "status": "error",
            "message": "El LLM devolvio error.",
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
        max_tokens: int = 8000
    ) -> dict:
        """
        Ejecuta el agente en modo script o llm.
        """

        mode = mode.lower().strip()
        _log("INFO", "agent_start", agent="synthesis_agent", decision_id=self.decision_id, mode=mode, llm_mode=llm_mode)

        if mode == "script":
            result = self.run_script_mode()
        elif mode == "llm":
            result = self.run_llm_mode(llm_mode=llm_mode, model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            result = {"agent": "synthesis_agent", "status": "error",
                      "message": "Modo de ejecucion no reconocido.",
                      "mode_received": mode, "valid_modes": ["script", "llm"]}

        _log("INFO" if result.get("status") == "success" else "ERROR", "agent_end",
             agent="synthesis_agent", decision_id=self.decision_id, status=result.get("status"))
        return result


def run_synthesis_agent(
    project_dir: str | Path | None = None,
    decision_id: str = "DECISION_001",
    mode: str = "script",
    llm_mode: str = "mock",
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 8000
) -> dict:
    """
    Funcion auxiliar para ejecutar SynthesisAgent desde otros scripts.
    """

    agent = SynthesisAgent(project_dir=Path(project_dir) if project_dir else None, decision_id=decision_id)

    return agent.run(
        mode=mode,
        llm_mode=llm_mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )


if __name__ == "__main__":
    result = run_synthesis_agent(mode="script")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))