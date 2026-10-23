// Controlador Frontend Interativo do Estúdio Web de Revisão HITL (`WebReviewStudioComponent`)
(function () {
  const state = {
    currentFarm: null,
    currentPaddock: null,
    currentInspection: null,
    selectedBoxId: null,
    pendingActions: [],
  };

  function setStatus(msg) {
    const el = document.getElementById("live-status");
    if (el) el.textContent = msg;
  }

  function logConsole(obj) {
    const el = document.getElementById("output-console");
    if (el) {
      el.textContent = typeof obj === "string" ? obj : JSON.stringify(obj, null, 2);
    }
  }

  async function api(method, path, body) {
    const opts = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body !== undefined) {
      opts.body = JSON.stringify(body);
    }
    const resp = await fetch(path, opts);
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.error ? `${data.error.code}: ${data.error.message}` : `HTTP ${resp.status}`);
    }
    return data;
  }

  async function refreshModelBadge() {
    try {
      const m = await api("GET", "/api/v1/models/active");
      const badge = document.getElementById("active-model-badge");
      if (badge && m.active_model) {
        const acc = (m.active_model.validation_counting_accuracy * 100).toFixed(1);
        const samples = m.golden_dataset_status ? m.golden_dataset_status.total_curated_samples : 0;
        badge.textContent = `Modelo Ativo: ${m.active_model.version_tag} (${acc}% | Golden Dataset: ${samples})`;
      }
    } catch (e) {
      console.error(e);
    }
  }

  function renderCanvasBoxes(insp) {
    const layer = document.getElementById("canvas-boxes-layer");
    if (!layer) return;
    layer.innerHTML = "";
    const dets = insp.detections || [];
    dets.forEach((box) => {
      if (box.review_status === "HUMAN_REMOVED_FP") return;
      const pill = document.createElement("span");
      pill.style.display = "inline-block";
      pill.style.margin = "4px";
      pill.style.padding = "4px 8px";
      pill.style.borderRadius = "6px";
      pill.style.fontSize = "0.8rem";
      pill.style.cursor = "pointer";

      if (box.review_status === "AI_UNCERTAIN") {
        pill.style.border = "2px dashed #D97706";
        pill.style.background = box.id === state.selectedBoxId ? "#78350F" : "rgba(217, 119, 6, 0.18)";
        pill.textContent = `[?] ${box.id} (${(box.confidence * 100).toFixed(0)}%)`;
      } else if (box.review_status === "HUMAN_ADDED") {
        pill.style.border = "3px double #2563EB";
        pill.style.background = "rgba(37, 99, 235, 0.22)";
        pill.textContent = `[+H] ${box.id} (Manual FN)`;
      } else {
        pill.style.border = "2px solid #15803D";
        pill.style.background = "rgba(21, 128, 61, 0.22)";
        pill.textContent = `[✓] ${box.id} (${(box.confidence * 100).toFixed(0)}%)`;
      }
      pill.onclick = () => {
        state.selectedBoxId = box.id;
        renderInspection(state.currentInspection);
      };
      layer.appendChild(pill);
    });
  }

  function renderInspection(insp) {
    state.currentInspection = insp;
    document.getElementById("val-raw-count").textContent = `${insp.raw_ai_count} cabeças`;
    const uncertain = (insp.detections || []).filter((d) => d.review_status === "AI_UNCERTAIN");
    document.getElementById("val-uncertain-count").textContent = `${uncertain.length} pendentes`;
    document.getElementById("val-audited-count").textContent =
      insp.final_audited_count !== null && insp.final_audited_count !== undefined
        ? `${insp.final_audited_count} cabeças`
        : "Aguardando revisão";

    renderCanvasBoxes(insp);

    const queueEl = document.getElementById("uncertain-queue");
    queueEl.innerHTML = "";
    uncertain.forEach((box) => {
      const li = document.createElement("li");
      li.className = "queue-item";
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", box.id === state.selectedBoxId ? "true" : "false");

      const labelSpan = document.createElement("span");
      labelSpan.textContent = `[?] ${box.id} — Confiança ${(box.confidence * 100).toFixed(1)}%`;

      const actionsDiv = document.createElement("div");
      actionsDiv.style.display = "flex";
      actionsDiv.style.gap = "6px";

      const btnConf = document.createElement("button");
      btnConf.className = "btn btn-primary";
      btnConf.style.minHeight = "30px";
      btnConf.style.padding = "4px 10px";
      btnConf.textContent = "Confirmar (Espaço)";
      btnConf.onclick = (e) => {
        e.stopPropagation();
        box.review_status = "HUMAN_CONFIRMED";
        state.pendingActions.push({ action: "CONFIRM", box_id: box.id });
        setStatus(`Confirmada detecção ${box.id}`);
        renderInspection(state.currentInspection);
      };

      const btnRem = document.createElement("button");
      btnRem.className = "btn btn-secondary";
      btnRem.style.minHeight = "30px";
      btnRem.style.padding = "4px 10px";
      btnRem.textContent = "Remover FP (Del)";
      btnRem.onclick = (e) => {
        e.stopPropagation();
        box.review_status = "HUMAN_REMOVED_FP";
        state.pendingActions.push({ action: "REMOVE_FALSE_POSITIVE", box_id: box.id });
        setStatus(`Removido falso positivo ${box.id}`);
        renderInspection(state.currentInspection);
      };

      actionsDiv.appendChild(btnConf);
      actionsDiv.appendChild(btnRem);
      li.appendChild(labelSpan);
      li.appendChild(actionsDiv);
      li.onclick = () => {
        state.selectedBoxId = box.id;
        renderInspection(state.currentInspection);
      };
      queueEl.appendChild(li);
    });
  }

  async function ensureFarmExists() {
    const farmsRes = await api("GET", "/api/v1/farms");
    if (farmsRes.items && farmsRes.items.length > 0) {
      state.currentFarm = farmsRes.items[0];
      state.currentPaddock = state.currentFarm.paddocks[0];
      return;
    }
    const created = await api("POST", "/api/v1/farms", {
      name: "Fazenda Santa Fé (Nelore)",
      code: "FSF-01",
      paddocks: [{ name: "Piquete Maternidade Norte", code: "PMN-01", area_hectares: 68.5 }],
    });
    state.currentFarm = created;
    state.currentPaddock = created.paddocks[0];
  }

  async function createDemoInspection() {
    try {
      setStatus("Processando voo de drone com SAHI + YOLO...");
      await ensureFarmExists();
      const alt = parseInt(document.getElementById("input-altitude").value || "60", 10);
      const ovl = parseInt(document.getElementById("input-overlap").value || "75", 10);
      const idem = `voo-${Date.now()}`;
      const insp = await api("POST", "/api/v1/inspections", {
        farm_id: state.currentFarm.id,
        paddock_id: state.currentPaddock.id,
        idempotency_key: idem,
        media_type: "IMAGE_4K",
        source_uri: `gs://agrocount-storage/flights/${idem}.jpg`,
        file_size_bytes: 25165824,
        flight_altitude_m: alt,
        overlap_pct: ovl,
      });
      state.pendingActions = [];
      state.selectedBoxId = null;
      renderInspection(insp);
      logConsole(insp);
      setStatus(`Inspeção ${insp.id} processada: ${insp.raw_ai_count} cabeças detectadas.`);
    } catch (err) {
      setStatus(`Erro: ${err.message}`);
      logConsole({ error: err.message });
    }
  }

  async function finalizeHitlReview() {
    if (!state.currentInspection) {
      setStatus("Crie ou selecione uma inspeção primeiro.");
      return;
    }
    try {
      // Auto-confirma quaisquer incertas restantes para facilitar o fluxo de 1 clique
      const remaining = (state.currentInspection.detections || []).filter(
        (d) => d.review_status === "AI_UNCERTAIN"
      );
      remaining.forEach((b) => {
        state.pendingActions.push({ action: "CONFIRM", box_id: b.id });
      });
      const res = await api("POST", `/api/v1/inspections/${state.currentInspection.id}/hitl-review`, {
        auditor_id: "auditor-web",
        actions: state.pendingActions,
      });
      const updated = await api("GET", `/api/v1/inspections/${state.currentInspection.id}`);
      renderInspection(updated);
      await refreshModelBadge();
      logConsole(res);
      setStatus(
        `Auditoria concluída! Contagem final: ${res.final_audited_count} cabeças. Amostra ${res.golden_dataset_sample.sample_id} salva no Golden Dataset.`
      );
    } catch (err) {
      setStatus(`Erro na revisão HITL: ${err.message}`);
      logConsole({ error: err.message });
    }
  }

  async function triggerFineTuning() {
    try {
      setStatus("Iniciando job de Fine-Tuning no Golden Dataset (Gate >= 95%)...");
      const res = await api("POST", "/api/v1/models/fine-tune", {
        min_new_golden_samples: 1,
        target_epochs: 30,
      });
      await refreshModelBadge();
      logConsole(res);
      setStatus(`Fine-Tuning concluído: ${res.candidate_version_tag} -> ${res.promotion_gate_result}`);
    } catch (err) {
      setStatus(`Aviso Fine-Tuning: ${err.message}`);
      logConsole({ error: err.message });
    }
  }

  async function exportReport(fmt) {
    if (!state.currentInspection) {
      setStatus("Nenhuma inspeção ativa para exportar.");
      return;
    }
    try {
      const res = await api("GET", `/api/v1/inspections/${state.currentInspection.id}/report?format=${fmt}`);
      logConsole(res);
      setStatus(`Laudo ${fmt} gerado com sucesso (${res.sha256_checksum.slice(0, 22)}...).`);
    } catch (err) {
      setStatus(`Erro ao exportar laudo ${fmt}: ${err.message}`);
      logConsole({ error: err.message });
    }
  }

  document.addEventListener("keydown", (ev) => {
    if (!state.currentInspection) return;
    const uncertain = (state.currentInspection.detections || []).filter(
      (d) => d.review_status === "AI_UNCERTAIN"
    );
    if (ev.key === "ArrowRight" && uncertain.length > 0) {
      state.selectedBoxId = uncertain[0].id;
      setStatus(`Selecionada detecção incerta ${state.selectedBoxId}`);
      renderInspection(state.currentInspection);
    } else if (ev.key === " " && state.selectedBoxId) {
      ev.preventDefault();
      const target = uncertain.find((b) => b.id === state.selectedBoxId);
      if (target) {
        target.review_status = "HUMAN_CONFIRMED";
        state.pendingActions.push({ action: "CONFIRM", box_id: state.selectedBoxId });
        setStatus(`Confirmada detecção ${state.selectedBoxId}`);
        renderInspection(state.currentInspection);
      }
    } else if (ev.key === "Delete" && state.selectedBoxId) {
      const target = uncertain.find((b) => b.id === state.selectedBoxId);
      if (target) {
        target.review_status = "HUMAN_REMOVED_FP";
        state.pendingActions.push({ action: "REMOVE_FALSE_POSITIVE", box_id: state.selectedBoxId });
        setStatus(`Removido falso positivo ${state.selectedBoxId}`);
        renderInspection(state.currentInspection);
      }
    } else if (ev.key === "n" || ev.key === "N") {
      state.pendingActions.push({
        action: "ADD_FALSE_NEGATIVE",
        new_box: { x_center: 0.5, y_center: 0.5, width: 0.045, height: 0.055 },
      });
      setStatus("Adicionado animal omitido (Falso Negativo +H) na fila de submissão.");
    }
  });

  window.addEventListener("DOMContentLoaded", async () => {
    const btnCreate = document.getElementById("btn-create-demo-inspection");
    if (btnCreate) btnCreate.onclick = createDemoInspection;

    const btnApprove = document.getElementById("btn-approve-finalize");
    if (btnApprove) btnApprove.onclick = finalizeHitlReview;

    const btnFt = document.getElementById("btn-trigger-finetune");
    if (btnFt) btnFt.onclick = triggerFineTuning;

    const btnPdf = document.getElementById("btn-export-pdf");
    if (btnPdf) btnPdf.onclick = () => exportReport("PDF");

    const btnCsv = document.getElementById("btn-export-csv");
    if (btnCsv) btnCsv.onclick = () => exportReport("CSV");

    await refreshModelBadge();
    await createDemoInspection();
  });

  window.AgroCountStudio = { state, renderInspection, setStatus };
})();
