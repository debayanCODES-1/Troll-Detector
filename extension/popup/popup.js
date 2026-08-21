const defaults = {wordFilter: true, fallacyDetection: true};
const fields = ['wordFilter', 'fallacyDetection'];
const dot = document.getElementById('dot');
const status = document.getElementById('status');

chrome.storage.sync.get(defaults, values => {
  fields.forEach(id => { document.getElementById(id).checked = Boolean(values[id]); });
});

fields.forEach(id => document.getElementById(id).addEventListener('change', event => {
  chrome.storage.sync.set({[id]: event.target.checked});
}));

chrome.runtime.sendMessage({type: 'health'}, response => {
  if (response?.ok) {
    dot.classList.add('ok');
    status.textContent = 'Local server connected';
    return;
  }
  dot.classList.add('error');
  status.textContent = 'Local server unavailable';
});
