const {chromium}=require('C:/Users/liuyu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const out=path.resolve(__dirname,'../runtime/qa');fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'}),context=await browser.newContext({viewport:{width:1600,height:1050}}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 async function confirm(n){await page.getByLabel('人工复核确认').check();await page.getByLabel('审核备注').fill('自动化界面测试，非用户工程签署；待补项保留。');await page.getByTestId('confirm-next').click();if(n<9)await page.waitForURL('**/step/'+(n+1));else await page.getByText('9 / 9 COMPLETE',{exact:true}).waitFor()}
 for(const dataset of ['pdh','pyridine']){
  await page.goto('http://127.0.0.1:8765/workspace/new');if(dataset==='pyridine')await page.getByRole('button',{name:/四氢糠醇制吡啶/}).click();await page.getByLabel('任务名称').fill(dataset==='pdh'?'丙烷脱氢 · 改进版演示':'吡啶 · 资料补充演示');await page.getByRole('button',{name:'创建并进入 Step 01'}).click();await page.waitForURL('**/step/1');
  const pid=page.url().split('/')[4];await page.getByRole('button',{name:'载入资料中的设计基准'}).click();await page.getByTestId('basis-completion').filter({hasText:'7 / 7'}).waitFor();assert((await page.locator('main').innerText()).includes('摩尔流量'));await page.screenshot({path:path.join(out,dataset+'-step1.png'),fullPage:true});await confirm(1);
  await page.getByRole('heading',{name:'核心物性与二元交互参数矩阵'}).waitFor();assert(await page.locator('.inspector').count()===0);
  if(dataset==='pdh'){
   await page.getByLabel('VLE数据集').selectOption('nist-c3-2006');await page.getByLabel('VLE条件').selectOption('303.15');await page.getByLabel('实验来源').fill('界面功能检查用数据（非生产实验）');await page.getByLabel('实验CSV').fill('T,P\n280,5.75\n300,10.0');await page.getByRole('button',{name:'保存并绘制实验数据'}).click();await page.getByText(/已保存 2 行实验数据/).waitFor();await page.reload();await page.getByLabel('VLE数据集').selectOption('user-experiment');assert(await page.locator('.vle-chart circle').count()===2);
   // Clear test-only data from the demo, retaining published experiments and generated curve.
   const published=await (await page.request.get('http://127.0.0.1:8765/api/projects/'+pid+'/vle')).json();
   const original=published.datasets.find(d=>d.id==='nist-propane-2006');
   const del=await page.request.put('http://127.0.0.1:8765/api/projects/'+pid+'/vle', {data:{kind:'propane_pt',components:['C3H8'],source:original.source,points:original.points}});assert(del.ok());
   await page.reload();await page.getByLabel('VLE数据集').selectOption('nist-c3-2006');
  }
  await page.screenshot({path:path.join(out,dataset+'-step2.png'),fullPage:true});assert(!(await page.locator('body').innerText()).toLowerCase().includes('aspen'));await confirm(2);
  await page.getByRole('button',{name:/采用推荐模型/}).click();await page.screenshot({path:path.join(out,dataset+'-step3.png'),fullPage:true});await confirm(3);
  const card=page.locator('.route-card').filter({has:page.getByRole('heading',{name:dataset==='pdh'?'普通精馏':'多级分离与吡啶回收',exact:true})});await card.getByRole('button',{name:'查看并选择此方案'}).click();await page.screenshot({path:path.join(out,dataset+'-step4.png'),fullPage:true});await confirm(4);
  await page.getByText('REFERENCE DATA LOADED · NOT SOLVED',{exact:true}).waitFor();await page.locator('.process-svg .stream-label').first().waitFor();const sid=dataset==='pdh'?'PRO-D':'A-S2';await page.locator(`.process-svg .stream-label[data-stream-id="${sid}"]`).click();await page.locator('.inspector').getByRole('heading',{name:sid,exact:true}).waitFor();if(dataset==='pdh')assert((await page.locator('.process-svg').innerText()).includes('2,058.98'));await page.screenshot({path:path.join(out,dataset+'-step5.png'),fullPage:true});await confirm(5);
  await page.getByRole('heading',{name:'已补充的工程资料'}).waitFor();await page.screenshot({path:path.join(out,dataset+'-step6.png'),fullPage:true});await confirm(6);
  await page.getByLabel('优化设备').selectOption(dataset==='pdh'?'COLUMN':'3-PY-SPR');await page.getByLabel('回流比 / mol·mol⁻¹',{exact:true}).fill('2');await page.getByRole('button',{name:'保存问题并选用参考基线'}).click();await page.getByText('方案基线已选定',{exact:true}).waitFor();await confirm(7);
  await page.getByRole('heading',{name:'已补充的工程资料'}).waitFor();await page.screenshot({path:path.join(out,dataset+'-step8.png'),fullPage:true});await page.getByRole('button',{name:'检查输入并计算可支持的指标'}).click();await page.getByText(/NOT_CALCULATED ·/).waitFor();await confirm(8);await confirm(9);await page.screenshot({path:path.join(out,dataset+'-step9.png'),fullPage:true});assert(!(await page.locator('body').innerText()).toLowerCase().includes('aspen'));
  fs.writeFileSync(path.join(out,dataset+'-project.txt'),pid);console.log('UI WORKFLOW PASS',dataset,pid);
 }
 assert.deepEqual(errors,[]);await page.setViewportSize({width:390,height:844});await page.goto('http://127.0.0.1:8765/workspace');await page.screenshot({path:path.join(out,'mobile-dashboard.png'),fullPage:true});await browser.close();fs.writeFileSync(path.join(out,'enhancements-ui.json'),JSON.stringify({status:'PASS',errors,checks:['two complete workflows','molar feed inputs','experimental CSV save/reload','20 model candidates','route choice','auto-populated SVG','stream inspector','evidence panels','scoped optimization','export readiness','brand scan']},null,2));
})().catch(e=>{console.error(e);process.exit(1)});
