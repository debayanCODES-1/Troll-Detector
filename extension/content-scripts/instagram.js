(() => {
  const adapter = {
    getCommentBox: button => button?.closest('form')?.querySelector('textarea') || null,
    getSubmitButton: target => target?.closest('button[type="submit"]') || null,
    getCommentText: box => box?.value || '',
    observeForCommentBox: callback => new MutationObserver(callback).observe(document.body, {subtree: true, childList: true})
  };
  CivilDialog.intercept(adapter);
})();
