const defaults = {wordFilter: true, fallacyDetection: true};
const fields = ['wordFilter', 'fallacyDetection'];
chrome.storage.sync.get(defaults, values => fields.forEach(id => { document.getElementById(id).checked = values[id]; }));
fields.forEach(id => document.getElementById(id).addEventListener('change', event => chrome.storage.sync.set({[id]: event.target.checked})));
chrome.runtime.sendMessage({type: 'health'}, response => {
  const dot = document.getElementById('dot'); const status = document.getElementById('status');
  if (response?.ok) { dot.classList.add('ok'); status.textContent = 'Local server connected'; } else status.textContent = 'Local server unavailable';
});
