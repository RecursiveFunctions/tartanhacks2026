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

    for(const pairObj of data.pairs){
      const el = document.createElement('div');
      el.className = 'pair';
      
      const title = document.createElement('h3');
      title.textContent = `${pairObj.id1} & ${pairObj.id2}`;
      el.appendChild(title);

      const schedule = pairObj.schedule;
      for(const [day, hours] of Object.entries(schedule)){
        const dayEl = document.createElement('p');
        dayEl.innerHTML = `<strong>${day}:</strong> ${hours.join(', ')}`;
        el.appendChild(dayEl);
      }

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
