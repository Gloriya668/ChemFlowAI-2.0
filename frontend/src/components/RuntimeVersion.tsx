import {useEffect,useState} from 'react';
import {api} from '../api';
import {Badge} from './ui';
export function RuntimeVersion(){
 const [build,setBuild]=useState('检测运行版本…');
 useEffect(()=>{api('/health').then(r=>setBuild(r.build||'旧版服务，请检查启动目录')).catch(()=>setBuild('服务不可达'));},[]);
 return <Badge tone="cyan">服务版本 · {build}</Badge>;
}
