import { test, expect } from '@playwright/test';

test('YouTube comment composer is discoverable', async ({ page }) => {
  await page.setContent('<ytd-commentbox><div id="contenteditable-root" contenteditable="true"></div><button id="submit-button">Comment</button></ytd-commentbox>');
  await expect(page.locator('ytd-commentbox #contenteditable-root')).toBeVisible();
  await expect(page.locator('#submit-button')).toBeVisible();
});

test('X only treats reply composers as comment targets', async ({ page }) => {
  await page.setContent('<div id="reply" data-testid="toolBar"><span>Replying to @user</span><div data-testid="tweetTextarea_0" contenteditable="true"></div></div><div id="post" data-testid="toolBar"><div data-testid="tweetTextarea_1" contenteditable="true"></div></div>');
  const result = await page.evaluate(() => [...document.querySelectorAll('[data-testid="toolBar"]')].map(container => ({
    hasBox: Boolean(container.querySelector('[data-testid^="tweetTextarea"], [contenteditable="true"][role="textbox"], [data-testid^="tweetTextarea"]')),
    isReply: /replying to|reply to/i.test(container.innerText || '') || Boolean(container.querySelector('[data-testid="replyingTo"]'))
  })));
  expect(result).toEqual([{hasBox: true, isReply: true}, {hasBox: true, isReply: false}]);
});

test('Instagram supports textarea and contenteditable composers', async ({ page }) => {
  await page.setContent('<form><textarea></textarea><button type="submit">Post</button></form><div role="dialog"><div contenteditable="true" role="textbox"></div><button aria-label="Send">Send</button></div>');
  await expect(page.locator('textarea, [contenteditable="true"][role="textbox"]')).toHaveCount(2);
  await expect(page.locator('button[type="submit"], button[aria-label="Post"], button[aria-label="Send"]')).toHaveCount(2);
});