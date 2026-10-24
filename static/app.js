const $ = id => document.getElementById(id);
const ids = ["month","avg_temp","occupants","ac_hours","prev_units","prev2_units"];

async function predict() {
  $("err").textContent = "";
  const body = {}; ids.forEach(i => body[i] = $(i).value);
  const r = await fetch("/api/predict", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const d = await r.json();
  if (!r.ok) { $("err").textContent = d.error || "Error"; return; }
  $("result").hidden = false;
  $("units").textContent = d.predicted_units;
  $("total").textContent = "₹" + d.bill.total;
  $("meta").textContent = `Model: ${d.model} · typical error ±${d.mae} kWh`;
  $("rows").innerHTML = d.bill.breakdown.map(b =>
    `<tr><td>${b.from}–${b.to}</td><td>${b.units}</td><td>₹${b.rate}</td><td>₹${b.cost}</td></tr>`).join("");
  $("extras").textContent = `Energy ₹${d.bill.energy_charge} + fixed ₹${d.bill.fixed_charge} + tax ₹${d.bill.tax}`;
  loadHistory();
}

async function loadHistory() {
  const rows = (await (await fetch("/api/history")).json()).reverse();
  const c = $("chart"), ctx = c.getContext("2d");
  c.width = c.clientWidth; ctx.clearRect(0,0,c.width,c.height);
  if (!rows.length) return;
  const max = Math.max(...rows.map(r => r.amount)) * 1.15, w = c.width / rows.length;
  rows.forEach((r,i) => {
    const h = r.amount / max * (c.height - 24);
    ctx.fillStyle = "#2a9d8f"; ctx.fillRect(i*w+6, c.height-h-14, w-12, h);
    ctx.fillStyle = "#333"; ctx.font = "11px sans-serif"; ctx.fillText("₹"+Math.round(r.amount), i*w+6, c.height-h-18);
  });
}
$("go").addEventListener("click", predict);
loadHistory();
