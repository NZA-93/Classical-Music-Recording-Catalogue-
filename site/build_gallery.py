#!/usr/bin/env python3
"""build_gallery.py — the immersive view.

Roon's strengths are worth taking: artwork at full scale, credits you can
follow, calm density. Roon's weakness is that it never tells you whether a
recording is any good. So the report survives intact inside the richer shell —
same evidence spine, same editions table, same honest gaps — and the imagery
carries you to it rather than replacing it.

Writes docs/gallery.html. No dependencies.
"""

import json
import pathlib

cat = json.loads(pathlib.Path("build/catalogue.json").read_text("utf-8"))

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --void:#0E110E; --panel:#161A15; --raised:#1D221C;
  --bone:#E8EBE3; --dim:#8A9488; --line:rgba(232,235,227,.14);
  --verd:#5AA294; --crimson:#C4515C; --gold:#C9A227;
}
html{scroll-behavior:smooth}
body{background:var(--void);color:var(--bone);
  font-family:"Newsreader",Georgia,serif;font-weight:400;font-size:17px;line-height:1.6}
.mono{font-family:"IBM Plex Mono",ui-monospace,monospace}
.lbl{font-family:"IBM Plex Mono",monospace;font-size:.58rem;font-weight:500;letter-spacing:.16em;
  text-transform:uppercase;color:var(--dim)}
a{color:var(--verd)}

/* bar */
.bar{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:1.4rem;
  padding:.9rem clamp(1rem,4vw,3rem);background:rgba(14,17,14,.92);
  backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.bar h1{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1rem;margin-right:auto}
.bar a{text-decoration:none;color:var(--dim);font-family:"IBM Plex Mono",monospace;
  font-size:.6rem;letter-spacing:.14em;text-transform:uppercase}
.bar a:hover{color:var(--bone)}

/* hero */
.hero{position:relative;min-height:clamp(20rem,46vh,30rem);display:flex;align-items:flex-end;
  padding:clamp(2rem,6vw,4rem);overflow:hidden}
.hero-art{position:absolute;inset:0;background-size:cover;background-position:center;
  filter:blur(26px) saturate(.5) brightness(.42);transform:scale(1.15)}
.hero-fall{position:absolute;inset:0;
  background:radial-gradient(120% 90% at 20% 0%,#22301f 0%,#0E110E 70%)}
.hero-veil{position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(14,17,14,.35) 0%,rgba(14,17,14,.92) 88%)}
.hero-in{position:relative;max-width:46rem}
.hero h2{font-family:"Bodoni Moda",serif;font-weight:400;
  font-size:clamp(2.6rem,8vw,5.4rem);line-height:.92;letter-spacing:-.02em;margin:.4rem 0}
.hero .cat{font-family:"Bodoni Moda",serif;font-style:italic;color:var(--dim);font-size:1.05rem}
.hero .stand{margin-top:1rem;color:var(--dim);max-width:34rem}

/* rail */
.rail-wrap{padding:clamp(1.6rem,4vw,2.6rem) clamp(1rem,4vw,3rem) 0}
.rail{display:flex;gap:1rem;overflow-x:auto;padding-bottom:1rem;scroll-snap-type:x mandatory}
.rail::-webkit-scrollbar{height:6px}
.rail::-webkit-scrollbar-thumb{background:var(--line)}
.card{flex:0 0 188px;scroll-snap-align:start;background:none;border:0;padding:0;
  cursor:pointer;text-align:left;color:inherit;font:inherit}
.card .art{width:188px;height:188px;background:var(--raised);position:relative;overflow:hidden;
  border:1px solid var(--line);transition:border-color .2s,transform .2s}
.card .art img{position:absolute;inset:0;z-index:1;width:100%;height:100%;object-fit:cover;display:block}
.card .art .plate{position:absolute;inset:0;z-index:0;display:flex;flex-direction:column;
  justify-content:space-between;padding:.7rem}
.card .art.has-art .plate{visibility:hidden}
.card .art .plate b{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.05rem;line-height:1.1}
.card[aria-selected="true"] .art{border-color:var(--verd);transform:translateY(-3px)}
.card .who{margin-top:.5rem;font-size:.9rem;font-weight:500;line-height:1.3}
.card .meta{margin-top:.2rem;font-family:"IBM Plex Mono",monospace;font-size:.62rem;font-weight:500;color:var(--dim)}
.card .st{color:var(--gold);letter-spacing:.1em}
.card .ref{color:var(--crimson)}

/* detail */
.detail{padding:clamp(1.6rem,4vw,3rem) clamp(1rem,4vw,3rem) 5rem;
  display:grid;grid-template-columns:minmax(0,1fr) 20rem;gap:clamp(1.5rem,4vw,3rem);
  max-width:88rem;margin:0 auto;align-items:start}
.report{background:var(--panel);border:1px solid var(--line);padding:clamp(1.2rem,3vw,2rem)}
.headline{font-size:1.22rem;font-weight:500;line-height:1.4;margin-bottom:.9rem}
.headline .dir{font-weight:600}
.headline .pub{color:var(--dim);font-weight:400}
.scorebox{display:grid;grid-template-columns:1fr 1fr;margin:0 0 1.4rem;
  border:1px solid var(--line);background:var(--raised)}
.scorebox .cell{padding:.75rem .85rem;min-height:5rem;display:flex;flex-direction:column;
  justify-content:space-between;gap:.35rem}
.scorebox .cell:nth-child(odd){border-right:1px solid var(--line)}
.scorebox .cell:nth-child(-n+2){border-bottom:1px solid var(--line)}
.scorebox .k{font-family:"IBM Plex Mono",monospace;font-size:.6rem;font-weight:600;
  letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}
.scorebox .v{font-family:"Bodoni Moda",serif;font-weight:500;font-size:1.5rem;line-height:1}
.scorebox .v.muted{font-size:1.05rem;color:var(--dim)}
.scorebox .sub{font-family:"IBM Plex Mono",monospace;font-size:.66rem;font-weight:500;color:var(--dim)}
.scorebox .stars{color:var(--gold);font-size:1.15rem;letter-spacing:.14em}
.scorebox .badge{align-self:flex-start;font-family:"IBM Plex Mono",monospace;font-size:.6rem;
  font-weight:600;letter-spacing:.13em;text-transform:uppercase;color:#0E110E;
  background:var(--crimson);padding:.25rem .45rem}
.scorebox .meter{display:block;width:100%;height:.5rem;background:rgba(232,235,227,.12)}
.scorebox .meter i{display:block;height:100%;background:var(--verd)}
.verdict{display:flex;flex-wrap:wrap;align-items:center;gap:.5rem 1rem;
  padding-bottom:1rem;border-bottom:1px solid var(--line);margin-bottom:1.2rem}
.stars{color:var(--gold);font-size:1.1rem;letter-spacing:.12em}
.badge{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.14em;
  text-transform:uppercase;color:#0E110E;background:var(--crimson);padding:.2rem .45rem}
.figs{font-family:"IBM Plex Mono",monospace;font-size:.66rem;color:var(--dim)}
.commentary{max-width:40rem;margin-bottom:1.5rem}
.anchors{list-style:none;display:grid;gap:.75rem;margin:.6rem 0 1.6rem;max-width:40rem}
.anchors li{padding-left:.9rem;border-left:1px solid var(--verd)}
.anchors .w{font-family:"Bodoni Moda",serif;font-size:.95rem;display:block}
.anchors .f{color:var(--dim);font-size:.9rem}

.influence{display:flex;height:28px;border:1px solid var(--line);overflow:hidden;margin-bottom:.5rem}
.seg{min-width:0;display:flex;align-items:center;padding:0 .35rem;overflow:hidden;
  font-family:"IBM Plex Mono",monospace;font-size:.56rem;color:#0E110E;white-space:nowrap;
  background:var(--verd);border-right:1px solid var(--void)}
.seg.flag{background:repeating-linear-gradient(135deg,rgba(232,235,227,.16) 0 3px,transparent 3px 6px);
  color:var(--dim)}

table{width:100%;border-collapse:collapse;font-size:.82rem;margin-top:.5rem}
th{text-align:left;font-family:"IBM Plex Mono",monospace;font-weight:500;font-size:.55rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--dim);
  padding:.35rem .5rem .35rem 0;border-bottom:1px solid var(--line)}
td{padding:.5rem .5rem .5rem 0;border-bottom:1px solid var(--line);vertical-align:top}
td.n{font-family:"IBM Plex Mono",monospace;font-size:.72rem;white-space:nowrap}
.chip{font-family:"IBM Plex Mono",monospace;font-size:.54rem;letter-spacing:.08em;
  text-transform:uppercase;padding:.15rem .4rem;border:1px solid currentColor;white-space:nowrap}
.c-good{color:var(--verd)} .c-mid{color:var(--dim)}
.c-bad{color:var(--crimson)} .c-none{color:var(--dim);border-style:dashed}

/* credits column — the Roon idea, applied to people who shaped the sound */
.aside{position:sticky;top:4.5rem;display:grid;gap:1.2rem}
.panel{background:var(--panel);border:1px solid var(--line);padding:1.1rem}
.panel h3{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.16em;
  text-transform:uppercase;color:var(--dim);font-weight:500;margin-bottom:.8rem}
.person{display:flex;justify-content:space-between;gap:.8rem;padding:.45rem 0;
  border-bottom:1px solid var(--line);font-size:.9rem}
.person:last-child{border-bottom:0}
.person .role{font-family:"IBM Plex Mono",monospace;font-size:.58rem;color:var(--dim);
  letter-spacing:.08em;text-transform:uppercase;padding-top:.25rem}
.person .name{text-align:right}
.person .name span{display:block;font-family:"IBM Plex Mono",monospace;
  font-size:.55rem;color:var(--crimson);letter-spacing:.06em}
.also{display:flex;flex-wrap:wrap;gap:.35rem;margin-top:.3rem}
.also a{font-family:"IBM Plex Mono",monospace;font-size:.58rem;letter-spacing:.05em;
  text-decoration:none;border:1px solid var(--line);padding:.2rem .4rem;color:var(--dim)}
.also a:hover{color:var(--bone);border-color:var(--verd)}
.meterline{display:flex;align-items:center;gap:.5rem;font-family:"IBM Plex Mono",monospace;
  font-size:.64rem;color:var(--dim)}
.meter{flex:1;height:.4rem;background:rgba(232,235,227,.12)}
.meter i{display:block;height:100%;background:var(--verd)}

footer{padding:2rem clamp(1rem,4vw,3rem) 4rem;border-top:1px solid var(--line);
  color:var(--dim);font-size:.82rem;max-width:46rem}

@media(max-width:900px){.detail{grid-template-columns:1fr}.aside{position:static}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
const C = __DATA__;
const FLAT = C.works.flatMap(w => w.recordings.map(r => ({...r, _w: w})));
const CHIP = {"preferred transfer":"c-good","sound and serviceable":"c-mid",
              "pass if you can":"c-bad","not yet assessed":"c-none"};
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const coverEdition = r => {
  const withMbid = (r.editions||[]).filter(e=>e.mbid);
  if(!withMbid.length) return null;
  const want = parseInt((String(r.published).match(/\\d{4}/)||[])[0]||"",10);
  if(!want) return withMbid[0];
  return withMbid.slice().sort((a,b)=>{
    const ya=parseInt((String(a.year).match(/\\d{4}/)||[])[0]||"9999",10);
    const yb=parseInt((String(b.year).match(/\\d{4}/)||[])[0]||"9999",10);
    return Math.abs(ya-want)-Math.abs(yb-want);
  })[0];
};
const cover = r => {
  const e = coverEdition(r);
  return e ? `https://coverartarchive.org/release/${e.mbid}/front-500` : null;
};

function art(r){
  const ed = coverEdition(r);
  const plate = `<div class="plate"><b>${esc(r.published.split(",")[0])}</b>
    <span class="lbl">${esc(r.published.split(",").pop().trim())}${ed?"":" · no cover"}</span></div>`;
  if(!ed) return plate;
  const url = `https://coverartarchive.org/release/${ed.mbid}/front-500`;
  return `${plate}<img src="${url}"
    srcset="https://coverartarchive.org/release/${ed.mbid}/front-250 250w, ${url} 500w"
    sizes="188px" alt="" loading="lazy"
    onload="this.parentElement.classList.add('has-art')"
    onerror="this.remove()">`;
}

/* rail */
document.getElementById("rail").innerHTML = FLAT.map((r,i)=>`
  <button class="card" role="tab" aria-selected="${i===0}" data-i="${i}">
    <div class="art">${art(r)}</div>
    <div class="who">${esc(r.director || r.soloists.split(",")[0])}</div>
    <div class="meta"><span class="st">${r.stars?"★".repeat(r.stars):"—"}</span>
      ${r.reference?'<span class="ref"> RÉF</span>':""} · ${esc(r.published.split(",").pop().trim())}</div>
  </button>`).join("");

function influence(r){
  const tot = r.sources.reduce((a,s)=>a+s.weight,0)||1;
  return r.sources.map(s=>{
    const pct=(s.weight/tot)*100;
    return `<div class="seg${s.conflict?" flag":""}" style="flex:0 0 ${pct}%"
      title="${esc(s.source)} — ${esc(s.provenance)}, score ${s.score.toFixed(2)}, weight ${s.weight.toFixed(2)}">
      ${pct>16?s.weight.toFixed(2):""}</div>`;
  }).join("");
}

function render(i){
  const r = FLAT[i], w = r._w;
  document.querySelectorAll(".card").forEach((c,j)=>c.setAttribute("aria-selected", j===i));
  const url = cover(r);
  const heroArt = document.getElementById("hero-art");
  heroArt.style.backgroundImage = url ? `url(${url})` : "";
  heroArt.style.display = url ? "block" : "none";
  document.getElementById("hero-title").textContent = w.title;
  document.getElementById("hero-cat").textContent = `${w.composer} · ${w.cat}`;
  document.getElementById("hero-stand").textContent = w.standfirst;

  const eds = r.editions.map(e=>`<tr>
    <td>${esc(e.label)} <span class="n">${esc(e.catno)}</span><br>
      <span class="lbl">${esc(e.format)}</span></td>
    <td class="n">${esc(e.year)}</td>
    <td>${esc(e.transfer)}</td>
    <td class="n">${e.sound!=null?e.sound.toFixed(2):"—"}</td>
    <td><span class="chip ${CHIP[e.verdict]||"c-none"}">${esc(e.verdict)}</span></td></tr>`).join("");

  const un = r.interpretation===null;
  const st = [0,1,2].map(i=>`<span class="${!un&&i<r.stars?"on":"off"}">★</span>`).join("");
  const confPct = un?0:Math.max(0,Math.min(100,r.confidence*100));
  const soundCell = r.sound_best==null
    ?`<span class="v muted">—</span><span class="sub">not yet assessed</span>`
    :`<span class="v">${r.sound_best.toFixed(2)}</span><span class="sub">best edition</span>`;
  const interpCell = un
    ?`<span class="v muted">—</span><span class="sub">awaiting sources</span>`
    :`<span class="stars">${st}</span><span class="v">${r.interpretation.toFixed(3)}</span>`;
  const stand = r.reference
    ?`<span class="badge">Référence</span><span class="sub">interpretation only</span>`
    :`<span class="v muted">${un?"—":"no"}</span><span class="sub">référence</span>`;

  document.getElementById("report").innerHTML = `
    <p class="headline">${esc(r.soloists)} — <span class="dir">${esc(r.director)}</span> —
      ${esc(r.ensemble)} <span class="pub">(${esc(r.published)})</span></p>
    <div class="scorebox" role="group" aria-label="Recording scores">
      <div class="cell"><span class="k">Interpretation</span>${interpCell}</div>
      <div class="cell"><span class="k">Sound</span>${soundCell}</div>
      <div class="cell"><span class="k">Confidence</span>
        <span class="v">${un?"—":r.confidence.toFixed(2)}</span>
        <span class="meter" aria-hidden="true"><i style="width:${confPct.toFixed(0)}%"></i></span>
      </div>
      <div class="cell"><span class="k">Standing</span>${stand}</div>
    </div>
    <p class="lbl">What to listen for</p>
    <ul class="anchors">${r.anchors.map(a=>`<li><span class="w">${esc(a.where)}</span>
      <span class="f">${esc(a.listen_for)}</span></li>`).join("")}</ul>
    ${r.interpretation===null?"":`<p class="lbl">Influence — who this verdict rests on</p>
    <div class="influence">${influence(r)}</div>`}
    <p class="lbl" style="margin-top:1.4rem">Editions and transfers</p>
    <table><thead><tr><th>Edition</th><th>Year</th><th>What it did to the sound</th>
      <th>Sound</th><th>Verdict</th></tr></thead><tbody>${eds}</tbody></table>`;

  const e = r.engineering, miss = '<span>not established</span>';
  const others = FLAT.filter((o,j)=>j!==i && (o.engineering.producer===e.producer ||
                   o._w.id===w.id)).slice(0,4);
  document.getElementById("aside").innerHTML = `
    <div class="panel">
      <h3>Made by</h3>
      <div class="person"><span class="role">Venue</span><span class="name">${esc(e.venue)}</span></div>
      <div class="person"><span class="role">Sessions</span><span class="name">${esc(e.sessions)}</span></div>
      <div class="person"><span class="role">Producer</span><span class="name">${e.producer?esc(e.producer):miss}</span></div>
      <div class="person"><span class="role">Engineer</span><span class="name">${e.engineer?esc(e.engineer):miss}</span></div>
      <div class="person"><span class="role">Credits</span><span class="name">${esc(e.status)}</span></div>
    </div>
    <div class="panel">
      <h3>Sound, best edition</h3>
      <div class="meterline"><span class="meter"><i style="width:${r.sound_best!=null?(((r.sound_best-1.5)/1.5)*100).toFixed(0):0}%"></i></span>
        ${r.sound_best!=null?r.sound_best.toFixed(2):"—"}</div>
      <p class="lbl" style="margin-top:.7rem">${r.sound_best!=null?esc(r.sound_best_edition):"no edition assessed"}</p>
    </div>
    <div class="panel">
      <h3>Follow the thread</h3>
      <div class="also">${others.map(o=>`<a href="#" data-i="${FLAT.indexOf(o)}">${esc(o.director||o.soloists.split(",")[0])}</a>`).join("")}</div>
    </div>`;
  document.querySelectorAll(".also a").forEach(a=>a.addEventListener("click",ev=>{
    ev.preventDefault(); render(+a.dataset.i); window.scrollTo({top:0,behavior:"smooth"});
  }));
}

document.getElementById("rail").addEventListener("click", e=>{
  const b = e.target.closest(".card"); if(b) render(+b.dataset.i);
});
render(0);
"""

html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Critical Discography — Gallery</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:opsz,wght@6..96,400;6..96,500;6..96,600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body>

<div class="bar">
  <h1>Critical Discography</h1>
  <a href="index.html">Catalogue</a>
  <a href="entries.html">Report view</a>
</div>

<section class="hero">
  <div class="hero-fall"></div>
  <div class="hero-art" id="hero-art"></div>
  <div class="hero-veil"></div>
  <div class="hero-in">
    <p class="lbl" id="hero-cat"></p>
    <h2 id="hero-title"></h2>
    <p class="stand" id="hero-stand"></p>
  </div>
</section>

<div class="rail-wrap">
  <p class="lbl" style="margin-bottom:.7rem">Recordings assessed</p>
  <div class="rail" id="rail" role="tablist"></div>
</div>

<div class="detail">
  <div class="report" id="report"></div>
  <div class="aside" id="aside"></div>
</div>

<footer>
  <p>The gallery is the same catalogue as the report view, differently paced. Artwork and
  credits carry you toward a judgement; they do not replace it. Every score here still shows
  who it rests on, and every gap is still visible.</p>
</footer>

<script>{JS.replace("__DATA__", json.dumps(cat, ensure_ascii=False))}</script>
</body></html>"""

pathlib.Path("docs/gallery.html").write_text(html, "utf-8")
n = sum(len(w["recordings"]) for w in cat["works"])
print(f"docs/gallery.html · {n} recordings")
