# Instruções de Build — AgroCount IA (`u1-agrocount-platform`)

## Summary

Este documento descreve os passos exatos de preparação de ambiente, compilação de bytecode Python, validação de ativos web e construção de imagem container para a unidade `u1-agrocount-platform` (`U1` — Plataforma Integrada AgroCount IA & Estúdio HITL).

## Pré-requisitos e Variáveis de Ambiente

| Item | Especificação | Valor Padrão (Local / CI) |
|---|---|---|
| **Python Runtime** | Python $\ge 3.11$ (validado em Python 3.13) | `python3` |
| **`PYTHONPATH`** | Caminho do código-fonte da unidade | `src` |
| **`PORT`** | Porta HTTP do servidor REST e Estúdio Web | `8080` |
| **Banco de Dados Local** | SQLite 3 nativo (`sqlite3`) | `:memory:` (testes) ou `./data/agrocount.db` |
| **Armazenamento Local** | Espelho local do bucket `gs://agrocount-storage` | `./data/storage` |

## Comandos de Build e Verificação Sintática

1. **Compilação e Verificação de Bytecode Python (Zero Erros de Sintaxe/Importação):**
   ```bash
   PYTHONPATH=src python3 -m compileall -q src/ tests/ scripts/
   ```
2. **Verificação de Integridade de Pacote e Módulos:**
   ```bash
   PYTHONPATH=src python3 -c "import agrocount; assert agrocount.__version__ == '1.0.0'"
   ```
3. **Build da Imagem Container Multi-Stage (Opcional / Cloud Run):**
   ```bash
   docker build -t agrocount-platform:1.0.0 .
   ```

## Resolução de Problemas Comuns (*Troubleshooting*)

- **`ModuleNotFoundError: No module named 'agrocount'`:** Certifique-se de exportar `PYTHONPATH=src` antes de invocar `python3` ou execute `bash scripts/verify.sh`.
- **Permissão de escrita em `./data/storage`:** Verifique se o usuário corrente possui permissão de escrita no diretório de trabalho ou utilize `tempfile.TemporaryDirectory()` em execuções de teste.
