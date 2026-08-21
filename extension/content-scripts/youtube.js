(() => {
  const adapter = {
    getCommentBox: button => button?.closest('ytd-commentbox')?.querySelector('#contenteditable-root'),
    getSubmitButton: target => target?.closest('#submit-button'),
    getCommentText: box => box?.innerText || '',
    observeForCommentBox: callback => new MutationObserver(callback).observe(document.body, {subtree: true, childList: true})
  };
  CivilDialog.intercept(adapter);
})();
