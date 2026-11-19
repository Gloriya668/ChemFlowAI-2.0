// Run against the isolated QA server with an explicit model test double.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.CHEMFLOW_TEST_URL||'http://127.0.0.1:8877';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1500,height:1000}});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const created=await page.request.post(base+'/api/projects',{data:{name:'Agent UI TEST DOUBLE',dataset:'pdh',mode:'reference',backend:'reference_replay'}});
  assert.equal(created.status(),200);const p=await created.json();
  await page.goto(base+'/workspace/'+p.id+'/step/1');
  const panel=page.locator('section.panel').filter({has:page.getByRole('heading',{name:'工程 Agent 任务',exact:true})});
  await panel.getByLabel('Agent 任务').fill('检查当前项目（自动测试，不运行真实模型）');
  await panel.getByRole('button',{name:'执行任务',exact:true}).click();
  await panel.getByText('自动测试完成：已检查当前项目；此测试没有调用真实模型或模拟器。',{exact:true}).waitFor({timeout:20000});
  await page.reload();
  await panel.getByText('自动测试完成：已检查当前项目；此测试没有调用真实模型或模拟器。',{exact:true}).waitFor();
  assert.equal(await panel.getByLabel('历史 Agent 任务').locator('option').count(),1);
  const runs=await (await page.request.get(base+'/api/projects/'+p.id+'/agent/runs')).json();
  assert.equal(runs[0].status,'COMPLETED');assert.equal(runs[0].trace[0].tool,'inspect_project');
  await panel.screenshot({path:process.env.CHEMFLOW_SCREENSHOT||'agent-ui.png'});
  assert.deepEqual(errors,[]);console.log('PASS: execute, tool trace, persistence after reload, no browser errors; test double only.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
