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


class MacroAgent:
    """
    Macro Agent / House View Agent - InvestCopilot

    Este agente puede funcionar en dos modos:

    1. script
       Usa el script determinista existente:
       03_macro_houseview/outputs_macro/generar_output_decision_001_macro.py

    2. llm
       Lee el prompt interno, construye contexto con archivos macro y llama a:
       08_agents_mcp/llm_client/llm_client.py

    Por defecto usa modo script para mantener la demo estable.

    Importante:
    - No recomienda inversiones.
    - No ejecuta operaciones.
    - No sustituye el House View oficial.
    - La decisión final es humana.
    """

    def __init__(self, project_dir: Path | None = None, decision_id: str = "DECISION_001"):
        if project_dir is None:
            self.project_dir = Path(__file__).resolve().parents[2]
        else:
            self.project_dir = Path(project_dir)

        self.decision_id = decision_id

        # DECISION_001 es el caso de demo precalculado, con su propio archivo
        # fijo. Cualquier otra decision_id (creada vía la web o a discreción
        # del gestor) vive en 01_decision_input/decisiones/{decision_id}.json.
        if decision_id == "DECISION_001":
            self.decision_path = self.project_dir / "01_decision_input" / "decision_actual.json"
        else:
            self.decision_path = self.project_dir / "01_decision_input" / "decisiones" / f"{decision_id}.json"

        self.agent_dir = self.project_dir / "08_agents_mcp"
        self.prompts_dir = self.agent_dir / "prompts"
        self.prompt_path = self.prompts_dir / "macro_agent_prompt.md"

        self.llm_client_dir = self.agent_dir / "llm_client"
        self.llm_client_path = self.llm_client_dir / "llm_client.py"

        self.macro_dir = self.project_dir / "03_macro_houseview"
        self.outputs_dir = self.macro_dir / "outputs_macro"

        self.generator_script = self.outputs_dir / "generar_output_decision_001_macro.py"

        self.output_md = self.outputs_dir / f"{decision_id}_macro.md"
        self.output_json = self.outputs_dir / f"{decision_id}_macro.json"

        self.output_llm_md = self.outputs_dir / f"{decision_id}_macro_llm.md"
        self.output_llm_json = self.outputs_dir / f"{decision_id}_macro_llm.json"
        self.output_llm_data_json = self.outputs_dir / f"{decision_id}_macro_llm_data.json"

        self.context_files = [
            self.decision_path,
            self.macro_dir / "house_view_base.md",
            self.macro_dir / "escenarios_macro.json",
            self.macro_dir / "indicadores_macro.csv",
            self.macro_dir / "supuestos_macro.json",
            self.macro_dir / "notas_macro" / "nota_tecnologia_usa.md",
        ]

        self.required_inputs_script = [
            self.prompt_path,
            self.decision_path,
            self.macro_dir / "house_view_base.md",
            self.macro_dir / "escenarios_macro.json",
            self.macro_dir / "indicadores_macro.csv",
            self.macro_dir / "supuestos_macro.json",
            self.macro_dir / "notas_macro" / "nota_tecnologia_usa.md",
            self.generator_script,
        ]

        self.required_inputs_llm = [
            self.prompt_path,
            self.llm_client_path,
            self.decision_path,
            self.macro_dir / "house_view_base.md",
            self.macro_dir / "escenarios_macro.json",
            self.macro_dir / "indicadores_macro.csv",
            self.macro_dir / "supuestos_macro.json",
            self.macro_dir / "notas_macro" / "nota_tecnologia_usa.md",
        ]

    # ============================================================
    # LECTURA Y VALIDACIÓN
    # ============================================================

    def read_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"No se encuentra el prompt del Macro Agent: {self.prompt_path}")

        return self.prompt_path.read_text(encoding="utf-8", errors="ignore")

    def validate_inputs(self, mode: str = "script") -> dict:
        mode = mode.lower().strip()

        if mode == "script":
            required = self.required_inputs_script
        elif mode == "llm":
            required = self.required_inputs_llm
        else:
            return {
                "agent": "macro_agent",
                "status": "error",
                "message": "Modo no reconocido.",
                "mode": mode,
                "valid_modes": ["script", "llm"]
            }

        missing = [str(path) for path in required if not path.exists()]

        return {
            "agent": "macro_agent",
            "mode": mode,
            "status": "ok" if not missing else "missing_inputs",
            "missing_inputs": missing,
            "required_inputs": [str(path) for path in required],
            "prompt_path": str(self.prompt_path),
        }

    # ============================================================
    # MODO SCRIPT
    # ============================================================

    def run_script_mode(self) -> dict:
        if self.decision_id != "DECISION_001":
            return {
                "agent": "macro_agent",
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
                "agent": "macro_agent",
                "mode": "script",
                "status": "error",
                "message": "Faltan inputs necesarios para ejecutar el Agente Macro en modo script.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "macro_agent",
                "mode": "script",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Macro.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        runpy.run_path(str(self.generator_script), run_name="__main__")

        if not self.output_md.exists() or not self.output_json.exists():
            return {
                "agent": "macro_agent",
                "mode": "script",
                "status": "error",
                "message": "El script se ejecutó, pero no se generaron todos los outputs esperados.",
                "expected_outputs": [
                    str(self.output_md),
                    str(self.output_json),
                ],
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
            }

        with open(self.output_json, "r", encoding="utf-8") as f:
            output_data = json.load(f)

        return {
            "agent": "macro_agent",
            "mode": "script",
            "status": "success",
            "message": "Agente Macro ejecutado correctamente en modo script.",
            "prompt_used": str(self.prompt_path),
            "prompt_characters": len(prompt_text),
            "outputs": {
                "markdown": str(self.output_md),
                "json": str(self.output_json),
            },
            "summary": {
                "id_decision": output_data.get("id_decision"),
                "clasificacion_macro": output_data.get("clasificacion_macro"),
                "escenario_central": output_data.get("escenario_central"),
                "alertas": output_data.get("alertas", []),
                "conclusion": output_data.get("conclusion"),
            },
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
        validation = self.validate_inputs(mode="llm")

        if validation["status"] != "ok":
            return {
                "agent": "macro_agent",
                "mode": "llm",
                "status": "error",
                "message": "Faltan inputs necesarios para ejecutar el Agente Macro en modo LLM.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "macro_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido leer el prompt interno del Agente Macro.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        if str(self.llm_client_dir) not in sys.path:
            sys.path.append(str(self.llm_client_dir))

        try:
            from llm_client import call_llm, build_context_from_files, extract_json_block
        except Exception as e:
            return {
                "agent": "macro_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido importar llm_client.",
                "llm_client_path": str(self.llm_client_path),
                "error": str(e),
            }

        try:
            context = build_context_from_files(
                files=self.context_files,
                title=f"Contexto Macro Agent - {self.decision_id}",
                max_chars_per_file=6000
            )

            llm_response = call_llm(
                system_prompt=prompt_text,
                user_context=context,
                mode=llm_mode,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_context_chars=25000,
            )

        except Exception as e:
            return {
                "agent": "macro_agent",
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
                "agent": "macro_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "context_characters": len(context),
                "output_markdown": str(self.output_llm_md),
                "output_data_json": str(self.output_llm_data_json) if parsed_data is not None else None,
                "parsed_output_ok": parsed_data is not None,
                "response_text_preview": response_text[:1000],
                "raw_llm_response": llm_response,
                "advertencia": (
                    "Este output ha sido generado mediante llm_client. "
                    "En modo mock no se llama a ningún modelo externo. "
                    "No constituye recomendación de inversión."
                )
            }

            with open(self.output_llm_json, "w", encoding="utf-8") as f:
                json.dump(output_json_data, f, ensure_ascii=False, indent=2, default=str)

            return {
                "agent": "macro_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "message": "Agente Macro ejecutado correctamente en modo LLM.",
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
            }

        else:
            error_json_data = {
                "id_decision": self.decision_id,
                "agent": "macro_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "error",
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "context_characters": len(context),
                "raw_llm_response": llm_response,
            }

            with open(self.output_llm_json, "w", encoding="utf-8") as f:
                json.dump(error_json_data, f, ensure_ascii=False, indent=2, default=str)

            return {
                "agent": "macro_agent",
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
        mode = mode.lower().strip()
        _log("INFO", "agent_start", agent="macro_agent", decision_id=self.decision_id, mode=mode, llm_mode=llm_mode)

        if mode == "script":
            result = self.run_script_mode()
        elif mode == "llm":
            result = self.run_llm_mode(llm_mode=llm_mode, model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            result = {"agent": "macro_agent", "status": "error",
                      "message": "Modo de ejecución no reconocido.",
                      "mode_received": mode, "valid_modes": ["script", "llm"]}

        _log("INFO" if result.get("status") == "success" else "ERROR", "agent_end",
             agent="macro_agent", decision_id=self.decision_id, status=result.get("status"))
        return result


def run_macro_agent(
    project_dir: str | Path | None = None,
    decision_id: str = "DECISION_001",
    mode: str = "script",
    llm_mode: str = "mock",
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 6000
) -> dict:
    agent = MacroAgent(project_dir=Path(project_dir) if project_dir else None, decision_id=decision_id)
    return agent.run(
        mode=mode,
        llm_mode=llm_mode,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
    )


if __name__ == "__main__":
    result = run_macro_agent(mode="script")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))