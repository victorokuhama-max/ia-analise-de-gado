// Controlador Frontend do Estúdio Web de Revisão HITL (`WebReviewStudioComponent`)
(function () {
  const state = {
    currentInspection: null,
    selectedBoxId: null,
    pendingActions: [],
  };

  function setStatus(msg) {
    const el = document.getElementById("live-status");
    if (el) el.textContent = msg;
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

    const queueEl = document.getElementById("uncertain-queue");
    queueEl.innerHTML = "";
    uncertain.forEach((box) => {
      const li = document.createElement("li");
      li.className = "queue-item";
      li.setAttribute("role", "option");
      li.setAttribute("aria-selected", box.id === state.selectedBoxId ? "true" : "false");
      li.textContent = `[?] ${box.id} — Confiança ${(box.confidence * 100).toFixed(1)}%`;
      li.onclick = () => {
        state.selectedBoxId = box.id;
        renderInspection(state.currentInspection);
      };
      queueEl.appendChild(li);
    });
  }

  document.addEventListener("keydown", (ev) => {
    if (!state.currentInspection) return;
    const uncertain = (state.currentInspection.detections || []).filter(
      (d) => d.review_status === "AI_UNCERTAIN"
    );
    if (ev.key === "ArrowRight" && uncertain.length > 0) {
      state.selectedBoxId = uncertain[0].id;
      setStatus(`Selecionada detecção incerta ${state.selectedBoxId}`);
    } else if (ev.key === " " && state.selectedBoxId) {
      state.pendingActions.push({ action: "CONFIRM", box_id: state.selectedBoxId });
      setStatus(`Confirmada detecção ${state.selectedBoxId}`);
    } else if (ev.key === "Delete" && state.selectedBoxId) {
      state.pendingActions.push({ action: "REMOVE_FALSE_POSITIVE", box_id: state.selectedBoxId });
      setStatus(`Removido falso positivo ${state.selectedBoxId}`);
    }
  });

  window.AgroCountStudio = { state, renderInspection, setStatus };
})();
