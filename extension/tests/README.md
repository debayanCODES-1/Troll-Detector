# Browser Checks

Use Chrome or Chromium with the server running on `127.0.0.1:8787`.

Automated selector checks require Node.js 20 or newer. Run them from this directory with `npm ci` followed by `npm test`. These checks exercise the selector assumptions in isolated DOM fixtures; they do not replace live Chrome testing.

1. Open `chrome://extensions`, enable Developer mode, and load `extension/` unpacked.
2. On YouTube, test a normal comment and a comment containing a blocklisted term.
3. On X, test a reply composer and confirm a new-post composer is never intercepted.
4. On Instagram, test both the textarea and contenteditable composer in a dialog.
5. Confirm the popup reports server connectivity and that disabling either toggle permits that check to pass through.

Platform DOMs are account- and rollout-dependent. Record the Chrome version, URL shape, selector markup, and result when filing a selector update.