
const {chromium}=require('C:/Users/lin8888/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('fs');
(async()=>{const browser=await chromium.launch({headless:true,channel:'msedge'});const page=await browser.newPage({viewport:{width:1280,height:850}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
const response=await page.request.post('http://127.0.0.1:8765/api/projects',{data:{name:'E2E Step01 acceptance',dataset:'pdh',mode:'reference',backend:'reference_replay'}});const p=await response.json();
await page.goto(`http://127.0.0.1:8765/workspace/${p.id}/step/1`);
await page.getByTestId('basis-completion').filter({hasText:'6 / 6 COMPLETE'}).waitFor();
assert.equal(await page.getByLabel('自然语言输入').inputValue(),'');assert(await page.getByTestId('confirm-next').isDisabled());
assert((await page.locator('main').innerText()).includes('Hydrogen / H2'));
await page.getByLabel('FEED 温度 / °C').fill('');await page.getByText(/Cannot continue: 1 required fields missing/).waitFor();await page.getByLabel('人工复核确认').check();assert(await page.getByTestId('confirm-next').isDisabled());
await page.getByLabel('FEED 温度 / °C').fill('57.004380032573');await page.waitForFunction(()=>!document.querySelector('[data-testid="confirm-next"]').disabled);
await page.screenshot({path:'E:/CodexOutputs/ChemFlowAI/runtime/qa/step01-fixed.png',fullPage:true});
let box=await page.getByTestId('confirm-next').boundingBox();assert(box.x>=0&&box.x+box.width<=1280&&box.y+box.height<=850);
await page.getByRole('button',{name:'确认并进入 Step 02',exact:true}).click();await page.waitForURL('**/step/2');await page.reload();await page.getByText('COMPONENT MASTER GRID',{exact:true}).waitFor();assert((await page.getByTestId('nav-step-1').getAttribute('class')).includes('done'));assert(!(await page.getByTestId('nav-step-2').isDisabled()));
await page.screenshot({path:'E:/CodexOutputs/ChemFlowAI/runtime/qa/step02-fixed.png',fullPage:true});
// Existing user project: inspect only, never approve or replace edits.
await page.goto('http://127.0.0.1:8765/workspace/91955520-f306-401b-9486-fe1789dc8a73/step/1');await page.getByTestId('basis-completion').filter({hasText:'6 / 6 COMPLETE'}).waitFor();
await page.setViewportSize({width:700,height:900});await page.getByTestId('confirm-next').waitFor();box=await page.getByTestId('confirm-next').boundingBox();assert(box.x>=0&&box.x+box.width<=700&&box.y+box.height<=900);
assert.deepEqual(errors,[]);fs.writeFileSync('E:/CodexOutputs/ChemFlowAI/runtime/qa/step01-results.json',JSON.stringify({status:'PASS',checks:['prefilled input','6/6 completeness','empty optional parser','required missing blocks approval','CTA within desktop and narrow viewport','continue step2','reload persists completion','existing task preserves edits'],errors},null,2));await browser.close();console.log('Step01 UI acceptance PASS')})().catch(e=>{console.error(e);process.exit(1)});
