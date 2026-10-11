"""Fixed, inspectable storefront source generator. No provider or arbitrary code."""
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FEATURES = {
    "item_details": {"title": "Item details", "description": "Materials, descriptions and useful missing-item responses."},
    "category_filter": {"title": "Category browsing", "description": "Filter the collection without losing matching objects."},
    "cart_total": {"title": "Shopping bag", "description": "Add, remove and change quantities with exact cent arithmetic."},
    "search": {"title": "Catalog search", "description": "Find an object by its name or description."},
}

CATALOG_SOURCE = '''import {readFileSync} from 'node:fs';
// The browser receives its catalog via app.mjs. Node QA reads the same JSON.
export const totalMultiplier = 1;
export function lookup(products, id) {
  if (!Number.isInteger(id) || id < 1) return {status:400,message:'Choose a positive whole-number item ID.'};
  const item = products.find(p => p.id === id);
  return item ? {status:200,item} : {status:404,message:'This item is not in the collection.'};
}
export function filterCatalog(products, category = 'All', query = '') {
  return products.filter(p => (category === 'All' || p.category === category) &&
    (p.name + ' ' + p.description).toLowerCase().includes(query.trim().toLowerCase()));
}
export function bagTotal(products, lines) {
  let cents = 0;
  for (const {id, quantity} of lines) {
    const result = lookup(products, id);
    if (result.status !== 200 || !Number.isInteger(quantity) || quantity < 1 || quantity > 20)
      throw new Error('A bag line needs a known item and a quantity from 1 to 20.');
    cents += Math.round(result.item.price * 100) * quantity;
  }
  return Math.round(cents * totalMultiplier) / 100;
}
'''.replace("import {readFileSync} from 'node:fs';\n", "")

APP_SOURCE = r'''import {lookup, filterCatalog, bagTotal} from './catalog.mjs';
const {products, features, brand} = JSON.parse(document.getElementById('catalog-contract').textContent);
const bag = new Map();
const money = value => '$' + value.toFixed(2);
const safe = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render() {
  const category = document.getElementById('category-filter')?.value || 'All';
  const query = document.getElementById('search-input')?.value || '';
  const visible = filterCatalog(products, category, query);
  document.getElementById('result-count').textContent = visible.length + ' objects';
  document.getElementById('catalog-grid').innerHTML = visible.map(p => `
    <article class="product">
      <button class="cover" style="--cover:${safe(p.color)}" ${features.includes('item_details') ? `data-details="${p.id}" aria-label="Inspect ${safe(p.name)}"` : 'disabled'}>
        <span class="edition">EDITION ${safe(p.edition)}</span><span class="cover-type">${safe(p.label).replace(/\n/g,'<br>')}</span><span class="cover-footer">${safe(brand.toUpperCase())} OBJECTS</span>
      </button>
      <div class="product-meta"><div><span class="category">${safe(p.category)}</span><h2>${safe(p.name)}</h2></div><strong>${money(p.price)}</strong></div>
      ${features.includes('cart_total') ? `<button class="add-button" data-add="${p.id}">Add to bag <span>+</span></button>` : ''}
    </article>`).join('') || '<p class="empty">No objects match. Try another search.</p>';
  document.querySelectorAll('[data-details]').forEach(b => b.onclick = () => showDetails(Number(b.dataset.details)));
  document.querySelectorAll('[data-add]').forEach(b => b.onclick = () => {
    const id = Number(b.dataset.add);bag.set(id, Math.min(20, (bag.get(id) || 0) + 1));renderBag();
    document.getElementById('message').textContent = lookup(products,id).item.name + ' added to your bag.';
  });
}
function showDetails(id) {
  const panel = document.getElementById('item-details'), result = lookup(products,id);
  if (!panel) return;
  panel.hidden = false;
  panel.innerHTML = result.status === 200 ? `<button class="detail-close" aria-label="Close details">Close</button><h2>${safe(result.item.name)}</h2><p>${safe(result.item.description)}</p><p class="category">${safe(result.item.material)}</p><strong>${money(result.item.price)}</strong>` : `<p>${safe(result.message)}</p>`;
  panel.querySelector('.detail-close')?.addEventListener('click',()=>panel.hidden=true);
  panel.scrollIntoView({block:'nearest',behavior:'smooth'});
}
function renderBag() {
  const panel = document.getElementById('cart-lines');if (!panel) return;
  panel.innerHTML = [...bag].map(([id,quantity]) => {const p = lookup(products,id).item;return `<div class="bag-line"><span>${safe(p.name)}</span><label>Quantity <input type="number" min="1" max="20" value="${quantity}" data-qty="${id}"></label><button data-remove="${id}" aria-label="Remove ${safe(p.name)}">Remove</button></div>`;}).join('') || '<p>Choose an object to start your bag.</p>';
  document.getElementById('bag-count').textContent = [...bag.values()].reduce((a,b)=>a+b,0);
  document.getElementById('bag-total').textContent = money(bagTotal(products,[...bag].map(([id,quantity])=>({id,quantity}))));
  document.querySelectorAll('[data-qty]').forEach(el => el.onchange = () => {
    const value = Number(el.value);if (Number.isInteger(value) && value >= 1 && value <= 20) bag.set(Number(el.dataset.qty),value);renderBag();
  });
  document.querySelectorAll('[data-remove]').forEach(b => b.onclick=()=>{bag.delete(Number(b.dataset.remove));renderBag();});
}
document.getElementById('category-filter')?.addEventListener('change',render);
document.getElementById('search-input')?.addEventListener('input',render);
document.getElementById('bag-toggle')?.addEventListener('click',()=>{const bag=document.getElementById('cart-panel');bag.hidden=!bag.hidden;});
document.getElementById('store-theme')?.addEventListener('click',()=>{document.documentElement.dataset.theme=document.documentElement.dataset.theme==='dark'?'light':'dark';});
render();renderBag();
'''

CSS_SOURCE = '''@font-face{font-family:Northline;src:url('fonts/dm-sans.ttf') format('truetype');font-weight:100 1000;font-display:swap}
:root{color-scheme:light;--bg:#f5f6f8;--text:#202729;--muted:#535e62;--line:#d7dce0;--panel:#fff;--accent:#2b473b}
:root[data-theme=dark]{color-scheme:dark;--bg:#172021;--text:#eff2ed;--muted:#b0bab4;--line:#3b4847;--panel:#202d2b;--accent:#b8d6bd}
*{box-sizing:border-box}body{margin:0;font:14px/1.5 Northline,sans-serif;background:var(--bg);color:var(--text)}button,input,select{font:inherit;color:inherit}button{cursor:pointer}button:disabled{cursor:default}a{color:inherit;text-decoration:none}button:focus-visible,input:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:3px}button{background:transparent;border:0}header{display:flex;align-items:center;justify-content:space-between;padding:20px 6%;border-bottom:1px solid var(--line);gap:12px}.brand{font-weight:700;font-size:23px;letter-spacing:-.035em}header nav{display:flex;gap:16px;align-items:center;font-size:12px}.bag-trigger{border:1px solid var(--line);padding:7px 10px;border-radius:4px}main{padding:30px 6% 22px}.collection-title{display:flex;justify-content:space-between;align-items:end;gap:12px;margin-bottom:25px}h1{font-size:clamp(34px,7vw,62px);line-height:1.05;font-weight:500;letter-spacing:-.04em;margin:0 0 10px}.intro{max-width:300px;color:var(--muted);margin:0}.collection-mark{font-size:11px;color:var(--muted);line-height:1.8;text-align:right}.toolbar{display:flex;align-items:center;gap:10px;border-block:1px solid var(--line);padding:13px 0;margin-bottom:22px}select,input{background:transparent;border:1px solid var(--line);border-radius:4px;padding:7px 8px;min-width:0}input[type=search]{flex:1;width:100px}#result-count{font-size:11px;color:var(--muted);white-space:nowrap;margin-left:auto}.grid{display:grid;grid-template-columns:1fr 1fr;gap:25px 20px}.cover{width:100%;background:var(--cover);color:#25302c;aspect-ratio:1/.96;display:flex;flex-direction:column;text-align:left;padding:18px;justify-content:space-between}.edition,.cover-footer{font-size:8px;letter-spacing:.08em}.cover-type{font-size:clamp(23px,4.9vw,39px);font-weight:650;line-height:.98;letter-spacing:-.04em}.cover:hover .cover-type{transform:translateY(-3px)}.cover-type{transition:transform .25s cubic-bezier(.16,1,.3,1)}.product-meta{display:flex;justify-content:space-between;align-items:center;padding:12px 0 10px;gap:7px}.category{font-size:10px;color:var(--muted)}h2{margin:2px 0 0;font-size:15px;font-weight:600;letter-spacing:-.02em}.product-meta strong{font-size:13px;font-weight:500}.add-button{padding:8px 0;width:100%;display:flex;justify-content:space-between;font-size:11px;border-top:1px solid var(--line)}.add-button:hover{color:var(--accent)}.add-button span{font-size:17px;line-height:1}#message{min-height:22px;font-size:11px;color:var(--accent);padding-top:8px}.details,.bag{margin:15px 0 25px;padding:19px;background:var(--panel);border:1px solid var(--line)}.details p{color:var(--muted);max-width:55ch}.detail-close{float:right;font-size:11px;text-decoration:underline}.bag h2{margin:0 0 12px}.bag-line{display:flex;gap:10px;align-items:center;padding:12px 0;border-top:1px solid var(--line);font-size:12px}.bag-line label{margin-left:auto;font-size:9px}.bag-line input{width:48px;padding:4px}.bag-line button{font-size:10px}.total{display:flex;justify-content:space-between;border-top:1px solid var(--line);padding-top:15px;font-size:18px}.bag>p{font-size:12px;color:var(--muted)}footer{padding:20px 6%;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:12px;color:var(--muted);font-size:10px}.empty{color:var(--muted)}[hidden]{display:none!important}::selection{background:#b1c5b5;color:#172021}*{scrollbar-width:thin;scrollbar-color:var(--line) transparent}@media(max-width:380px){header nav{gap:8px}.collection-mark{display:none}.toolbar{flex-wrap:wrap}.grid{gap:18px 12px}.cover{padding:14px}.cover-type{font-size:25px}.bag-line{flex-wrap:wrap}}
'''


def module_source(fault="none"):
    return CATALOG_SOURCE.replace("totalMultiplier = 1;", "totalMultiplier = 1.1;") if fault == "wrong_total" else CATALOG_SOURCE


def generate(run, fault="none"):
    products = json.loads((ROOT / "fixtures/catalog.json").read_text(encoding="utf-8"))
    if fault == "leak_cost":
        products[0]["internal_cost"] = 7
    contract = {"products": products, "features": run["features"], "brand": run["brand"]}
    encoded = json.dumps(contract, ensure_ascii=True).replace("<", "\\u003c")
    features = set(run["features"])
    brand = html.escape(run["brand"])
    filter_ui = '<label for="category-filter" hidden>Category</label><select id="category-filter" aria-label="Filter category"><option>All</option><option>Paper</option><option>Objects</option><option>Carry</option></select>' if "category_filter" in features else ''
    search_ui = '<input id="search-input" type="search" placeholder="Search the collection" aria-label="Search the collection">' if "search" in features else ''
    bag_ui = '<button class="bag-trigger" id="bag-toggle">Bag (<span id="bag-count">0</span>)</button>' if "cart_total" in features else ''
    bag_panel = '<section id="cart-panel" class="bag" hidden><h2>Your bag</h2><div id="cart-lines"></div><div class="total"><span>Total</span><strong id="bag-total">$0.00</strong></div><p>Collection preview. No checkout or payment.</p></section>' if "cart_total" in features else ''
    detail_panel = '<section id="item-details" class="details" hidden aria-live="polite"></section>' if "item_details" in features else ''
    page = f'''<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{brand} — Everyday objects</title><link rel="stylesheet" href="style.css"></head><body>
<header><a class="brand" href="#">{brand.lower()}.</a><nav><button id="store-theme" aria-label="Switch storefront theme">Theme</button>{bag_ui}</nav></header>
<main><div class="collection-title"><div><h1>Objects for<br>every day.</h1><p class="intro">Less, but considered. A small collection for the way you live and work.</p></div><span class="collection-mark">THE COLLECTION<br>VOL. 01 / 2026</span></div>
<div class="toolbar">{filter_ui}{search_ui}<span id="result-count">4 objects</span></div>{bag_panel}{detail_panel}<div id="catalog-grid" class="grid"></div><div id="message" aria-live="polite"></div></main>
<footer><span>{brand} / Everyday essentials</span><span>Made to be kept.</span></footer><script type="application/json" id="catalog-contract">{encoded}</script><script type="module" src="app.mjs"></script></body></html>'''
    return {
        "index.html": page,
        "style.css": CSS_SOURCE,
        "catalog.json": json.dumps(contract, indent=2),
        "catalog.mjs": module_source(fault),
        "app.mjs": APP_SOURCE,
        "README.md": f"# {run['brand']} storefront\n\nA generated local collection for browsing, item details and bag arithmetic.\n\nServe this folder with `python -m http.server 8000`, then open http://127.0.0.1:8000.\nRun `node qa.mjs` to execute its checks.\n\n## Brief\n{run['brief']}\n\n## Scope\n" + "\n".join('- '+FEATURES[f]['title'] for f in run['features']) + "\n",
        "qa.mjs": (ROOT / "qa_runner.mjs").read_text(encoding="utf-8"),
        "package.json": json.dumps({"name":"northline-storefront","version":"1.0.0","private":True,"type":"module","scripts":{"test":"node qa.mjs"}}, indent=2),
    }


def preview(files):
    font = base64.b64encode((ROOT / "public/fonts/dm-sans.ttf").read_bytes()).decode()
    html_source = files["index.html"].replace('<link rel="stylesheet" href="style.css">', '<style>'+files['style.css'].replace("url('fonts/dm-sans.ttf')", "url('data:font/ttf;base64,"+font+"')")+'</style>')
    logic = files["catalog.mjs"].replace("export ", "") + files["app.mjs"].replace("import {lookup, filterCatalog, bagTotal} from './catalog.mjs';", "")
    return html_source.replace('<script type="module" src="app.mjs"></script>', '<script type="module">'+logic+'</script>')
