# Extension

Load this directory with Chrome's **Load unpacked** action. The package includes 16, 48, and 128 pixel SVG icons. X is intentionally limited to reply composers; original posts and direct messages are outside the comment-section scope. Instagram selectors support both textarea and contenteditable composers.

See [tests/README.md](tests/README.md) for the live browser checklist. For a release zip, run `zip -r civildialog-extension.zip extension -x 'extension/tests/*'` and distribute the server/model separately; model artifacts are intentionally not bundled in the extension package.
