from pathlib import Path
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime

_AGENTS_MCP_DIR = Path(__file__).resolve().parents[1]
if str(_AGENTS_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(_AGENTS_MCP_DIR))
try:
    from cost_tracker import check_cap, record_llm_call, CostCapExceeded
except ImportError:
    def check_cap(*a, **kw): pass
    def record_llm_call(*a, **kw): return {"status": "ok"}
    class CostCapExceeded(Exception): pass


# ============================================================
# CONFIGURACIÓN
# ============================================================

# Guarda este archivo en:
# 08_agents_mcp/llm_client/llm_client.py
#
# Este cliente LLM está preparado para cuatro modos:
#
# 1. mock
#    No llama a ningún modelo. Devuelve una respuesta simulada.
#
# 2. openai_compatible
#    Llama a un endpoint compatible con OpenAI Chat Completions.
#
# 3. azure_openai
#    Llama a Azure OpenAI usando endpoint, deployment y api-version.
#
# 4. vertex_ai
#    Llama a Vertex AI (Gemini) en Google Cloud.
#
# Por defecto usa modo mock para no romper la demo.
#
# Variables de entorno opcionales (también se pueden poner en un .env
# en la raíz del repo, ver .env.example):
#
# INVESTCOPILOT_LLM_MODE=mock | openai_compatible | azure_openai | vertex_ai
#
# Para openai_compatible:
# OPENAI_API_KEY=...
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4o-mini
#
# Para azure_openai:
# AZURE_OPENAI_API_KEY=...
# AZURE_OPENAI_ENDPOINT=https://xxxxx.openai.azure.com
# AZURE_OPENAI_DEPLOYMENT=...
# AZURE_OPENAI_API_VERSION=2024-02-15-preview
#
# Para vertex_ai:
# GOOGLE_CLOUD_PROJECT=...
# GOOGLE_CLOUD_LOCATION=us-central1
# GOOGLE_VERTEX_MODEL=gemini-2.5-flash
# GOOGLE_ACCESS_TOKEN=...   (dev local: gcloud auth print-access-token)


LLM_CLIENT_DIR = Path(__file__).resolve().parent
AGENTS_MCP_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[2]
# Tras aplanar la estructura de carpetas (sin el wrapper duplicado
# InvestCopilot_AI_Summit/InvestCopilot_AI_Summit), la raíz del repo y la
# raíz del proyecto son el mismo directorio.
REPO_ROOT = PROJECT_DIR


def _load_dotenv(path: Path) -> None:
    """
    Carga variables de un archivo .env en os.environ, sobrescribiendo
    siempre el valor existente.

    Implementación mínima sin dependencias externas. Solo para uso local/dev:
    en cloud las credenciales deben venir de un gestor de secretos (Key Vault +
    managed identity), no de un .env.

    Override siempre (no solo si falta la key): en este proyecto el .env es
    la única fuente de estas variables (nadie las exporta a mano en el
    shell), y GOOGLE_ACCESS_TOKEN rota cada ~1h. Con un proceso de larga
    duración (p.ej. Streamlit, que no se reinicia entre preguntas), si solo
    se rellenara cuando falta, el primer valor cargado quedaría cacheado en
    os.environ para siempre y las regeneraciones del token en disco nunca
    se recogerían — incluido en subprocesos que heredan ese os.environ ya
    obsoleto (como el orquestador lanzado desde la web).
    """
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ[key] = value


_load_dotenv(REPO_ROOT / ".env")


# ============================================================
# RESPUESTAS ESTÁNDAR
# ============================================================

def _ok(data: dict) -> dict:
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "data": data,
    }


def _error(message: str, details: dict | None = None) -> dict:
    return {
        "status": "error",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "message": message,
        "details": details or {},
    }


# ============================================================
# UTILIDADES
# ============================================================

def get_llm_mode() -> str:
    """
    Devuelve el modo de LLM configurado.

    Por defecto usa mock para que la demo funcione sin claves ni llamadas externas.
    """
    return os.getenv("INVESTCOPILOT_LLM_MODE", "mock").strip().lower()


def truncate_text(text: str, max_chars: int = 12000) -> str:
    """
    Recorta un texto si supera max_chars.

    Sirve para evitar enviar prompts o contextos demasiado largos al LLM.
    """
    if text is None:
        return ""

    text = str(text)

    if len(text) <= max_chars:
        return text

    return text[:max_chars] + "\n\n[Texto truncado por longitud]"


def build_messages(system_prompt: str, user_context: str) -> list[dict]:
    """
    Construye mensajes en formato compatible con Chat Completions.
    """
    return [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_context
        }
    ]


_RETRYABLE_HTTP_CODES = {429, 500, 503}


def _post_json(url: str, headers: dict, payload: dict, timeout: int = 120, retries: int = 3) -> dict:
    """
    Realiza una petición POST JSON usando librerías estándar de Python.
    Reintenta con backoff exponencial (2s, 4s, 8s) ante:
    - Errores HTTP retryables: 429 (rate limit), 500, 503
    - Errores de red transitorios: SSL EOF, timeout, connection reset

    timeout=120s: suficiente para la llamada legítima más lenta (síntesis Pro o
    grounding, ~40s), pero corta rápido una llamada colgada en el proxy corporativo
    (antes 240s → un cuelgue arrastraba el run 4 min, y hasta ~16 min con reintentos).
    """
    data = json.dumps(payload).encode("utf-8")
    last_exc: Exception | None = None

    for attempt in range(retries + 1):
        request = urllib.request.Request(
            url=url,
            data=data,
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)

        except urllib.error.HTTPError as e:
            if e.code in _RETRYABLE_HTTP_CODES and attempt < retries:
                wait = 2 ** (attempt + 1)
                last_exc = RuntimeError(f"HTTPError {e.code} (intento {attempt + 1}/{retries + 1}, reintento en {wait}s)")
                time.sleep(wait)
                continue
            error_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"HTTPError {e.code}: {error_body}") from e

        except Exception as e:
            last_exc = e
            err_str = str(e).lower()
            if attempt < retries and any(k in err_str for k in ("eof", "ssl", "timeout", "connection")):
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
                continue
            break

    raise RuntimeError(str(last_exc)) from last_exc


# ============================================================
# MODO MOCK
# ============================================================

def call_mock_llm(system_prompt: str, user_context: str, **kwargs) -> dict:
    """
    Modo seguro para demo.

    No llama a ningún modelo.
    Devuelve una respuesta simulada para comprobar que la integración funciona.
    """

    response_text = f"""# Respuesta simulada del LLM - InvestCopilot

Este resultado se ha generado en modo `mock`.

El cliente LLM ha recibido correctamente:

- Un prompt de sistema de {len(system_prompt)} caracteres.
- Un contexto de usuario de {len(user_context)} caracteres.

No se ha llamado a ningún modelo externo.

Este modo sirve para validar la arquitectura antes de activar llamadas reales a LLM.

## Mensaje clave

InvestCopilot analiza.

La persona decide.
"""

    return _ok(
        {
            "mode": "mock",
            "model": "mock-model",
            "response_text": response_text,
            "usage": {
                "prompt_characters": len(system_prompt),
                "context_characters": len(user_context)
            }
        }
    )


# ============================================================
# MODO OPENAI COMPATIBLE
# ============================================================

def call_openai_compatible_llm(
    system_prompt: str,
    user_context: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2500
) -> dict:
    """
    Llama a un endpoint compatible con OpenAI Chat Completions.

    Requiere:
    - OPENAI_API_KEY
    - OPENAI_BASE_URL, opcional. Por defecto: https://api.openai.com/v1
    - OPENAI_MODEL, opcional.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    if not api_key:
        return _error(
            "Falta OPENAI_API_KEY.",
            {
                "required_env": [
                    "OPENAI_API_KEY"
                ]
            }
        )

    url = f"{base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": build_messages(system_prompt, user_context),
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        result = _post_json(url, headers, payload)

        response_text = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        return _ok(
            {
                "mode": "openai_compatible",
                "model": model,
                "response_text": response_text,
                "raw_response": result,
                "usage": result.get("usage", {})
            }
        )

    except Exception as e:
        return _error(
            "Error llamando al endpoint OpenAI compatible.",
            {
                "error": str(e),
                "url": url,
                "model": model
            }
        )


# ============================================================
# MODO AZURE OPENAI
# ============================================================

def call_azure_openai_llm(
    system_prompt: str,
    user_context: str,
    temperature: float = 0.2,
    max_tokens: int = 2500
) -> dict:
    """
    Llama a Azure OpenAI Chat Completions.

    Requiere:
    - AZURE_OPENAI_API_KEY
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_DEPLOYMENT
    - AZURE_OPENAI_API_VERSION, opcional.
    """

    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

    missing = []

    if not api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not deployment:
        missing.append("AZURE_OPENAI_DEPLOYMENT")

    if missing:
        return _error(
            "Faltan variables de entorno para Azure OpenAI.",
            {
                "missing_env": missing
            }
        )

    url = (
        f"{endpoint}/openai/deployments/{deployment}/chat/completions"
        f"?api-version={api_version}"
    )

    payload = {
        "messages": build_messages(system_prompt, user_context),
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    try:
        result = _post_json(url, headers, payload)

        response_text = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        return _ok(
            {
                "mode": "azure_openai",
                "deployment": deployment,
                "api_version": api_version,
                "response_text": response_text,
                "raw_response": result,
                "usage": result.get("usage", {})
            }
        )

    except Exception as e:
        return _error(
            "Error llamando a Azure OpenAI.",
            {
                "error": str(e),
                "endpoint": endpoint,
                "deployment": deployment,
                "api_version": api_version
            }
        )


# ============================================================
# MODO VERTEX AI (GOOGLE CLOUD / GEMINI)
# ============================================================

def _gemini_messages(system_prompt: str, user_context: str) -> dict:
    """
    Construye el payload en formato generateContent de Vertex AI / Gemini.

    Gemini no usa role "system" en el array de mensajes: el system prompt
    va aparte, en systemInstruction.
    """
    return {
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_context}]
            }
        ]
    }


# Cache en memoria del access token ADC, para no llamar a `gcloud` en cada
# petición. Los access tokens de Google son siempre de corta duración
# (~1h, por diseño de OAuth2 — no hay forma de pedir uno más largo). Lo que
# sí dura mucho más es la sesión de `gcloud auth application-default login`
# (el refresh token detrás), así que en vez de pegar un access token a mano
# en .env y regenerarlo cada hora, lo regeneramos solos automáticamente.
_adc_token_cache = {"token": None, "expires_at": 0.0}
_ADC_TOKEN_TTL_SECONDS = 50 * 60  # refrescar antes de que caduque (~1h real)


def _get_google_access_token() -> tuple[str | None, str | None]:
    """
    Devuelve (token, error). Prioridad:

    1. GOOGLE_ACCESS_TOKEN en .env/entorno, si está fijado explícitamente
       (útil para overridear en CI o pegar un token puntual a mano).
    2. Cache en memoria de un token ADC pedido a `gcloud`, si todavía no ha
       caducado (TTL interno de 50 min, algo menor que la validez real).
    3. Pedir uno nuevo ejecutando
       `gcloud auth application-default print-access-token` y cachearlo.

    En cloud (no hay `gcloud` CLI disponible) esto debe sustituirse por
    Workload Identity / Service Account — ver docstring de call_vertex_ai_llm.
    """
    explicit_token = os.getenv("GOOGLE_ACCESS_TOKEN")

    if explicit_token:
        return explicit_token, None

    now = time.time()

    if _adc_token_cache["token"] and now < _adc_token_cache["expires_at"]:
        return _adc_token_cache["token"], None

    # gcloud puede no estar en el PATH del proceso (p.ej. Streamlit lanzado desde un
    # entorno sin ~/.profile). Buscamos en ubicaciones conocidas de instalación.
    _GCLOUD_CANDIDATES = [
        "gcloud",
        "/home/marioen/google-cloud-sdk/bin/gcloud",
        "/snap/google-cloud-cli/current/bin/gcloud",
        "/snap/google-cloud-cli/473/bin/gcloud",
        "/usr/lib/google-cloud-sdk/bin/gcloud",
    ]
    _gcloud_bin = None
    for _candidate in _GCLOUD_CANDIDATES:
        try:
            subprocess.run([_candidate, "--version"], capture_output=True, timeout=5)
            _gcloud_bin = _candidate
            break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if _gcloud_bin is None:
        # Fallback: google-auth library (funciona en Cloud Run via Workload Identity / metadata server)
        try:
            import google.auth
            import google.auth.transport.requests
            credentials, _ = google.auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
            token = credentials.token
            _adc_token_cache["token"] = token
            _adc_token_cache["expires_at"] = now + _ADC_TOKEN_TTL_SECONDS
            return token, None
        except Exception as ga_err:
            return None, (
                f"No se encuentra gcloud y google-auth falló ({ga_err}). "
                "En local: instala gcloud y ejecuta 'gcloud auth application-default login'. "
                "En Cloud Run: asigna una Service Account con roles/aiplatform.user."
            )

    try:
        result = subprocess.run(
            [_gcloud_bin, "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return None, (
            "No se encuentra el CLI 'gcloud' y GOOGLE_ACCESS_TOKEN no está fijado. "
            "En local: instala gcloud y ejecuta 'gcloud auth application-default login'. "
            "En cloud: usa Workload Identity / Service Account en vez de un access token."
        )
    except Exception as e:
        return None, f"Error ejecutando gcloud para obtener el access token: {e}"

    if result.returncode != 0:
        return None, (
            "gcloud no ha podido generar un access token ADC. "
            f"stderr: {result.stderr.strip()}. "
            "Prueba 'gcloud auth application-default login' manualmente."
        )

    token = result.stdout.strip()

    _adc_token_cache["token"] = token
    _adc_token_cache["expires_at"] = now + _ADC_TOKEN_TTL_SECONDS

    return token, None


def call_vertex_ai_llm(
    system_prompt: str,
    user_context: str,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2500,
    tools: list[dict] | None = None,
    contents: list[dict] | None = None,
) -> dict:
    """
    Llama a Vertex AI (Gemini) Generate Content API.

    Requiere:
    - GOOGLE_CLOUD_PROJECT
    - GOOGLE_CLOUD_LOCATION, opcional. Por defecto: us-central1
    - GOOGLE_VERTEX_MODEL, opcional. Por defecto: gemini-2.5-flash.
      gemini-2.5-flash: agentes de dominio (macro, riesgo, mandatos) — buen
      tool calling, rápido y barato, contexto de sobra para esta carga.
      gemini-2.5-pro: recomendado para el agente de Síntesis/Comité Virtual,
      donde pesa más el razonamiento cruzado entre dominios.
    - GOOGLE_ACCESS_TOKEN: opcional. Si no se fija, se obtiene y cachea
      automáticamente ejecutando
        gcloud auth application-default print-access-token
      (requiere haber hecho una vez 'gcloud auth application-default login';
      esa sesión dura mucho más que el access token de ~1h, así que no hace
      falta regenerar nada a mano). En cloud, sustituir por una identidad
      gestionada: Workload Identity / Service Account con scope
      https://www.googleapis.com/auth/cloud-platform.

    Function calling (tools):
    - tools: declaración de funciones en formato Gemini
      (`[{"functionDeclarations": [...]}]`) para permitir que el modelo pida
      invocar una función en vez de responder directamente. El caller debe
      inspeccionar `data.raw_response` para detectar `functionCall` y, si
      aparece, ejecutar la función y volver a llamar pasando `contents` con
      el turno de function response añadido (protocolo estándar de Gemini).
    - contents: si se pasa, sustituye la construcción automática de
      `[{"role": "user", "parts": [...]}]` a partir de `user_context`. Útil
      para continuar una conversación multi-turno (p.ej. tras una
      functionCall) sin perder el historial previo.
    """

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    model = model or os.getenv("GOOGLE_VERTEX_MODEL", "gemini-2.5-flash")
    access_token, token_error = _get_google_access_token()

    missing = []

    if not project:
        missing.append("GOOGLE_CLOUD_PROJECT")

    if not access_token:
        return _error(
            "No se ha podido obtener un access_token para Vertex AI.",
            {"error": token_error}
        )

    if missing:
        return _error(
            "Faltan variables de entorno para Vertex AI.",
            {
                "missing_env": missing
            }
        )

    url = (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}"
        f"/locations/{location}/publishers/google/models/{model}:generateContent"
    )

    # Los modelos Gemini 2.5 son "thinking" por defecto: consumen parte del
    # maxOutputTokens en razonamiento interno antes de la respuesta visible,
    # lo que puede truncarla (finishReason=MAX_TOKENS) si el budget es bajo.
    # Para agentes de dominio con salida estructurada (no exploración abierta)
    # lo desactivamos por defecto. GOOGLE_THINKING_BUDGET permite forzar un
    # valor explícito (p.ej. para el agente de Síntesis).
    #
    # Importante: gemini-2.5-pro no admite thinkingBudget=0 (HTTP 400). Solo
    # los modelos *-flash permiten desactivarlo del todo. Por eso el default
    # 0 solo se aplica a flash; en pro (u otros) se omite el parámetro y se
    # deja el comportamiento por defecto de la API, salvo override explícito.
    thinking_budget_env = os.getenv("GOOGLE_THINKING_BUDGET")

    payload = _gemini_messages(system_prompt, user_context)

    if contents is not None:
        payload["contents"] = contents

    if tools:
        payload["tools"] = tools

    payload["generationConfig"] = {
        "temperature": temperature,
        "maxOutputTokens": max_tokens
    }

    if thinking_budget_env is not None:
        payload["generationConfig"]["thinkingConfig"] = {
            "thinkingBudget": int(thinking_budget_env)
        }
    elif "flash" in model.lower():
        payload["generationConfig"]["thinkingConfig"] = {
            "thinkingBudget": 0
        }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Cap duro: aborta antes de incurrir en el gasto si ya se superó el límite diario
    try:
        check_cap(model=model)
    except CostCapExceeded as e:
        return _error(str(e), {"error": "cost_cap_exceeded", "model": model})

    try:
        result = _post_json(url, headers, payload)

        response_text = (
            result
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
        )

        # Registra coste real con tokens de usageMetadata (mejor que estimación)
        usage = result.get("usageMetadata", {})
        try:
            record_llm_call(
                model=model,
                input_tokens=usage.get("promptTokenCount", 0),
                output_tokens=usage.get("candidatesTokenCount", 0),
            )
        except CostCapExceeded as e:
            # El cap se superó en esta misma llamada: registrado, pero dejamos
            # devolver el resultado ya obtenido (el gasto ya ocurrió).
            pass
        except Exception:
            pass  # nunca romper la respuesta LLM por errores de tracking

        grounding_metadata = (
            result.get("candidates", [{}])[0].get("groundingMetadata", {})
        )

        return _ok(
            {
                "mode": "vertex_ai",
                "model": model,
                "project": project,
                "location": location,
                "response_text": response_text,
                "raw_response": result,
                "usage": usage,
                "grounding_metadata": grounding_metadata,
            }
        )

    except CostCapExceeded:
        raise  # ya manejado arriba, no debería llegar aquí
    except Exception as e:
        return _error(
            "Error llamando a Vertex AI.",
            {
                "error": str(e),
                "project": project,
                "location": location,
                "model": model
            }
        )


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def call_llm(
    system_prompt: str,
    user_context: str,
    mode: str | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 2500,
    max_context_chars: int = 20000,
    tools: list[dict] | None = None,
    contents: list[dict] | None = None,
) -> dict:
    """
    Punto único de entrada para llamar a un LLM.

    Parámetros:
    - system_prompt: prompt interno del agente.
    - user_context: contexto construido a partir de archivos/datos.
    - mode: mock, openai_compatible o azure_openai.
    - model: modelo opcional para openai_compatible.
    - temperature: temperatura del modelo.
    - max_tokens: máximo de tokens de salida.
    - max_context_chars: límite de caracteres del contexto enviado.
    - tools / contents: solo soportados en mode="vertex_ai" (function calling
      y continuidad multi-turno). Se ignoran en el resto de modos.

    Devuelve un dict estándar con:
    - status
    - data.response_text si success
    - message/details si error
    """

    mode = (mode or get_llm_mode()).strip().lower()

    system_prompt = truncate_text(system_prompt, max_chars=12000)
    user_context = truncate_text(user_context, max_chars=max_context_chars)

    if mode == "mock":
        return call_mock_llm(
            system_prompt=system_prompt,
            user_context=user_context,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    if mode == "openai_compatible":
        return call_openai_compatible_llm(
            system_prompt=system_prompt,
            user_context=user_context,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    if mode == "azure_openai":
        return call_azure_openai_llm(
            system_prompt=system_prompt,
            user_context=user_context,
            temperature=temperature,
            max_tokens=max_tokens
        )

    if mode == "vertex_ai":
        return call_vertex_ai_llm(
            system_prompt=system_prompt,
            user_context=user_context,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            contents=contents,
        )

    return _error(
        "Modo LLM no reconocido.",
        {
            "mode_received": mode,
            "valid_modes": [
                "mock",
                "openai_compatible",
                "azure_openai",
                "vertex_ai"
            ]
        }
    )


# ============================================================
# UTILIDAD PARA EXTRAER EL BLOQUE JSON DE LA RESPUESTA DEL LLM
# ============================================================

def extract_json_block(text: str) -> dict | None:
    """
    Extrae y parsea el primer bloque ```json ... ``` de una respuesta de LLM.

    Los prompts de los agentes piden generar dos archivos (.md y .json) en
    una sola respuesta de texto. El orden y el resto de la narración varían
    según el agente y la pasada, pero todos devuelven el JSON estructurado
    dentro de un bloque ```json. Esta función lo localiza de forma robusta
    en lugar de asumir una posición fija.

    Devuelve None si no se encuentra o no se puede parsear.
    """
    if not text:
        return None

    match = re.search(r"```json\s*(.*?)```", text, re.DOTALL)

    if not match:
        return None

    try:
        return json.loads(match.group(1).strip())
    except json.JSONDecodeError:
        return None


# ============================================================
# UTILIDAD PARA CONSTRUIR CONTEXTO SIMPLE
# ============================================================

def build_context_from_files(
    files: list[str | Path],
    title: str = "Contexto InvestCopilot",
    max_chars_per_file: int = 6000
) -> str:
    """
    Construye un contexto textual simple a partir de varios archivos.

    Lee archivos de texto, markdown, json, csv y py de forma básica.
    """

    sections = [f"# {title}"]

    for file in files:
        path = Path(file)

        if not path.is_absolute():
            path = PROJECT_DIR / path

        sections.append("\n---")
        sections.append(f"\n## Archivo: {path}")

        if not path.exists():
            sections.append("\nArchivo no encontrado.")
            continue

        try:
            suffix = path.suffix.lower()

            if suffix in [".md", ".txt", ".py", ".json", ".csv"]:
                text = path.read_text(encoding="utf-8", errors="ignore")
                sections.append("\n```plaintext")
                sections.append(truncate_text(text, max_chars=max_chars_per_file))
                sections.append("```")
            else:
                sections.append("\nTipo de archivo no soportado para lectura textual simple.")

        except Exception as e:
            sections.append(f"\nError leyendo archivo: {e}")

    return "\n".join(sections)


# ============================================================
# UTILIDAD PARA GUARDAR RESPUESTA LLM
# ============================================================

def save_llm_response(
    response: dict,
    output_path: str | Path,
    overwrite: bool = True
) -> dict:
    """
    Guarda la respuesta del LLM en un archivo de texto.

    Si la respuesta es success, guarda data.response_text.
    Si es error, guarda el JSON completo del error.
    """

    path = Path(output_path)

    if not path.is_absolute():
        path = PROJECT_DIR / path

    if path.exists() and not overwrite:
        return _error(
            "El archivo ya existe y overwrite=False.",
            {
                "output_path": str(path)
            }
        )

    path.parent.mkdir(parents=True, exist_ok=True)

    if response.get("status") == "success":
        text = response.get("data", {}).get("response_text", "")
    else:
        text = json.dumps(response, ensure_ascii=False, indent=2, default=str)

    path.write_text(text, encoding="utf-8")

    return _ok(
        {
            "output_path": str(path),
            "characters_written": len(text),
            "overwrite": overwrite
        }
    )


# ============================================================
# FUNCTION CALLING — UTILIDADES REUTILIZABLES POR LOS AGENTES
# ============================================================

def extract_function_call(raw_response: dict) -> tuple[str | None, dict]:
    """
    Busca un part de tipo functionCall en la respuesta raw de Vertex AI.
    Devuelve (nombre, args) o (None, {}) si el modelo respondió en texto.
    """
    try:
        parts = raw_response["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return None, {}

    for part in parts:
        fc = part.get("functionCall")
        if fc:
            return fc.get("name"), fc.get("args", {})

    return None, {}


def call_llm_with_tools(
    system_prompt: str,
    user_context: str,
    tools: list[dict],
    tool_executor_fn,
    mode: str | None = None,
    model: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 6000,
    max_context_chars: int = 30000,
    max_iterations: int = 5,
) -> dict:
    """
    Llama al LLM con function calling en modo multi-vuelta: si el modelo pide
    invocar una tool, ejecuta `tool_executor_fn(nombre, args)`, añade el
    resultado al historial de conversación y vuelve a llamar. Repite hasta que
    el modelo devuelva texto (sin functionCall) o se alcance max_iterations.

    Solo aplica en mode='vertex_ai'. En otros modos actúa como call_llm normal.

    tool_executor_fn: callable(nombre: str, args: dict) -> dict
    """
    llm_mode = (mode or get_llm_mode()).strip().lower()

    contents = None
    tools_invocadas = []

    for _iteration in range(max_iterations):
        kwargs = {}
        if llm_mode == "vertex_ai":
            kwargs["tools"] = tools
            if contents is not None:
                kwargs["contents"] = contents

        response = call_llm(
            system_prompt=system_prompt,
            user_context=user_context,
            mode=llm_mode,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            max_context_chars=max_context_chars,
            **kwargs,
        )

        if response.get("status") != "success" or llm_mode != "vertex_ai":
            return response

        raw = response.get("data", {}).get("raw_response", {})
        nombre, args = extract_function_call(raw)

        if not nombre:
            # Respuesta final en texto — terminar el loop
            if tools_invocadas:
                response.setdefault("data", {})["tools_invocadas"] = tools_invocadas
            return response

        # Ejecutar la tool y acumular en el historial
        resultado = tool_executor_fn(nombre, args)
        tools_invocadas.append({"tool": nombre, "args": args})

        if contents is None:
            contents = [
                {"role": "user", "parts": [{"text": truncate_text(user_context, max_context_chars)}]},
            ]

        contents.append(
            {"role": "model", "parts": [{"functionCall": {"name": nombre, "args": args}}]}
        )
        contents.append(
            {"role": "user", "parts": [{"functionResponse": {"name": nombre, "response": resultado}}]}
        )

    # Agotadas las iteraciones — devolver la última respuesta disponible
    if tools_invocadas:
        response.setdefault("data", {})["tools_invocadas"] = tools_invocadas
    return response


# ============================================================
# PRUEBA LOCAL
# ============================================================

def local_test():
    prompt = (
        "Eres un agente de prueba de InvestCopilot. "
        "Resume el contexto de forma prudente y recuerda que la persona decide."
    )

    context = (
        "Hipótesis: incrementar tecnología estadounidense en BAM. "
        "Esta es una prueba local del cliente LLM en modo mock."
    )

    result = call_llm(
        system_prompt=prompt,
        user_context=context,
        mode="mock"
    )

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))

    if result.get("status") == "success":
        test_output = LLM_CLIENT_DIR / "llm_client_test_output.md"
        save_result = save_llm_response(result, test_output, overwrite=True)
        print(json.dumps(save_result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    local_test()