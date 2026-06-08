#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
be-file-guard.py — File creation guardian for agent scripts.

Garante que nenhum arquivo seja sobrescrito acidentalmente por um agente IA.
Toda criacao de arquivo obrigatoriamente passa por este script.
O agente nunca usa create_file diretamente — apenas edita apos o guard.

Uso:
    python scripts/be-file-guard.py <caminho_do_arquivo>

Exemplos:
    python scripts/be-file-guard.py docs/architecture/backend/plans/plan-<MODULE>.md
    python scripts/be-file-guard.py backend/services/<service>/src/main/java/<package>/domain/model/<Entity>.java

Saida (primeira linha sempre comeca com o status):
    CREATED:<caminho>  -> arquivo criado vazio; agente deve inserir conteudo via insert_edit_into_file
    EXISTS:<caminho>   -> arquivo ja existe; agente deve apenas editar (nunca recriar do zero)

Exit codes:
    0 -> operacao concluida (tanto CREATED quanto EXISTS sao sucesso)
    1 -> erro de argumento ou caminho invalido
"""

import sys
from pathlib import Path


_USAGE = (
    "Uso: python scripts/be-file-guard.py <caminho_do_arquivo>\n"
    "   Exemplo: python scripts/be-file-guard.py docs/.../plans/plan-APS-004.md\n"
    "\n"
    "O script cria o arquivo VAZIO no caminho informado. Se ja existe, retorna\n"
    "EXISTS sem tocar no conteudo. Nao aceita flags - o primeiro argumento\n"
    "DEVE ser um path real."
)


def main():
    from cli_utils import force_utf8_stdio, require_positional_argv
    force_utf8_stdio()

    # D-086 hardening, extracted into shared helper in D-087.
    raw_path = require_positional_argv(
        sys.argv, usage=_USAGE, doc=__doc__, prog="be-file-guard.py"
    )

    # Resolve relative to repo root (script lives in scripts/, repo root is one level up)
    repo_root = Path(__file__).resolve().parent.parent
    file_path = (repo_root / raw_path).resolve() if not Path(raw_path).is_absolute() else Path(raw_path).resolve()

    if file_path.exists():
        print(f"EXISTS:{file_path}")
        print()
        print(f"[!] O arquivo ja existe.")
        print(f"    -> Use insert_edit_into_file ou replace_string_in_file para editar.")
        print(f"    -> NUNCA recriar o arquivo do zero (apagaria o conteudo existente).")
        print(f"    Caminho: {file_path}")
        sys.exit(0)

    # Cria diretorios pai se necessario
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Cria arquivo vazio
    file_path.touch()

    print(f"CREATED:{file_path}")
    print()
    print(f"[+] Arquivo criado vazio.")
    print(f"    -> Use insert_edit_into_file para inserir o conteudo completo.")
    print(f"    Caminho: {file_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()

