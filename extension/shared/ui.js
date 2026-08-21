const CivilDialogUI = (() => {
  function show(box, message, terms) {
    remove(box);
    const panel = document.createElement('aside');
    panel.className = 'civildialog-warning';
    panel.style.cssText = 'position:absolute;z-index:2147483647;max-width:360px;padding:14px 16px;background:rgba(255,249,235,.86);border:1px solid rgba(213,154,66,.7);border-radius:14px;color:#2d2417;font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;box-shadow:0 12px 32px rgba(44,35,20,.2),inset 0 1px rgba(255,255,255,.8);backdrop-filter:blur(14px);';
    panel.textContent = message + (terms.length ? ` Matched: ${terms.join(', ')}.` : '');
    const dismiss = document.createElement('button'); dismiss.textContent = 'Dismiss'; dismiss.style.cssText = 'display:block;margin-top:8px;'; dismiss.onclick = () => panel.remove();
    panel.append(dismiss); document.body.append(panel);
    const rect = box.getBoundingClientRect(); panel.style.left = `${rect.left + window.scrollX}px`; panel.style.top = `${rect.bottom + window.scrollY + 6}px`;
  }
  function showWordFilter(box, terms) { show(box, 'This comment contains blocked language. Please revise.', terms); }
  function showFallacy(box, data) { show(box, `This looks like a personal attack rather than a response to the argument. ${data.explanation} Suggested rewrite: “${data.suggested_rewrite}”`, []); }
  function remove(box) { box.parentElement?.querySelector('.civildialog-warning')?.remove(); }
  return {show, showWordFilter, showFallacy};
})();
