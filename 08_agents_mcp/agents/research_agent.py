from pathlib import Path
import json
import sys

_AGENTS_MCP_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_MCP_DIR))
try:
    from log_util import log as _log
except ImportError:
    def _log(*args, **kwargs): pass

# Google Search grounding nativo de Gemini 2.x en Vertex AI.
# No requiere API key separada ni PSE — usa la misma auth de Vertex AI.
# En mock mode se ignora y el LLM devuelve respuesta simulada.
_GROUNDING_TOOL = [{"google_search": {}}]


class ResearchAgent:
    """
    Research Agent - InvestCopilot

    Agente de research con Google Search grounding nativo (Gemini 2.x):
    el LLM busca en tiempo real durante la generación de la respuesta,
    sin loop de function calling ni API key de búsqueda adicional.

    Solo soporta modo "llm". En mock (llm_mode="mock") no hay búsqueda real.

    Importante:
    - No valida límites de mandato ni Asset Allocation.
    - No calcula métricas de riesgo.
    - No emite recomendación de inversión.
    - La decisión final es humana.
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
        self.prompt_path = self.prompts_dir / "research_agent_prompt.md"

        self.llm_client_dir = self.agent_dir / "llm_client"
        self.llm_client_path = self.llm_client_dir / "llm_client.py"

        self.research_dir = self.project_dir / "02_research"
        self.outputs_dir = self.research_dir / "outputs_research"

        self.output_llm_md = self.outputs_dir / f"{decision_id}_research_llm.md"
        self.output_llm_json = self.outputs_dir / f"{decision_id}_research_llm.json"
        self.output_llm_data_json = self.outputs_dir / f"{decision_id}_research_llm_data.json"

        self.required_inputs_llm = [self.prompt_path, self.llm_client_path]

        self.context_files = [
            self.decision_path,
            self.project_dir / "00_contexto" / "03_resumen_para_agentes" / "contexto_base_para_agentes.md",
            self.project_dir / "00_contexto" / "03_resumen_para_agentes" / "reglas_generales_de_respuesta.md",
            self.project_dir / "00_contexto" / "03_resumen_para_agentes" / "limitaciones_del_prototipo.md",
        ]

    # ============================================================
    # LECTURA Y VALIDACIÓN
    # ============================================================

    def read_prompt(self) -> str:
        if not self.prompt_path.exists():
            raise FileNotFoundError(f"No se encuentra el prompt del Research Agent: {self.prompt_path}")
        return self.prompt_path.read_text(encoding="utf-8", errors="ignore")

    def validate_inputs(self, mode: str = "llm") -> dict:
        mode = mode.lower().strip()
        if mode != "llm":
            return {
                "agent": "research_agent",
                "status": "error",
                "message": "Research Agent solo soporta modo 'llm'.",
                "mode": mode,
                "valid_modes": ["llm"],
            }
        missing = [str(p) for p in self.required_inputs_llm if not p.exists()]
        return {
            "agent": "research_agent",
            "mode": mode,
            "status": "ok" if not missing else "missing_inputs",
            "missing_inputs": missing,
            "required_inputs": [str(p) for p in self.required_inputs_llm],
            "prompt_path": str(self.prompt_path),
        }

    # ============================================================
    # PARSEAR FUENTES DEL GROUNDING METADATA
    # ============================================================

    @staticmethod
    def _parse_grounding_sources(grounding_metadata: dict) -> list[dict]:
        """Extrae título + URL de groundingChunks."""
        sources = []
        for chunk in grounding_metadata.get("groundingChunks", []):
            web = chunk.get("web", {})
            uri = web.get("uri", "")
            title = web.get("title", "")
            if uri:
                sources.append({"title": title, "url": uri})
        return sources

    # ============================================================
    # MODO LLM
    # ============================================================

    def run_llm_mode(
        self,
        llm_mode: str = "mock",
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 6000,
    ) -> dict:
        validation = self.validate_inputs(mode="llm")
        if validation["status"] != "ok":
            return {
                "agent": "research_agent",
                "mode": "llm",
                "status": "error",
                "message": "Faltan inputs necesarios para ejecutar el Research Agent.",
                "details": validation,
            }

        try:
            prompt_text = self.read_prompt()
        except Exception as e:
            return {
                "agent": "research_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido leer el prompt del Research Agent.",
                "prompt_path": str(self.prompt_path),
                "error": str(e),
            }

        if str(self.llm_client_dir) not in sys.path:
            sys.path.append(str(self.llm_client_dir))

        try:
            from llm_client import call_llm, build_context_from_files, extract_json_block
        except Exception as e:
            return {
                "agent": "research_agent",
                "mode": "llm",
                "status": "error",
                "message": "No se ha podido importar llm_client.",
                "llm_client_path": str(self.llm_client_path),
                "error": str(e),
            }

        existing_context_files = [p for p in self.context_files if p.exists()]

        try:
            context = build_context_from_files(
                files=existing_context_files,
                title=f"Contexto Research Agent - {self.decision_id}",
                max_chars_per_file=6000,
            )

            # Grounding tool solo aplica en vertex_ai; en otros modos call_llm lo ignora
            llm_response = call_llm(
                system_prompt=prompt_text,
                user_context=context,
                mode=llm_mode,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                max_context_chars=25000,
                tools=_GROUNDING_TOOL,
            )
        except Exception as e:
            return {
                "agent": "research_agent",
                "mode": "llm",
                "status": "error",
                "message": "Error construyendo contexto o llamando al LLM.",
                "error": str(e),
            }

        self.outputs_dir.mkdir(parents=True, exist_ok=True)

        if llm_response.get("status") == "success":
            response_text = llm_response.get("data", {}).get("response_text", "")
            grounding_metadata = llm_response.get("data", {}).get("grounding_metadata", {})
            sources = self._parse_grounding_sources(grounding_metadata)
            web_queries = grounding_metadata.get("webSearchQueries", [])

            self.output_llm_md.write_text(response_text, encoding="utf-8")

            parsed_data = extract_json_block(response_text)
            if parsed_data is not None:
                # Inyecta fuentes reales si el JSON no las incluye
                if isinstance(parsed_data, dict) and not parsed_data.get("fuentes_web"):
                    parsed_data["fuentes_web"] = sources
                with open(self.output_llm_data_json, "w", encoding="utf-8") as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2, default=str)

            output_json_data = {
                "id_decision": self.decision_id,
                "agent": "research_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "context_characters": len(context),
                "context_files_used": [str(p) for p in existing_context_files],
                "grounding_used": llm_mode == "vertex_ai",
                "web_queries": web_queries,
                "sources": sources,
                "output_markdown": str(self.output_llm_md),
                "output_data_json": str(self.output_llm_data_json) if parsed_data is not None else None,
                "parsed_output_ok": parsed_data is not None,
                "response_text_preview": response_text[:1000],
                "raw_llm_response": llm_response,
                "advertencia": (
                    "Output generado por LLM con Google Search grounding (vertex_ai) "
                    "o simulado (mock). No constituye research real ni recomendación de inversión."
                ),
            }

            with open(self.output_llm_json, "w", encoding="utf-8") as f:
                json.dump(output_json_data, f, ensure_ascii=False, indent=2, default=str)

            return {
                "agent": "research_agent",
                "mode": "llm",
                "llm_mode": llm_mode,
                "status": "success",
                "message": "Research Agent ejecutado correctamente.",
                "prompt_used": str(self.prompt_path),
                "prompt_characters": len(prompt_text),
                "context_characters": len(context),
                "grounding_used": llm_mode == "vertex_ai",
                "web_queries_count": len(web_queries),
                "sources_count": len(sources),
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

        error_json_data = {
            "id_decision": self.decision_id,
            "agent": "research_agent",
            "mode": "llm",
            "llm_mode": llm_mode,
            "status": "error",
            "prompt_used": str(self.prompt_path),
            "raw_llm_response": llm_response,
        }
        with open(self.output_llm_json, "w", encoding="utf-8") as f:
            json.dump(error_json_data, f, ensure_ascii=False, indent=2, default=str)

        return {
            "agent": "research_agent",
            "mode": "llm",
            "llm_mode": llm_mode,
            "status": "error",
            "message": "El LLM devolvió error.",
            "prompt_used": str(self.prompt_path),
            "outputs": {"json": str(self.output_llm_json)},
            "llm_response": llm_response,
        }

    # ============================================================
    # RUN GENERAL
    # ============================================================

    def run(
        self,
        mode: str = "llm",
        llm_mode: str = "mock",
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 6000,
    ) -> dict:
        mode = mode.lower().strip()
        _log("INFO", "agent_start", agent="research_agent", decision_id=self.decision_id, mode=mode, llm_mode=llm_mode)

        if mode == "llm":
            result = self.run_llm_mode(llm_mode=llm_mode, model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            result = {
                "agent": "research_agent",
                "status": "error",
                "message": "Research Agent solo soporta modo 'llm'.",
                "mode_received": mode,
                "valid_modes": ["llm"],
            }

        _log("INFO" if result.get("status") == "success" else "ERROR", "agent_end",
             agent="research_agent", decision_id=self.decision_id, status=result.get("status"))
        return result


def run_research_agent(
    project_dir: str | Path | None = None,
    decision_id: str = "DECISION_001",
    mode: str = "llm",
    llm_mode: str = "mock",
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 6000,
) -> dict:
    agent = ResearchAgent(project_dir=Path(project_dir) if project_dir else None, decision_id=decision_id)
    return agent.run(mode=mode, llm_mode=llm_mode, model=model, temperature=temperature, max_tokens=max_tokens)


if __name__ == "__main__":
    result = run_research_agent(mode="llm", llm_mode="mock")
    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
