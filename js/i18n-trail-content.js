(() => {
    'use strict';
    const PAGE = {
        '/trilha.html': 'clf', '/trilha-dea.html': 'dea', '/trilha-dva.html': 'dva', '/trilha-saa.html': 'saa',
        '/en/trilha.html': 'clf', '/en/trilha-dea.html': 'dea', '/en/trilha-dva.html': 'dva', '/en/trilha-saa.html': 'saa',
    };
    const trail = PAGE[location.pathname] || (location.pathname.endsWith('/trilha.html') ? 'clf' : null);
    if (!trail) return;
    const SKIP = new Set(['SCRIPT','STYLE','NOSCRIPT','PRE','CODE','SVG']);
    let catalogs=null, observer=null, applying=false;
    const locale=()=>String(window.I18n?.locale||document.documentElement.lang||'pt-BR').toLowerCase().startsWith('en')?'en':'pt-BR';
    const url=(l)=>`/locales/${l}/trail-${trail}-literals.json`;
    async function load(){
        if(catalogs)return catalogs;
        const [pr,er]=await Promise.all([fetch(url('pt-BR'),{cache:'no-cache'}),fetch(url('en'),{cache:'no-cache'})]);
        if(!pr.ok||!er.ok)throw new Error(`trail catalogs unavailable ${trail}: PT=${pr.status} EN=${er.status}`);
        const [p,e]=await Promise.all([pr.json(),er.json()]);const pt=p.trailLiterals||{},en=e.trailLiterals||{};
        const pk=Object.keys(pt).sort(),ek=Object.keys(en).sort();if(pk.length!==ek.length||pk.some((k,i)=>k!==ek[i]))throw new Error(`trail catalog parity mismatch: ${trail}`);
        catalogs={'pt-BR':pt,en};return catalogs;
    }
    function mapping(target){const src=target==='en'?'pt-BR':'en',m=new Map();for(const k of Object.keys(catalogs[src])){const a=String(catalogs[src][k]||'').trim(),b=String(catalogs[target][k]||'').trim();if(a&&b&&a!==b)m.set(a,b);}return m;}
    function preserve(original,replacement){return `${original.match(/^\s*/)?.[0]||''}${replacement}${original.match(/\s*$/)?.[0]||''}`;}
    function translate(v,m){if(typeof v!=='string'||!v.trim())return v;const x=m.get(v.trim());return x?preserve(v,x):v;}
    function applyNode(root,m){
        if(!root)return;
        if(root.nodeType===Node.TEXT_NODE){const p=root.parentElement;if(!p||SKIP.has(p.tagName))return;const n=translate(root.nodeValue,m);if(n!==root.nodeValue)root.nodeValue=n;return;}
        if(root!==document&&root.nodeType!==Node.ELEMENT_NODE)return;if(root.nodeType===Node.ELEMENT_NODE&&SKIP.has(root.tagName))return;
        const attrs=(el)=>{for(const a of ['aria-label','title','placeholder','alt'])if(el.hasAttribute?.(a)){const c=el.getAttribute(a),n=translate(c,m);if(n!==c)el.setAttribute(a,n);}};
        if(root.nodeType===Node.ELEMENT_NODE)attrs(root);
        const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode(node){let p=node.parentElement;while(p&&p!==document.body){if(SKIP.has(p.tagName))return NodeFilter.FILTER_REJECT;p=p.parentElement;}return NodeFilter.FILTER_ACCEPT;}});let n;while((n=w.nextNode()))applyNode(n,m);
        for(const el of root.querySelectorAll?.('[aria-label],[title],[placeholder],[alt]')||[])attrs(el);
    }
    async function apply(root=document){if(applying)return;applying=true;try{await load();const l=locale();document.documentElement.dataset.trailLocale=l;applyNode(root,mapping(l));}catch(e){console.error('[Trail i18n]',e);}finally{applying=false;}}
    function observe(){if(observer||!document.body)return;observer=new MutationObserver(ms=>{if(applying)return;for(const m of ms)for(const n of m.addedNodes||[])apply(n);});observer.observe(document.body,{subtree:true,childList:true});}
    document.addEventListener('cloudpath:i18nready',()=>apply(document));document.addEventListener('cloudpath:localechange',()=>apply(document));
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{apply(document);observe();},{once:true});else{apply(document);observe();}
})();
