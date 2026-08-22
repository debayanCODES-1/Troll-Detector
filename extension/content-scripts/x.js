(() => {
  const isReply = container => /replying to|reply to/i.test(container?.innerText || '') || Boolean(container?.querySelector('[data-testid="replyingTo"]'));
  const adapter = {
    getCommentBox: button => {
      const container = button?.closest('[data-testid="toolBar"], [role="dialog"], form');
      if (!container) return null;
      const box = container.querySelector('[data-testid^="tweetTextarea"], [contenteditable="true"][role="textbox"]');
      return box && isReply(container) ? box : null;
    },
    getSubmitButton: target => target?.closest('[data-testid$="tweetButtonInline"], [data-testid$="tweetButton"]'),
    getCommentText: box => box?.value || box?.innerText || '',
    observeForCommentBox: callback => new MutationObserver(callback).observe(document.body, {subtree: true, childList: true})
  };
  TrollGate.intercept(adapter);
})();
