(() => {
  const adapter = {
    getCommentBox: button => {
      const container = button?.closest('[role="dialog"], form, [data-testid="toolBar"]') || document;
      const box = container.querySelector('[data-testid^="tweetTextarea"]');
      return box && /replying to/i.test(container.innerText || '') ? box : null;
    },
    getSubmitButton: target => target?.closest('[data-testid$="tweetButtonInline"], [data-testid$="tweetButton"]'),
    getCommentText: box => box?.value || box?.innerText || '',
    observeForCommentBox: callback => new MutationObserver(callback).observe(document.body, {subtree: true, childList: true})
  };
  CivilDialog.intercept(adapter);
})();
