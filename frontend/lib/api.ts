const API=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
export function token(){return typeof window==="undefined"?null:localStorage.getItem("verilex-token")}
export async function api(path:string,opts:RequestInit={}){
 const headers=new Headers(opts.headers);const t=token();if(t)headers.set("Authorization",`Bearer ${t}`);
 if(opts.body&&!(opts.body instanceof FormData))headers.set("Content-Type","application/json");
 const res=await fetch(API+path,{...opts,headers});const data=await res.json().catch(()=>({detail:"Invalid server response"}));
 if(!res.ok)throw new Error(data.detail||`Request failed: ${res.status}`);return data;
}
export async function authenticate(path:string,payload:object){const d=await api(path,{method:"POST",body:JSON.stringify(payload)});localStorage.setItem("verilex-token",d.access_token);return d.user}
