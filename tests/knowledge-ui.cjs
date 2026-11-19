const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
const base=process.env.CHEMFLOW_TEST_URL||'http://127.0.0.1:8878';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 try{
  const page=await browser.newPage({viewport:{width:1500,height:1100}});const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  const res=await page.request.post(base+'/api/projects',{data:{name:'知识库 UI 验收',dataset:'pdh',mode:'reference',backend:'reference_replay'}});
  assert.equal(res.status(),200);const p=await res.json();
  await page.goto(base+'/workspace/'+p.id+'/step/1');
  await page.locator('summary').filter({hasText:'工程知识库 ·'}).click();
  await page.getByLabel('知识库查询',{exact:true}).fill('天然气处理');
  await page.getByRole('button',{name:'检索知识库',exact:true}).click();
  await page.getByText('天然气处理 / Natural Gas Processing Unit',{exact:true}).waitFor();
  assert.ok(await page.getByRole('link',{name:'查看原始来源'}).count()>0);
  await page.getByLabel('知识库查询',{exact:true}).fill('zzzzzzzznonexistent');
  await page.getByRole('button',{name:'检索知识库',exact:true}).click();
  await page.getByText('没有找到相关资料，请换用具体的组分、设备或流程名称。',{exact:true}).waitFor();
  await page.getByLabel('知识库查询',{exact:true}).fill('天然气处理');
  await page.getByRole('button',{name:'检索知识库',exact:true}).click();
  await page.getByText('天然气处理 / Natural Gas Processing Unit',{exact:true}).waitFor();
  await page.locator('section.panel').filter({has:page.getByRole('heading',{name:'工程 Agent 任务',exact:true})}).screenshot({path:process.env.CHEMFLOW_SCREENSHOT||'knowledge-ui.png'});
  assert.deepEqual(errors,[]);console.log('PASS: Chinese knowledge search, source links, no-match state, no browser errors. No LLM or simulator called.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
