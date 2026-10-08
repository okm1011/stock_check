const cfg = window.STOCK_CHECK || { pollInterval: 60 };
const $ = (id) => document.getElementById(id);

const state = {
  rows: [],
  macro: [],
  tagGroups: [],
  altCount: 0,
  altStrength: null,
  tag: "all",
  updatedAt: null,
  backfill: false,
};

function fmtPrice(v) {
  if (v == null || Number.isNaN(v)) return "—";
  const n = Number(v);
  if (n >= 1000) return n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  if (n >= 1) return n.toLocaleString("en-US", { maximumFractionDigits: 4 });
  return n.toPrecision(4);
}

function fmtChg(v) {
  if (v == null || Number.isNaN(v)) return { text: "—", cls: "flat" };
  const n = Number(v);
  const sign = n > 0 ? "+" : "";
  const cls = n > 0 ? "up" : n < 0 ? "down" : "flat";
  return { text: `${sign}${n.toFixed(2)}%`, cls };
}

function fmtMetric(v) {
  if (v == null || Number.isNaN(Number(v))) return "—";
  const n = Number(v);
  if (Math.abs(n) >= 100) return n.toFixed(0);
  if (Math.abs(n) >= 10) return n.toFixed(1);
  return n.toFixed(2);
}

function fmtVol(v) {
  if (v == null) return "—";
  const n = Number(v);
  if (n >= 1e9) return (n / 1e9).toFixed(2) + "B";
  if (n >= 1e6) return (n / 1e6).toFixed(1) + "M";
  if (n >= 1e3) return (n / 1e3).toFixed(0) + "K";
  return n.toFixed(0);
}

function fmtTime(ts) {
  if (!ts) return "아직 없음";
  return new Date(ts * 1000).toLocaleTimeString("ko-KR", { hour12: false });
}

function esc(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll('"', "&quot;");
}

function altRows() {
  return state.rows.filter((r) => !r.is_macro);
}

function filtered() {
  const q = $("q").value.trim().toUpperCase();
  const rawQ = $("q").value.trim();
  let rows = altRows();
  if (state.tag === "기타") rows = rows.filter((r) => !(r.tags || []).length);
  else if (state.tag !== "all") rows = rows.filter((r) => (r.tags || []).includes(state.tag));
  if (q) {
    rows = rows.filter(
      (r) =>
        r.symbol.includes(q) ||
        (r.base || "").toUpperCase().includes(q) ||
        (r.brief || "").toUpperCase().includes(q) ||
        (r.tags || []).some((t) => String(t).toUpperCase().includes(q) || String(t).includes(rawQ))
    );
  }
  const sort = $("sort").value;
  rows.sort((a, b) => {
    if (sort === "symbol") return a.symbol.localeCompare(b.symbol);
    if (sort === "volume_desc") return (b.quote_volume || 0) - (a.quote_volume || 0);
    if (sort === "popularity_desc" || sort === "growth_desc") {
      const key = sort === "popularity_desc" ? "popularity" : "growth";
      const av = a[key], bv = b[key];
      if (av == null && bv == null) return a.symbol.localeCompare(b.symbol);
      if (av == null) return 1;
      if (bv == null) return -1;
      return bv - av;
    }
    const av = a.change_pct, bv = b.change_pct;
    if (av == null && bv == null) return a.symbol.localeCompare(b.symbol);
    if (av == null) return 1;
    if (bv == null) return -1;
    return sort === "change_asc" ? av - bv : bv - av;
  });
  return rows;
}

function renderMacro() {
  const el = $("macro");
  el.innerHTML = (state.macro || [])
    .map((m) => {
      const ch = fmtChg(m.change_pct);
      const off = m.listed === false;
      return `<article class="glass macro-card ${off ? "off" : ""}">
        <div>
          <div class="name">${esc(m.label)}</div>
          <div class="hint">${esc(m.hint || m.symbol)}${off ? " · 미상장" : ""}</div>
        </div>
        <div>
          <div class="px">${fmtPrice(m.price)}</div>
          <div class="chg ${ch.cls}">${ch.text}</div>
        </div>
      </article>`;
    })
    .join("");
}

function renderChips() {
  const el = $("chips");
  const all = {
    id: "all",
    label: "전체",
    count: state.altCount,
    ...(state.altStrength || {}),
  };
  const items = [all].concat(state.tagGroups || []);
  el.innerHTML = items
    .map((s) => {
      const ch = fmtChg(s.median_chg);
      const br = s.up_pct == null ? "—" : `${Number(s.up_pct).toFixed(0)}%↑`;
      return `<button type="button" class="chip ${state.tag === s.id ? "on" : ""}" data-tag="${esc(s.id)}">
        <span class="chip-name">${esc(s.label)} <em>${s.count ?? 0}</em></span>
        <span class="chip-med ${ch.cls}">${ch.text}</span>
        <span class="chip-br">${br}</span>
      </button>`;
    })
    .join("");
}

function renderTable() {
  const rows = filtered();
  const tbody = $("tbody");
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="10" class="empty">조건에 맞는 종목이 없습니다</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map((r, i) => {
      const ch = fmtChg(r.change_pct);
      const tags = (r.tags || []).map((t) => `<span class="tag">${esc(t)}</span>`).join("");
      return `<tr>
        <td class="num">${i + 1}</td>
        <td><span class="sym">${esc(r.base || r.symbol)}</span><span class="base">${esc(r.symbol)}</span></td>
        <td><div class="tags">${tags || "—"}</div></td>
        <td class="num">${fmtPrice(r.price)}</td>
        <td class="num ${ch.cls}">${ch.text}</td>
        <td class="num">${fmtVol(r.quote_volume)}</td>
        <td class="num">${fmtMetric(r.popularity)}</td>
        <td class="num">${fmtMetric(r.growth)}</td>
        <td class="num">${fmtMetric(r.transparency)}</td>
        <td><div class="brief" title="${esc(r.brief)}">${esc(r.brief) || "—"}</div></td>
      </tr>`;
    })
    .join("");
}

function render() {
  renderMacro();
  renderChips();
  renderTable();
  $("altMeta").textContent = `알트 ${state.altCount}종 · 칩 = 태그별 중간값 변동 / 상승비율 (선택 기간)`;
}

function rootdataLabel(data) {
  const st = data.rootdata_status || "";
  if (st === "sync") return data.rootdata_error ? `RootData ${data.rootdata_error}` : "RootData 갱신 중";
  if (st === "error") return "RootData 오류";
  if (st === "wait") return "RootData 종목 대기";
  if (data.rootdata_updated_at) return `RootData ${fmtTime(data.rootdata_updated_at)}`;
  return "";
}

function applyStatus(data) {
  const el = $("status");
  const bits = [
    `알트 ${data.alt_count ?? 0}`,
    `갱신 ${fmtTime(data.updated_at)}`,
    data.poll_status || "",
    rootdataLabel(data),
  ];
  if (data.backfill) bits.push("과거가 채우는 중");
  el.textContent = bits.filter(Boolean).join(" · ");
  el.className = "status " + (data.poll_status === "error" || data.rootdata_status === "error" ? "err" : "ok");
  el.title = data.rootdata_error || data.last_error || "";
}

async function load() {
  const period = $("period").value;
  const res = await fetch(`/api/rows?period=${encodeURIComponent(period)}`);
  const data = await res.json();
  state.rows = data.rows || [];
  state.macro = data.macro || [];
  state.tagGroups = data.tag_groups || [];
  state.altCount = data.alt_count || 0;
  state.altStrength = data.alt_strength || null;
  state.updatedAt = data.updated_at;
  state.backfill = !!data.backfill;
  applyStatus(data);
  render();
}

$("chips").addEventListener("click", (e) => {
  const btn = e.target.closest("[data-tag]");
  if (!btn) return;
  state.tag = btn.dataset.tag;
  render();
});

["period", "sort"].forEach((id) =>
  $(id).addEventListener("change", () => {
    if (id === "period") load();
    else render();
  })
);
$("q").addEventListener("input", render);

load();
setInterval(load, Math.max(15, Number(cfg.pollInterval) || 60) * 1000);
let bootTries = 0;
const bootTimer = setInterval(() => {
  if (state.rows.length || bootTries++ > 20) {
    clearInterval(bootTimer);
    return;
  }
  load();
}, 2000);
