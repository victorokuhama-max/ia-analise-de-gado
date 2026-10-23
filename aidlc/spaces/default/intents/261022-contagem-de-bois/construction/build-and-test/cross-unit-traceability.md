# Rastreabilidade Cruzada entre Unidades (*Cross-Unit Traceability*) — `build-and-test`

## Summary

O verificador determinístico de rastreabilidade (`bun .agents/tools/aidlc.ts engine sensor-traceability --stage build-and-test`) confirmou **100% de cobertura (`pass: true`, `uncovered: []`)** para todos os requisitos funcionais (`FR1.1`–`FR6.1`), requisitos não-funcionais (`NFR1`–`NFR6` e `NFR1.1`–`NFR6.2`), critérios de aceite (`AC1.1.1`–`AC6.1.1`) e regras de negócio (`BR1.1`–`BR6.1`) na unidade `u1-agrocount-platform`.

## Veredito Global do Gate de Rastreabilidade

- **Veredito:** **PASS (`pass: true`)**
- **Elementos descobertos (`uncovered`):** `[]` (Nenhum — 0 elementos descobertos)

## Matriz de Cobertura por Requisito e Critério de Aceite

| ID | Coberto (`covered`) | Unidade / Mecanismo de Rastreamento | Arquivo de Implementação / Teste |
|---|---|---|---|
| **`FR1.1`** | `true` | `AC1.1.1`, `AC1.1.2` (`u1-agrocount-platform`) | `src/agrocount/service.py`, `src/agrocount/repository.py` |
| **`FR1.2`** | `true` | `AC1.2.1`, `AC1.2.2` (`u1-agrocount-platform`) | `src/agrocount/service.py`, `src/agrocount/vision.py` |
| **`FR1.3`** | `true` | `AC1.3.1`, `AC1.3.2` (`u1-agrocount-platform`) | `src/agrocount/vision.py` |
| **`FR2.1`** | `true` | `AC2.1.1`, `AC2.1.2` (`u1-agrocount-platform`) | `src/agrocount/vision.py` |
| **`FR2.2`** | `true` | `AC2.2.1` (`u1-agrocount-platform`) | `src/agrocount/vision.py` |
| **`FR3.1`** | `true` | `AC3.1.1` (`u1-agrocount-platform`) | `src/agrocount/vision.py` |
| **`FR3.2`** | `true` | `AC3.2.1` (`u1-agrocount-platform`) | `src/agrocount/web/index.html` |
| **`FR3.3`** | `true` | `AC3.3.1` (`u1-agrocount-platform`) | `src/agrocount/web/app.js` |
| **`FR4.1`** | `true` | `AC4.1.1` (`u1-agrocount-platform`) | `src/agrocount/hitl.py` |
| **`FR4.2`** | `true` | `AC4.2.1` (`u1-agrocount-platform`) | `src/agrocount/hitl.py` |
| **`FR4.3`** | `true` | `AC4.3.1` (`u1-agrocount-platform`) | `src/agrocount/hitl.py` |
| **`FR5.1`** | `true` | `AC5.1.1` (`u1-agrocount-platform`) | `src/agrocount/hitl.py` |
| **`FR5.2`** | `true` | `AC5.2.1` (`u1-agrocount-platform`) | `src/agrocount/hitl.py` |
| **`FR5.3`** | `true` | `AC5.3.1` (`u1-agrocount-platform`) | `src/agrocount/hitl.py` |
| **`FR6.1`** | `true` | `AC6.1.1` (`u1-agrocount-platform`) | `src/agrocount/service.py` |
| **`NFR1`** | `true` | `NFR1.1`, `NFR1.2`, `NFR1.3`, `NFR1.4` (`u1-agrocount-platform`) | `src/agrocount/vision.py`, `src/agrocount/api.py` |
| **`NFR2`** | `true` | `NFR2.1`, `NFR2.2`, `NFR2.3` (`u1-agrocount-platform`) | `src/agrocount/api.py`, `src/agrocount/repository.py`, `src/agrocount/hitl.py` |
| **`NFR3`** | `true` | `NFR3.1`, `NFR3.2` (`u1-agrocount-platform`) | `Dockerfile`, `src/agrocount/vision.py` |
| **`NFR4`** | `true` | `NFR4.1`, `NFR4.2`, `NFR4.3` (`u1-agrocount-platform`) | `src/agrocount/service.py`, `src/agrocount/repository.py`, `src/agrocount/hitl.py` |
| **`NFR5`** | `true` | `NFR5.1`, `NFR5.2` (`u1-agrocount-platform`) | `src/agrocount/web/index.html`, `src/agrocount/models.py` |
| **`NFR6`** | `true` | `NFR6.1`, `NFR6.2` (`u1-agrocount-platform`) | `src/agrocount/api.py`, `src/agrocount/service.py` |
