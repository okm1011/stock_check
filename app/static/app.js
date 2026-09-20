const cfg = window.STOCK_CHECK || { pollInterval: 60, categories: [] };
const $ = (id) => document.getElementById(id);

const state = {
  rows: [],
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

function currentCats() {
  const extra = [...new Set(state.rows.map((r) => r.category).filter(Boolean))];
  return [...new Set([...(cfg.categories || []), ...extra])];
}

function catOptions(selected) {
  return currentCats()
    .map((c) => `<option value="${esc(c)}" ${c === selected ? "selected" : ""}>${esc(c)}</option>`)
    .join("");
}

function esc(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll('"', "&quot;");
}

function filtered() {
  const q = $("q").value.trim().toUpperCase();
  const cat = $("catFilter").value;
  let rows = state.rows.slice();
  if (cat) rows = rows.filter((r) => r.category === cat);
  if (q) {
    rows = rows.filter(
      (r) =>
        r.symbol.includes(q) ||
        (r.base || "").toUpperCase().includes(q) ||
        (r.memo || "").toUpperCase().includes(q)
    );
  }
  const sort = $("sort").value;
  rows.sort((a, b) => {
    if (sort === "symbol") return a.symbol.localeCompare(b.symbol);
    if (sort === "volume_desc") return (b.quote_volume || 0) - (a.quote_volume || 0);
    const av = a.change_pct, bv = b.change_pct;
    if (av == null && bv == null) return a.symbol.localeCompare(b.symbol);
    if (av == null) return 1;
    if (bv == null) return -1;
    return sort === "change_asc" ? av - bv : bv - av;
  });
  return rows;
}

function render() {
  const rows = filtered();
  const tbody = $("tbody");
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="empty">조건에 맞는 종목이 없습니다</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map((r, i) => {
      const ch = fmtChg(r.change_pct);
      return `<tr data-symbol="${esc(r.symbol)}">
        <td class="num">${i + 1}</td>
        <td><span class="sym">${esc(r.base || r.symbol)}</span><span class="base">${esc(r.symbol)}</span></td>
        <td class="num">${fmtPrice(r.price)}</td>
        <td class="num ${ch.cls}">${ch.text}</td>
        <td class="num">${fmtVol(r.quote_volume)}</td>
        <td>
          <select class="cat">
            ${catOptions(r.category)}
            <option value="__custom__">직접 입력…</option>
          </select>
        </td>
        <td><input class="memo" value="${esc(r.memo)}" maxlength="500" placeholder="메모" /></td>
      </tr>`;
    })
    .join("");
}

function applyStatus(data) {
  const el = $("status");
  const n = data.count || data.rows?.length || 0;
  const bits = [`${n}종목`, `갱신 ${fmtTime(data.updated_at)}`, data.poll_status || ""];
  if (data.backfill) bits.push("과거가 채우는 중");
  el.textContent = bits.filter(Boolean).join(" · ");
  el.className = "status " + (data.poll_status === "error" ? "err" : "ok");
  if (data.last_error) el.title = data.last_error;
}

async function load() {
  const period = $("period").value;
  const res = await fetch(`/api/rows?period=${encodeURIComponent(period)}`);
  const data = await res.json();
  state.rows = data.rows || [];
  state.updatedAt = data.updated_at;
  state.backfill = !!data.backfill;
  applyStatus(data);
  const cat = $("catFilter");
  const keep = cat.value;
  const opts = ['<option value="">전체</option>']
    .concat(currentCats().map((c) => `<option value="${esc(c)}">${esc(c)}</option>`));
  cat.innerHTML = opts.join("");
  cat.value = keep;
  render();
}

async function saveRow(tr) {
  const symbol = tr.dataset.symbol;
  const category = tr.querySelector(".cat").value;
  const memo = tr.querySelector(".memo").value;
  const row = state.rows.find((r) => r.symbol === symbol);
  if (row) {
    row.category = category;
    row.memo = memo;
  }
  await fetch(`/api/notes/${encodeURIComponent(symbol)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category, memo }),
  });
}

$("tbody").addEventListener("change", async (e) => {
  const tr = e.target.closest("tr");
  if (!tr) return;
  if (e.target.classList.contains("cat") && e.target.value === "__custom__") {
    const name = prompt("분류 이름");
    if (!name) {
      e.target.value = "미분류";
      return;
    }
    if (![...e.target.options].some((o) => o.value === name)) {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      e.target.insertBefore(opt, e.target.lastElementChild);
    }
    e.target.value = name;
  }
  await saveRow(tr);
});

let memoTimer = null;
$("tbody").addEventListener("input", (e) => {
  if (!e.target.classList.contains("memo")) return;
  const tr = e.target.closest("tr");
  clearTimeout(memoTimer);
  memoTimer = setTimeout(() => saveRow(tr), 400);
});

["period", "catFilter", "sort"].forEach((id) => $(id).addEventListener("change", () => {
  if (id === "period") load();
  else render();
}));
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
