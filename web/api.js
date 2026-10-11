export async function api(path, options={}) {
  let response;
  try {response=await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...options.headers}})}
  catch {throw new Error('The Wanderlore server is unreachable. Check your connection and retry. Free hosting may take a minute to wake up.')}
  if(!response.ok){
    if(response.status===401) {const e=new Error('Enter your private access code in Setup to connect this device.');e.pairing=true;throw e}
    const body=await response.json().catch(()=>({detail:'Something went wrong. Please retry.'}));
    throw new Error(typeof body.detail==='string'?body.detail:'Please check the values and try again.')
  }
  return response.json();
}
export const send=(path,body,method='POST')=>api(path,{method,body:JSON.stringify(body)});
export const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
