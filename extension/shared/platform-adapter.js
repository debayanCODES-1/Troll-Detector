const TrollGate = (() => {
  const defaults = {wordFilter: true, fallacyDetection: true};

  function settings() {
    return new Promise(resolve => chrome.storage.sync.get(defaults, resolve));
  }

  function request(type, text) {
    return new Promise(resolve => chrome.runtime.sendMessage({type, text}, response => resolve(response || {ok: false, error: 'No response'})));
  }

  function intercept(adapter) {
    let busy = false;
    document.addEventListener('click', async event => {
      const button = adapter.getSubmitButton(event.target);
      if (!button || busy) return;
      const box = adapter.getCommentBox(button);
      if (!box) return;
      const text = adapter.getCommentText(box).trim();
      if (!text) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      busy = true;
      try {
        const prefs = await settings();
        if (prefs.wordFilter) {
          const result = await request('wordfilter', text);
          if (!result.ok) { TrollGateUI.show(box, 'The local TROLL GATE server is unavailable. Comment was not posted.', []); return; }
          if (result.data.flagged) { TrollGateUI.showWordFilter(box, result.data.matched_terms); return; }
        }
        if (prefs.fallacyDetection) {
          const result = await request('fallacy', text);
          if (!result.ok) { TrollGateUI.show(box, 'The local TROLL GATE server is unavailable. Comment was not posted.', []); return; }
          if (result.data.flagged) {
            const explanation = await request('explain', text);
            const data = explanation.ok ? explanation.data : {explanation: 'This wording appears to target a person.', suggested_rewrite: ''};
            TrollGateUI.showFallacy(box, data);
            return;
          }
        }
        button.click();
      } finally { busy = false; }
    }, true);
    adapter.observeForCommentBox(() => {});
  }

  return {intercept};
})();
