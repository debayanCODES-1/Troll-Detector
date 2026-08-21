const API = 'http://127.0.0.1:8787';

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (!['wordfilter', 'fallacy', 'explain', 'health'].includes(message.type)) return;
  const path = message.type === 'health' ? '/health' : `/check/${message.type}`;
  const endpoint = message.type === 'explain' ? '/explain' : path;
  fetch(API + endpoint, {
    method: message.type === 'health' ? 'GET' : 'POST',
    headers: {'Content-Type': 'application/json'},
    body: message.type === 'health' ? undefined : JSON.stringify({text: message.text})
  }).then(async response => {
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    return response.json();
  }).then(data => sendResponse({ok: true, data})).catch(error => sendResponse({ok: false, error: error.message}));
  return true;
});
