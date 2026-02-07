async function fetchOverlaps(){
  const status = document.getElementById('status');
  const results = document.getElementById('results');
  status.textContent = 'Loading...';
  results.innerHTML = '';
  try{
    const res = await fetch('/api/overlaps');
    if(!res.ok){
      const err = await res.json().catch(()=>({message:'unknown'}));
      status.textContent = 'Error: ' + (err.error || res.status);
      return;
    }
    const data = await res.json();
    status.textContent = `Found ${data.pairs_count} pairs`;

    if(!data.pairs_count){
      results.innerHTML = '<div class="pair">No overlapping pairs found.</div>';
      return;
    }

    for(const key of Object.keys(data.pairs)){
      const pair = data.pairs[key];
      const el = document.createElement('div');
      el.className = 'pair';
      const title = document.createElement('h3');
      title.textContent = key.replace(/[()\"]+/g,'');
      el.appendChild(title);

      const pre = document.createElement('pre');
      pre.textContent = JSON.stringify(pair, null, 2);
      el.appendChild(pre);

      results.appendChild(el);
    }
  }catch(e){
    status.textContent = 'Fetch error';
    results.innerHTML = '<div class="pair">'+String(e)+'</div>';
  }
}

document.getElementById('refresh').addEventListener('click', ()=>fetchOverlaps());
// Auto load on first visit
fetchOverlaps();
