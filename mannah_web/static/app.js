(()=>{
  const themes=['linen','midnight','forest','ocean','berry','citrus','lavender','sand','slate','rose','mint','contrast'];
  let current='midnight';
  try{current=localStorage.getItem('mannah-theme')||'midnight'}catch(e){}
  if(!themes.includes(current))current='midnight';
  const apply=(theme,animate=false)=>{
    current=themes.includes(theme)?theme:'midnight';
    if(animate){document.documentElement.classList.add('theme-changing');setTimeout(()=>document.documentElement.classList.remove('theme-changing'),460)}
    document.documentElement.dataset.theme=current;
    document.querySelectorAll('[data-theme]').forEach(b=>b.classList.toggle('active',b.dataset.theme===current));
    try{localStorage.setItem('mannah-theme',current)}catch(e){}
  };
  apply(current);
  document.querySelectorAll('[data-theme]').forEach(b=>b.addEventListener('click',()=>apply(b.dataset.theme,true)));
  const sheet=document.querySelector('#theme-sheet');
  const open=()=>{if(!sheet)return;sheet.classList.add('open');sheet.setAttribute('aria-hidden','false')};
  const close=()=>{if(!sheet)return;sheet.classList.remove('open');sheet.setAttribute('aria-hidden','true')};
  document.querySelectorAll('[data-theme-open]').forEach(b=>b.addEventListener('click',open));
  document.querySelectorAll('[data-theme-close]').forEach(b=>b.addEventListener('click',close));
  document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});
  document.querySelectorAll('[data-public-theme]').forEach(b=>b.addEventListener('click',()=>apply(themes[(themes.indexOf(current)+1)%themes.length],true)));
})();

(()=>{
  document.querySelectorAll('.flash button').forEach(b=>b.addEventListener('click',()=>{const f=b.closest('.flash');if(!f)return;f.classList.add('is-leaving');setTimeout(()=>f.remove(),260)}));
  document.querySelectorAll('[data-nutrient-tabs] button').forEach(btn=>btn.addEventListener('click',()=>{
    const wrap=btn.closest('[data-nutrient-tabs]');
    wrap.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===btn));
    const group=btn.dataset.group;
    document.querySelectorAll('.nutrient-line[data-group]').forEach(row=>row.hidden=!(group==='all'||row.dataset.group===group));
  }));
  document.querySelectorAll('[data-finder-tabs] button').forEach(btn=>btn.addEventListener('click',()=>{
    const tabs=btn.closest('[data-finder-tabs]');
    tabs.querySelectorAll('button').forEach(x=>x.classList.toggle('active',x===btn));
    document.querySelectorAll('.finder-pane').forEach(p=>p.classList.toggle('active',p.dataset.pane===btn.dataset.tab));
  }));
})();

(()=>{
  const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduce)return;
  document.querySelectorAll('.energy-ring').forEach(r=>{
    const target=getComputedStyle(r).getPropertyValue('--p').trim()||r.style.getPropertyValue('--p')||'0%';
    r.style.setProperty('--p','0%');
    requestAnimationFrame(()=>requestAnimationFrame(()=>r.style.setProperty('--p',target)));
  });
  document.querySelectorAll('.line-meter i').forEach((bar,i)=>{
    bar.classList.add('motion-meter');
    bar.style.animationDelay=`${Math.min(i*24,240)}ms`;
  });
})();

(()=>{
  const h=document.querySelector('#height-cm'),w=document.querySelector('#weight-kg');
  const ho=document.querySelector('#height-us'),wo=document.querySelector('#weight-us');
  if(h&&ho){
    const update=()=>{const cm=Number(h.value)||0;if(!cm){ho.textContent='— ft — in';return}const total=cm/2.54;const ft=Math.floor(total/12);const inch=Math.round((total-ft*12)*10)/10;ho.textContent=`${ft} ft ${inch} in`};
    h.addEventListener('input',update);update();
  }
  if(w&&wo){
    const update=()=>{const kg=Number(w.value)||0;wo.textContent=kg?`${(kg*2.2046226218).toFixed(1)} lb`:'— lb'};
    w.addEventListener('input',update);update();
  }
})();

(()=>{
  if(!window.MannahLogger)return;
  const q=document.querySelector('#food-search'),results=document.querySelector('#search-results');
  const clear=document.querySelector('#clear-search'),globalBtn=document.querySelector('#global-search');
  const form=document.querySelector('#log-form'),placeholder=document.querySelector('#food-placeholder');
  const grams=document.querySelector('#grams'),save=document.querySelector('#save-food'),ounce=document.querySelector('#ounce-readout');
  const favBtn=document.querySelector('#favorite-food');
  let current=null,timer=null,seq=0;
  const esc=s=>String(s??'').replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]||c));
  const fmt=(n,d=1)=>Number(n||0).toLocaleString(undefined,{maximumFractionDigits:d,minimumFractionDigits:d});
  const empty=(title='Start with a food name',sub='Your local Pot of Mannah database is searched first.')=>{results.innerHTML=`<div class="search-empty"><span>⌕</span><b>${esc(title)}</b><p>${esc(sub)}</p></div>`};
  const loading=(text='Searching foods…')=>{results.innerHTML=`<div class="search-empty"><span>•••</span><b>${esc(text)}</b><p>Nutrition values are normalized per 100 g.</p></div>`};
  const render=items=>{
    if(!items.length){empty('No matching foods','Try a shorter name or use the global search.');return}
    results.innerHTML=items.map((f,i)=>`<button type="button" class="food-result" data-i="${i}"><span class="food-result-main"><b>${esc(f.name)}</b><span>${esc(f.category||'Food')} · ${esc(f.source)}</span></span><span class="food-result-macros"><b>${fmt(f.calories,0)} kcal</b><span>${fmt(f.protein)}g P</span><span>${fmt(f.carbs)}g C</span></span></button>`).join('');
    results.querySelectorAll('.food-result').forEach(b=>b.addEventListener('click',()=>choose(items[Number(b.dataset.i)])));
  };
  async function search(global=false){
    const query=q.value.trim();if(query.length<1){empty();return}
    const my=++seq;loading(global?'Searching USDA and packaged foods…':'Searching Pot of Mannah…');
    try{const r=await fetch(`${global?'/api/global-foods':'/api/search-foods'}?q=${encodeURIComponent(query)}&limit=35`);const data=await r.json();if(my===seq)render(data.results||[])}
    catch(e){if(my===seq)empty('Search unavailable',global?'The online databases could not be reached. Local foods still work.':'Please try again.')}
  }
  async function choose(food){if(food.source_key==='usda'||food.source_key==='off')return importRemote(food);show(food)}
  async function importRemote(food){
    loading('Saving this food to your library…');
    try{const r=await fetch('/api/import-food',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(food)});const data=await r.json();if(!r.ok)throw new Error();show(data.food)}
    catch(e){empty('Could not import that food','Try another search result.')}
  }
  function update(){
    if(!current)return;const g=Math.max(0,Number(grams.value)||0),factor=g/100;
    const kcal=Number(current.calories||0)*factor,protein=Number(current.protein||0)*factor,carbs=Number(current.carbs||0)*factor,fat=Number(current.fat||0)*factor;
    document.querySelector('#portion-kcal').textContent=fmt(kcal,0);
    document.querySelector('#portion-protein').textContent=`${fmt(protein)}g protein`;
    document.querySelector('#portion-carbs').textContent=`${fmt(carbs)}g carbs`;
    document.querySelector('#portion-fat').textContent=`${fmt(fat)}g fat`;
    document.querySelector('#math-line').textContent=g>0?`${fmt(current.calories,0)} kcal / 100 g × ${fmt(g,1)} g ÷ 100 = ${fmt(kcal,0)} kcal`:'Nutrition per 100 g × grams ÷ 100';
    if(ounce)ounce.textContent=`${fmt(g/28.349523125,2)} oz`;save.disabled=!(g>0);
  }
  async function refreshFavorite(){
    if(!current||!favBtn)return;
    try{const r=await fetch(`/api/favorite-state?source_key=${encodeURIComponent(current.source_key)}&source_id=${encodeURIComponent(current.source_id)}`);const data=await r.json();favBtn.classList.toggle('active',!!data.active);favBtn.textContent=data.active?'★':'☆'}catch(e){favBtn.textContent='☆'}
  }
  function show(food){
    current=food;placeholder.classList.add('hidden');form.classList.remove('hidden');
    document.querySelector('#source-key').value=food.source_key;document.querySelector('#source-id').value=food.source_id;
    document.querySelector('#food-source').textContent=food.source;document.querySelector('#food-name').textContent=food.name;
    document.querySelector('#food-category').textContent=`${food.category||'Food'}${food.serving?' · '+food.serving:''}`;
    ['calories','protein','carbs','fat'].forEach(k=>document.querySelector('#n-'+k).textContent=fmt(food[k],k==='calories'?0:1));
    grams.value='';save.disabled=true;update();refreshFavorite();
    if(window.matchMedia('(max-width:1180px)').matches)document.querySelector('#log-pane')?.scrollIntoView({behavior:'smooth',block:'start'});else grams.focus();
  }
  q?.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(()=>search(false),220)});
  q?.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();search(false)}});
  clear?.addEventListener('click',()=>{q.value='';seq++;empty();q.focus()});
  globalBtn?.addEventListener('click',()=>search(true));
  grams?.addEventListener('input',update);
  document.querySelectorAll('[data-g]').forEach(b=>b.addEventListener('click',()=>{grams.value=Number(b.dataset.g).toFixed(Number(b.dataset.g)%1?1:0);update();grams.focus()}));
  document.querySelectorAll('.library-food[data-food]').forEach(b=>b.addEventListener('click',()=>{try{show(JSON.parse(b.dataset.food))}catch(e){}}));
  favBtn?.addEventListener('click',async()=>{if(!current)return;favBtn.disabled=true;try{const r=await fetch('/api/favorite',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source_key:current.source_key,source_id:current.source_id})});const data=await r.json();if(r.ok){favBtn.classList.toggle('active',!!data.active);favBtn.textContent=data.active?'★':'☆'}}finally{favBtn.disabled=false}});
  const pick=new URLSearchParams(location.search).get('pick');
  if(pick&&pick.includes(':')){const [sourceKey,...rest]=pick.split(':');const sourceId=rest.join(':');fetch(`/api/food/${encodeURIComponent(sourceKey)}/${encodeURIComponent(sourceId)}`).then(r=>r.json()).then(d=>{if(d.food)show(d.food)}).catch(()=>{})}
})();

// v9 motion + progressive disclosure
(()=>{
  const reduce=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const reveals=[...document.querySelectorAll('.reveal')];
  if(reduce){reveals.forEach(el=>el.classList.add('in-view'));return}
  if('IntersectionObserver' in window){
    const io=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('in-view');io.unobserve(entry.target)}}),{threshold:.08,rootMargin:'0px 0px -30px'});
    reveals.forEach(el=>io.observe(el));
  }else reveals.forEach(el=>el.classList.add('in-view'));

  document.querySelectorAll('[data-count]').forEach(el=>{
    const end=Number(el.dataset.count||el.textContent)||0;
    const decimals=String(end).includes('.')?1:0;
    let start=null;const duration=850;
    const step=t=>{if(start===null)start=t;const p=Math.min((t-start)/duration,1);const eased=1-Math.pow(1-p,3);el.textContent=(end*eased).toFixed(decimals);if(p<1)requestAnimationFrame(step)};
    requestAnimationFrame(step);
  });

  document.querySelectorAll('.btn,.log-cta,.round-btn,.theme-card,.mobile-tabs a,.planner-food>a').forEach(el=>el.addEventListener('pointerdown',e=>{
    if(reduce)return;const r=document.createElement('span');r.className='ripple-dot';const box=el.getBoundingClientRect();r.style.left=`${e.clientX-box.left}px`;r.style.top=`${e.clientY-box.top}px`;el.appendChild(r);setTimeout(()=>r.remove(),700)
  }));

  document.querySelectorAll('[data-tilt]').forEach(el=>{
    el.addEventListener('pointermove',e=>{if(reduce||window.innerWidth<900)return;const b=el.getBoundingClientRect();const x=(e.clientX-b.left)/b.width-.5;const y=(e.clientY-b.top)/b.height-.5;el.style.transform=`perspective(1000px) rotateX(${-y*2.2}deg) rotateY(${x*2.2}deg) translateY(-2px)`});
    el.addEventListener('pointerleave',()=>el.style.transform='');
  });
})();

// v10: generic in-page tab sets with URL hash support
(()=>{
  const sets=[...document.querySelectorAll('[data-tabset]')];
  if(!sets.length)return;
  const safeHash=()=>{try{return decodeURIComponent(location.hash.slice(1))}catch(e){return ''}};
  sets.forEach(tabset=>{
    const buttons=[...tabset.querySelectorAll('[data-tab-target]')];
    const shell=tabset.parentElement;
    const panels=[...shell.querySelectorAll(':scope > [data-tab-panel]')];
    if(!buttons.length||!panels.length)return;
    const valid=new Set(buttons.map(b=>b.dataset.tabTarget));
    const key=tabset.dataset.tabsetKey||'tabs';
    const activate=(name,writeHash=true)=>{
      if(!valid.has(name))name=buttons[0].dataset.tabTarget;
      buttons.forEach(b=>{const on=b.dataset.tabTarget===name;b.classList.toggle('active',on);b.setAttribute('aria-selected',on?'true':'false')});
      panels.forEach(p=>p.classList.toggle('active',p.dataset.tabPanel===name));
      try{sessionStorage.setItem(`mannah-tab-${key}`,name)}catch(e){}
      if(writeHash&&history.replaceState)history.replaceState(null,'',`${location.pathname}${location.search}#${name}`);
    };
    buttons.forEach(b=>b.addEventListener('click',()=>activate(b.dataset.tabTarget)));
    shell.querySelectorAll('[data-open-tab]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();activate(a.dataset.openTab);tabset.scrollIntoView({behavior:'smooth',block:'start'})}));
    let initial=safeHash();
    if(!valid.has(initial)){try{initial=sessionStorage.getItem(`mannah-tab-${key}`)||''}catch(e){initial=''}}
    activate(valid.has(initial)?initial:buttons[0].dataset.tabTarget,false);
  });
})();
