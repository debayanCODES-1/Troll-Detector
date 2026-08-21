(() => {
  const composer = node => node?.closest('[role="dialog"], form') || document;
  const adapter = {
    getCommentBox: button => composer(button).querySelector('textarea, [contenteditable="true"][role="textbox"]'),
    getSubmitButton: target => target?.closest('button[type="submit"], button[aria-label="Post"], button[aria-label="Send"]'),
    getCommentText: box => box?.value || box?.innerText || '',
    observeForCommentBox: callback => new MutationObserver(callback).observe(document.body, {subtree: true, childList: true})
  };
  CivilDialog.intercept(adapter);
})();
