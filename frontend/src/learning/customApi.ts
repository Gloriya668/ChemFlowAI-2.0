import {useEffect,useState} from 'react';
import type {LearningCase} from './types';
export async function learningRequest<T>(url:string,options?:RequestInit):Promise<T>{
 const response=await fetch(url,{...options,headers:{'Content-Type':'application/json',...options?.headers}});
 if(!response.ok){let message='请求失败，请稍后重试。';try{const body=await response.json();message=typeof body.detail==='string'?body.detail:Array.isArray(body.detail)?body.detail.map((e:{msg:string})=>e.msg).join('；'):message}catch{}throw new Error(message)}
 return response.json();
}
export function useCustomCases(){const [cases,setCases]=useState<LearningCase[]>([]),[error,setError]=useState(''),[loading,setLoading]=useState(true);useEffect(()=>{let active=true;learningRequest<LearningCase[]>('/api/learning/custom').then(data=>{if(active)setCases(data)}).catch(e=>{if(active)setError(e.message)}).finally(()=>{if(active)setLoading(false)});return()=>{active=false}},[]);return {cases,error,loading}}
