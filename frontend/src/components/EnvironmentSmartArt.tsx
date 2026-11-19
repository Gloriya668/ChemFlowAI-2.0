import {Flame,Zap,RefreshCw,Droplets,Factory,ShieldCheck,Leaf} from 'lucide-react';
import './EnvironmentSmartArt.css';
export function EnvironmentSmartArt(){
 const routes=[{title:'普通精馏',icon:Flame,color:'#d7b6ff',flow:'外部供热 → 再沸与冷凝',text:'蒸汽供应与冷却系统决定主要运行环境负担。'}, {title:'热泵精馏',icon:Zap,color:'#00cddd',flow:'蒸气压缩 → 温位提升 → 热量回用',text:'回收冷凝热用于再沸，环境表现与电力来源密切相关。'}, {title:'热耦合精馏',icon:RefreshCw,color:'#66eda5',flow:'精馏段 ⇄ 内部传热 ⇄ 提馏段',text:'减少外部供热与冷却需求，具有运行减排潜力。'}];
 return <div className="env-art compact-art environment-compact" aria-label="环境评价逻辑图">
 <div className="env-art-routes">{routes.map(({title,icon:Icon,color,flow,text})=><article key={title} className="env-art-card" style={{'--accent':color} as React.CSSProperties}><div className="env-art-heading"><Icon size={24}/><h3>{title}</h3></div><div className="env-art-flow">{flow}</div><p>{text}</p></article>)}</div>

 <section className="env-art-account"><h3>运行排放核算</h3><div className="env-art-equation"><div><Zap/><strong>年用电量</strong><span>× 电力排放因子</span></div><b>＋</b><div><Flame/><strong>年蒸汽用量</strong><span>× 蒸汽排放因子</span></div><b>＋</b><div><Droplets/><strong>其他公用工程</strong><span>对应的运行排放</span></div><b>＝</b><div className="env-art-total"><Leaf/><strong>运行碳排放</strong><span>按相同边界汇总</span></div></div><p>电力、蒸汽及循环水因子待确定；费用降幅不等于碳减排率。</p></section>

 <div className="env-art-routes env-art-branches">{[{icon:Droplets,title:'水资源',text:'冷却需求降低可减轻水务负担。',note:'循环水量 ≠ 新鲜水量；节水量需结合补水率、排污率。'},{icon:Factory,title:'设备与材料',text:'计入塔体、换热面及压缩机材料。',note:'新增设备制造排放可能抵消部分运行减排，需按使用寿命核查。'},{icon:ShieldCheck,title:'运行与维护',text:'控制烃类泄漏与无组织排放。',note:'密封监测 → 泄漏检测与修复 → 冷凝液回收及检修废物管理。'}].map(({icon:Icon,title,text,note})=><article className="env-art-card" key={title}><div className="env-art-heading"><Icon size={23}/><h3>{title}</h3></div><strong>{text}</strong><p>{note}</p></article>)}</div>
 <div className="env-art-conclusion"><Leaf size={28}/><div><h3>综合判断：热耦合具有较好的运行环境表现潜力</h3><p>相较热泵，外购供热及包含制冷机的总电输入更低；压缩机自身功率仍较高，需结合能源排放因子综合判断。低碳电力有利于两种强化分离方案。</p><span>当前为定性评价 · 不给出未经核算的减排比例 · 不等同于完整生命周期评价</span></div></div>
 </div>;
}
