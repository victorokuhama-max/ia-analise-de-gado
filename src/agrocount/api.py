"""Camada de API RESTful OpenAPI 3.1 (/api/v1/*) e Servidor do Estúdio Web HITL."""

from __future__ import annotations

import json
import re
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

from .models import AgroCountError
from .service import InspectionManagementService

WEB_DIR = Path(__file__).resolve().parent / "web"


class AgroCountApp:
    """Roteador HTTP determinístico para os endpoints /api/v1/* e ativos do Web Review Studio."""

    def __init__(
        self,
        service: Optional[InspectionManagementService] = None,
        require_auth: bool = False,
        valid_tokens: Optional[Dict[str, str]] = None,
    ) -> None:
        self.service = service or InspectionManagementService()
        self.require_auth = require_auth
        self.valid_tokens = valid_tokens or {"agrocount-dev-token": "auditor-1"}

    def handle_request(
        self,
        method: str,
        raw_url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes | str] = None,
    ) -> Tuple[int, Dict[str, str], bytes]:
        req_headers = {k.lower(): v for k, v in (headers or {}).items()}
        correlation_id = req_headers.get("x-correlation-id") or f"corr-{uuid.uuid4().hex[:12]}"
        parsed = urlparse(raw_url)
        path = parsed.path.rstrip("/") or "/"
        query = {k: v[0] for k, v in parse_qs(parsed.query).items() if v}

        resp_headers = {
            "X-Correlation-Id": correlation_id,
            "X-Content-Type-Options": "nosniff",
        }

        try:
            # Rotas públicas estáticas e health check
            if method == "GET" and path == "/":
                html_bytes = (WEB_DIR / "index.html").read_bytes()
                resp_headers["Content-Type"] = "text/html; charset=utf-8"
                return 200, resp_headers, html_bytes

            if method == "GET" and path == "/app.js":
                js_bytes = (WEB_DIR / "app.js").read_bytes()
                resp_headers["Content-Type"] = "application/javascript; charset=utf-8"
                return 200, resp_headers, js_bytes

            if method == "GET" and path == "/api/v1/health":
                active_model = self.service.repo.get_active_model()
                return self._json_response(
                    200,
                    resp_headers,
                    {
                        "status": "ok",
                        "service": "u1-agrocount-platform",
                        "active_model_version": active_model.version_tag,
                    },
                )

            # Verificação opcional de autenticação JWT/Bearer (NFR2.1)
            if self.require_auth:
                auth_header = req_headers.get("authorization", "")
                if not auth_header.startswith("Bearer "):
                    raise AgroCountError(
                        code="UNAUTHORIZED",
                        message="Token Bearer ausente no cabeçalho Authorization.",
                        http_status=401,
                    )
                token = auth_header[len("Bearer ") :].strip()
                if token not in self.valid_tokens:
                    raise AgroCountError(
                        code="INVALID_TOKEN",
                        message="Token Bearer inválido ou expirado.",
                        http_status=401,
                    )

            payload = self._parse_json_body(body) if method in ("POST", "PUT", "PATCH") else {}

            # 1. Fazendas e Pastos
            if path == "/api/v1/farms":
                if method == "GET":
                    return self._json_response(200, resp_headers, {"items": self.service.list_farms()})
                if method == "POST":
                    created = self.service.create_farm(
                        name=str(payload.get("name") or ""),
                        code=str(payload.get("code") or ""),
                        paddocks_data=payload.get("paddocks") or [],
                    )
                    return self._json_response(201, resp_headers, created)

            # 2. Inspeções (Listagem e Criação)
            if path == "/api/v1/inspections":
                if method == "GET":
                    items = self.service.list_inspections(
                        farm_id=query.get("farm_id"),
                        status=query.get("status"),
                    )
                    return self._json_response(200, resp_headers, {"items": items})
                if method == "POST":
                    idem_key = str(payload.get("idempotency_key") or "")
                    already_exists = (
                        self.service.repo.get_inspection_by_idempotency_key(idem_key) is not None
                        if idem_key
                        else False
                    )
                    result = self.service.create_inspection(
                        farm_id=str(payload.get("farm_id") or ""),
                        paddock_id=str(payload.get("paddock_id") or ""),
                        idempotency_key=idem_key,
                        media_type=str(payload.get("media_type") or ""),
                        source_uri=str(payload.get("source_uri") or ""),
                        file_size_bytes=int(payload.get("file_size_bytes") or 0),
                        flight_altitude_m=payload.get("flight_altitude_m"),
                        overlap_pct=payload.get("overlap_pct"),
                        media_metadata=payload.get("media_metadata"),
                        custom_detections=payload.get("custom_detections"),
                    )
                    status_code = 200 if already_exists else 202
                    return self._json_response(status_code, resp_headers, result)

            # 3. Detalhe de Inspeção (/api/v1/inspections/{id})
            m_detail = re.fullmatch(r"/api/v1/inspections/([^/]+)", path)
            if m_detail and method == "GET":
                inspection_id = m_detail.group(1)
                details = self.service.get_inspection_details(inspection_id)
                return self._json_response(200, resp_headers, details)

            # 4. Submissão de Revisão HITL (/api/v1/inspections/{id}/hitl-review)
            m_hitl = re.fullmatch(r"/api/v1/inspections/([^/]+)/hitl-review", path)
            if m_hitl and method == "POST":
                inspection_id = m_hitl.group(1)
                result = self.service.submit_hitl_review(
                    inspection_id=inspection_id,
                    auditor_id=str(payload.get("auditor_id") or ""),
                    actions=payload.get("actions") or [],
                    idempotent_retry=bool(payload.get("idempotent_retry", False)),
                )
                return self._json_response(200, resp_headers, result)

            # 5. Exportação de Laudo (/api/v1/inspections/{id}/report)
            m_report = re.fullmatch(r"/api/v1/inspections/([^/]+)/report", path)
            if m_report and method == "GET":
                inspection_id = m_report.group(1)
                fmt = query.get("format", "PDF")
                report_data = self.service.export_audit_report(inspection_id, fmt=fmt)
                return self._json_response(200, resp_headers, report_data)

            # 6. Status do Modelo Ativo (/api/v1/models/active)
            if path == "/api/v1/models/active" and method == "GET":
                return self._json_response(200, resp_headers, self.service.get_active_model_status())

            # 7. Disparo de Fine-Tuning (/api/v1/models/fine-tune)
            if path == "/api/v1/models/fine-tune" and method == "POST":
                ft_result = self.service.trigger_fine_tuning(
                    min_new_golden_samples=int(payload.get("min_new_golden_samples", 10)),
                    target_epochs=int(payload.get("target_epochs", 30)),
                    candidate_metrics=payload.get("candidate_metrics"),
                )
                return self._json_response(202, resp_headers, ft_result)

            raise AgroCountError(
                code="ENDPOINT_NOT_FOUND",
                message=f"Rota não encontrada: {method} {path}",
                http_status=404,
            )

        except AgroCountError as exc:
            return self._json_response(
                exc.http_status,
                resp_headers,
                exc.to_envelope(correlation_id),
            )
        except Exception as exc:
            err = AgroCountError(
                code="INTERNAL_SERVER_ERROR",
                message=f"Erro interno inesperado: {exc}",
                http_status=500,
            )
            return self._json_response(500, resp_headers, err.to_envelope(correlation_id))

    def _parse_json_body(self, body: Optional[bytes | str]) -> Dict[str, Any]:
        if not body:
            return {}
        raw = body.decode("utf-8") if isinstance(body, bytes) else body
        if not raw.strip():
            return {}
        try:
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ValueError("JSON root must be an object")
            return data
        except Exception as exc:
            raise AgroCountError(
                code="INVALID_JSON_PAYLOAD",
                message="Corpo da requisição JSON malformado.",
                http_status=400,
                details={"reason": str(exc)},
            ) from exc

    def _json_response(
        self,
        status_code: int,
        headers: Dict[str, str],
        data: Dict[str, Any],
    ) -> Tuple[int, Dict[str, str], bytes]:
        headers["Content-Type"] = "application/json; charset=utf-8"
        body_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        return status_code, headers, body_bytes


def create_http_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    app: Optional[AgroCountApp] = None,
) -> ThreadingHTTPServer:
    """Cria uma instância ThreadingHTTPServer conectada ao AgroCountApp."""
    agro_app = app or AgroCountApp()

    class RequestHandler(BaseHTTPRequestHandler):
        def _dispatch(self, method: str) -> None:
            content_len = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(content_len) if content_len > 0 else b""
            hdrs = {k: v for k, v in self.headers.items()}
            status, resp_headers, resp_body = agro_app.handle_request(
                method=method,
                raw_url=self.path,
                headers=hdrs,
                body=body,
            )
            self.send_response(status)
            for hk, hv in resp_headers.items():
                self.send_header(hk, hv)
            self.send_header("Content-Length", str(len(resp_body)))
            self.end_headers()
            self.wfile.write(resp_body)

        def do_GET(self) -> None:  # noqa: N802
            self._dispatch("GET")

        def do_POST(self) -> None:  # noqa: N802
            self._dispatch("POST")

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            return

    return ThreadingHTTPServer((host, port), RequestHandler)
