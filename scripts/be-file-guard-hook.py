#!/usr/bin/env python3
"""
be-file-guard-hook.py — Hook Claude Code para PreToolUse[Write].

Recebe JSON via stdin com o input da ferramenta Write.
Verifica se o arquivo já existe antes de Claude sobrescrever.

Se existir: imprime aviso e exit 0 (não bloqueia — apenas informa).
Se não existir: cria o diretório pai (para Write funcionar) e exit 0.

Configuração em .claude/settings.json:
  "hooks": {
    "PreToolUse": [{
      "matcher": "Write",
      "hooks": [{"type": "command", "command": "python scripts/be-file-guard-hook.py"}]
    }]
  }

Saída legível para o usuário no terminal.
"""

import json
import sys
from pathlib import Path


def main():
    from cli_utils import force_utf8_stdio
    force_utf8_stdio()
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # Se não tem stdin válido (chamada direta), sai silenciosamente
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    file_path_str = tool_input.get("file_path", "")

    if not file_path_str:
        sys.exit(0)

    file_path = Path(file_path_str)

    if file_path.exists():
        # Arquivo já existe — Claude vai sobrescrever
        # Aviso: imprime no stderr (visível ao usuário sem bloquear)
        print(
            f"\n⚠️  [file-guard] SOBRESCRITA detectada: {file_path}\n"
            f"   O arquivo já existe. Claude vai substituir o conteúdo completo.\n"
            f"   Se era intenção editar (não recriar), prefira a ferramenta Edit.\n",
            file=sys.stderr,
        )
    else:
        # Arquivo novo — criar diretórios pai preventivamente
        file_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[file-guard] Novo arquivo: {file_path}", file=sys.stderr)

    # Sempre exit 0 — aviso apenas, não bloqueia
    sys.exit(0)


if __name__ == "__main__":
    main()
