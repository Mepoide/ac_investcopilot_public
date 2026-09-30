from pathlib import Path
import json
import sys
import traceback

# ============================================================
# CONFIGURACIÓN
# ============================================================

# Guarda este archivo en:
# 08_agents_mcp/mcp_server/server.py
#
# Este servidor es una versión mínima tipo MCP/stdin-stdout para la demo.
# No depende todavía de librerías externas de MCP.
#
# Permite invocar tools definidas en:
# 08_agents_mcp/mcp_server/tools.py

MCP_SERVER_DIR = Path(__file__).resolve().parent

if str(MCP_SERVER_DIR) not in sys.path:
    sys.path.append(str(MCP_SERVER_DIR))

from tools import TOOLS_REGISTRY, listar_tools_disponibles


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def respuesta_jsonrpc_ok(request_id, result):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }


def respuesta_jsonrpc_error(request_id, code, message, data=None):
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": code,
            "message": message,
            "data": data or {}
        }
    }


def parse_request(line):
    try:
        return json.loads(line)
    except Exception as e:
        return {
            "_parse_error": str(e),
            "_raw": line
        }


def call_tool(tool_name, arguments):
    if tool_name == "listar_tools_disponibles":
        return listar_tools_disponibles()

    if tool_name not in TOOLS_REGISTRY:
        return {
            "tool": tool_name,
            "status": "error",
            "message": "Tool no registrada.",
            "available_tools": sorted(list(TOOLS_REGISTRY.keys()))
        }

    tool_fn = TOOLS_REGISTRY[tool_name]

    if arguments is None:
        arguments = {}

    if not isinstance(arguments, dict):
        return {
            "tool": tool_name,
            "status": "error",
            "message": "Los argumentos deben ser un objeto JSON.",
            "arguments_received": arguments
        }

    try:
        return tool_fn(**arguments)
    except TypeError as e:
        return {
            "tool": tool_name,
            "status": "error",
            "message": "Error de parámetros al llamar a la tool.",
            "error": str(e),
            "arguments_received": arguments
        }
    except Exception as e:
        return {
            "tool": tool_name,
            "status": "error",
            "message": "Error ejecutando la tool.",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# ============================================================
# HANDLERS
# ============================================================

def handle_initialize(request_id, params):
    result = {
        "server": {
            "name": "investcopilot-mcp-demo",
            "version": "0.1.0",
            "description": "Servidor MCP mínimo para la demo InvestCopilot."
        },
        "capabilities": {
            "tools": True,
            "resources": False,
            "prompts": False
        },
        "notes": [
            "Esta es una implementación mínima para demo.",
            "No usa todavía una librería MCP externa.",
            "Expone tools locales para leer archivos, guardar outputs y ejecutar el orquestador DECISION_001."
        ]
    }

    return respuesta_jsonrpc_ok(request_id, result)


def handle_tools_list(request_id, params):
    tools = []

    for tool_name in sorted(list(TOOLS_REGISTRY.keys()) + ["listar_tools_disponibles"]):
        tools.append({
            "name": tool_name,
            "description": get_tool_description(tool_name),
            "inputSchema": get_tool_schema(tool_name)
        })

    return respuesta_jsonrpc_ok(
        request_id,
        {
            "tools": tools
        }
    )


def get_tool_description(tool_name):
    descriptions = {
        "listar_tools_disponibles": "Devuelve el listado de tools disponibles.",
        "listar_archivos": "Lista archivos dentro de una carpeta del proyecto.",
        "leer_texto": "Lee un archivo de texto o Markdown.",
        "leer_json": "Lee un archivo JSON.",
        "leer_csv": "Lee un CSV y devuelve registros.",
        "guardar_texto": "Guarda contenido de texto en un archivo.",
        "guardar_json": "Guarda contenido JSON en un archivo.",
        "leer_output_agente": "Lee el output principal de un agente en formato JSON o Markdown.",
        "ejecutar_orquestador_decision_001": "Ejecuta el flujo completo DECISION_001: Macro, Riesgo, Mandatos y Síntesis.",
        "validar_estructura_proyecto": "Valida que existen carpetas y archivos clave del prototipo.",
        "resumen_rapido_decision_001": "Devuelve un resumen rápido de la síntesis final DECISION_001."
    }

    return descriptions.get(tool_name, "Tool disponible en InvestCopilot MCP demo.")


def get_tool_schema(tool_name):
    schemas = {
        "listar_tools_disponibles": {
            "type": "object",
            "properties": {}
        },
        "listar_archivos": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta relativa o absoluta. Por defecto, raíz del proyecto."
                },
                "patron": {
                    "type": "string",
                    "description": "Patrón glob. Ejemplo: *.md, *.json, *.csv."
                },
                "recursivo": {
                    "type": "boolean",
                    "description": "Si true, busca en subcarpetas."
                }
            }
        },
        "leer_texto": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta relativa o absoluta del archivo."
                }
            },
            "required": ["ruta"]
        },
        "leer_json": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta relativa o absoluta del archivo JSON."
                }
            },
            "required": ["ruta"]
        },
        "leer_csv": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta relativa o absoluta del archivo CSV."
                },
                "max_filas": {
                    "type": ["integer", "null"],
                    "description": "Número máximo de filas a devolver."
                }
            },
            "required": ["ruta"]
        },
        "guardar_texto": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta relativa o absoluta donde guardar."
                },
                "contenido": {
                    "type": "string",
                    "description": "Contenido de texto a guardar."
                },
                "sobrescribir": {
                    "type": "boolean",
                    "description": "Si false, no sobrescribe si el archivo existe."
                }
            },
            "required": ["ruta", "contenido"]
        },
        "guardar_json": {
            "type": "object",
            "properties": {
                "ruta": {
                    "type": "string",
                    "description": "Ruta relativa o absoluta donde guardar."
                },
                "contenido": {
                    "type": ["object", "array"],
                    "description": "Objeto o lista JSON a guardar."
                },
                "sobrescribir": {
                    "type": "boolean",
                    "description": "Si false, no sobrescribe si el archivo existe."
                }
            },
            "required": ["ruta", "contenido"]
        },
        "leer_output_agente": {
            "type": "object",
            "properties": {
                "nombre_agente": {
                    "type": "string",
                    "description": "macro, riesgo, risk, mandatos, sintesis o synthesis."
                },
                "formato": {
                    "type": "string",
                    "description": "json o md."
                }
            },
            "required": ["nombre_agente"]
        },
        "ejecutar_orquestador_decision_001": {
            "type": "object",
            "properties": {}
        },
        "validar_estructura_proyecto": {
            "type": "object",
            "properties": {}
        },
        "resumen_rapido_decision_001": {
            "type": "object",
            "properties": {}
        }
    }

    return schemas.get(tool_name, {
        "type": "object",
        "properties": {}
    })


def handle_tools_call(request_id, params):
    if params is None:
        params = {}

    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name:
        return respuesta_jsonrpc_error(
            request_id,
            -32602,
            "Falta el nombre de la tool en params.name."
        )

    result = call_tool(tool_name, arguments)

    return respuesta_jsonrpc_ok(
        request_id,
        {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, indent=2, default=str)
                }
            ],
            "isError": result.get("status") == "error"
        }
    )


def handle_request(request):
    if "_parse_error" in request:
        return respuesta_jsonrpc_error(
            None,
            -32700,
            "Error parseando JSON.",
            {
                "error": request["_parse_error"],
                "raw": request.get("_raw")
            }
        )

    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return handle_initialize(request_id, params)

    if method == "tools/list":
        return handle_tools_list(request_id, params)

    if method == "tools/call":
        return handle_tools_call(request_id, params)

    if method == "ping":
        return respuesta_jsonrpc_ok(
            request_id,
            {
                "status": "ok",
                "server": "investcopilot-mcp-demo"
            }
        )

    return respuesta_jsonrpc_error(
        request_id,
        -32601,
        f"Método no soportado: {method}",
        {
            "supported_methods": [
                "initialize",
                "tools/list",
                "tools/call",
                "ping"
            ]
        }
    )


# ============================================================
# SERVIDOR STDIN / STDOUT
# ============================================================

def main():
    """
    Servidor mínimo por stdin/stdout.

    Lee una línea JSON-RPC por stdin.
    Devuelve una línea JSON-RPC por stdout.

    Ejemplo manual de entrada:
    {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
    """

    for line in sys.stdin:
        line = line.strip()

        if not line:
            continue

        request = parse_request(line)
        response = handle_request(request)

        print(json.dumps(response, ensure_ascii=False, default=str), flush=True)


# ============================================================
# PRUEBA LOCAL SIN STDIN
# ============================================================

def local_test():
    tests = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "validar_estructura_proyecto",
                "arguments": {}
            }
        },
        {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "resumen_rapido_decision_001",
                "arguments": {}
            }
        }
    ]

    for test in tests:
        response = handle_request(test)
        print(json.dumps(response, ensure_ascii=False, indent=2, default=str))
        print("-" * 80)


if __name__ == "__main__":
    if "--test" in sys.argv:
        local_test()
    else:
        main()