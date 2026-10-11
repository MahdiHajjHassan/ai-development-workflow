/** Fixed QA entry point. Receives an artifact directory, never a shell command. */
import {readFileSync, existsSync} from 'node:fs';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {fileURLToPath} from 'node:url';
const folder = resolve(process.argv[2] || fileURLToPath(new URL('.', import.meta.url)));
const {products, features} = JSON.parse(readFileSync(join(folder,'catalog.json'),'utf8'));
const {lookup, filterCatalog, bagTotal} = await import(pathToFileURL(join(folder,'catalog.mjs')).href);
const page = readFileSync(join(folder,'index.html'),'utf8');
const app = readFileSync(join(folder,'app.mjs'),'utf8');
const checks=[];
function check(id,title,fn){try{const observed=fn();checks.push({id,title,passed:true,observed});console.log('PASS  '+title+' — '+observed);}catch(error){checks.push({id,title,passed:false,observed:error.message});console.log('FAIL  '+title+' — '+error.message);}}
function assert(condition,message){if(!condition)throw new Error(message);}
check('catalog','Catalog contains four usable objects',()=>{assert(products.length===4 && products.every(p=>p.id&&p.price>0&&p.name),'Expected four priced objects');return products.map(p=>p.name).join(', ');});
check('known-item','Known item resolves to public details',()=>{const result=lookup(products,1);assert(result.status===200&&result.item.name==='Field notes','Item 1 lookup failed');return 'Item 1 → 200 / Field notes';});
check('missing-item','Missing item returns a useful response',()=>{const result=lookup(products,999);assert(result.status===404&&result.message,'Missing ID should be 404');return 'Item 999 → 404';});
check('invalid-id','Invalid identifiers are rejected',()=>{assert(lookup(products,'../private').status===400&&lookup(products,0).status===400,'Invalid ID accepted');return 'String and zero → 400';});
check('public-fields','Supplier costs stay out of public source',()=>{const fields=['internal_cost','supplier_cost','wholesale_price'];assert(!products.some(p=>fields.some(f=>f in p))&&!fields.some(f=>page.includes('"'+f+'"')),'Internal purchasing cost found in public catalog');return 'Restricted fields: none';});
check('source-contract','Browser source and Node source share the contract',()=>{assert(page.includes('catalog-contract')&&app.includes('bagTotal')&&existsSync(join(folder,'style.css')),'Source contract or stylesheet missing');const inline=JSON.parse(page.match(/id="catalog-contract">([\s\S]*?)<\/script>/)[1]);assert(JSON.stringify(inline.products)===JSON.stringify(products),'Inline browser catalog differs from checked JSON');return 'HTML, data, module and stylesheet present';});
if(features.includes('item_details'))check('details','Item details have a real browser hook',()=>{assert(page.includes('id="item-details"')&&app.includes('showDetails'),'Detail hook missing');return 'Detail panel and lookup handler present';});
if(features.includes('category_filter'))check('categories','Filtering returns matching objects',()=>{assert(filterCatalog(products,'Objects').length===2&&filterCatalog(products,'Missing').length===0,'Category results differ');return 'Objects → 2 / Missing → 0';});
if(features.includes('search'))check('search','Search handles mixed case and empty results',()=>{assert(filterCatalog(products,'All','FIELD').length===1&&filterCatalog(products,'All','zzzz').length===0,'Search mismatch');return 'FIELD → Field notes / zzzz → 0';});
if(features.includes('cart_total')){
check('cart-total','Quantities produce the correct bag total',()=>{const actual=bagTotal(products,[{id:1,quantity:2},{id:2,quantity:2}]);assert(actual===84,'Observed $'+actual.toFixed(2)+'; expected $84.00');return '2 × $18 + 2 × $24 = $84.00';});
check('quantity-validation','Bad quantities cannot enter a total',()=>{for(const quantity of [0,21,1.5]){let rejected=false;try{bagTotal(products,[{id:1,quantity}]);}catch{rejected=true;}assert(rejected,'Invalid quantity '+quantity+' accepted');}assert(bagTotal(products,[])===0,'Empty bag should total zero');return '0, 21, fraction rejected / empty bag $0.00';});
}
console.log('\n'+checks.filter(c=>c.passed).length+'/'+checks.length+' checks passed');
console.log('AGENTCREW_REPORT='+JSON.stringify({passed:checks.every(c=>c.passed),checks}));
process.exitCode=checks.every(c=>c.passed)?0:1;
