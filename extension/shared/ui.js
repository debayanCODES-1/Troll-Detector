const CivilDialogUI = (() => {
  function show(box, message, terms) {
    remove(box);
    const panel = document.createElement('aside');
    panel.className = 'civildialog-warning';
    panel.style.cssText = 'position:absolute;z-index:2147483647;max-width:360px;padding:12px;background:#fff8e6;border:1px solid #d89b2b;border-radius:6px;color:#2d2417;font:14px/1.4 sans-serif;box-shadow:0 3px 12px #0003;';
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
