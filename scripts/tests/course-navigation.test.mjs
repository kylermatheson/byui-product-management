import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const root = new URL('../../', import.meta.url);
const weekCode = fs.readFileSync(new URL('_extensions/week-view/week-view.js', root), 'utf8');
const learnCode = fs.readFileSync(new URL('_extensions/learn/learn.js', root), 'utf8');

class Element {
  constructor(tag = 'div') {
    this.tagName = tag.toUpperCase();
    this.dataset = {};
    this.style = {};
    this.attrs = {};
    this.children = [];
    this.handlers = {};
    this.classes = new Set();
    this.classList = {
      add: (...values) => values.forEach(x => this.classes.add(x)),
      remove: (...values) => values.forEach(x => this.classes.delete(x)),
      toggle: (value, on) => on ? this.classes.add(value) : this.classes.delete(value),
    };
  }
  set innerHTML(value) {
    this.html = value;
    this.label = { textContent: value.match(/class="learn-label">([^<]*)/)?.[1] };
    this.note = { textContent: '' };
  }
  get innerHTML() { return this.html || ''; }
  setAttribute(key, value) { this.attrs[key] = value; }
  getAttribute(key) { return this.attrs[key]; }
  appendChild(child) { this.children.push(child); }
  removeChild(child) { this.children.splice(this.children.indexOf(child), 1); }
  addEventListener(event, fn) { this.handlers[event] = fn; }
  select() {}
  querySelector(selector) {
    if (selector === '.learn-label') return this.label;
    if (selector === '.learn-note') return this.note;
    if (selector === '.learn-btn') return this.children.find(x => x.className?.includes('learn-btn'));
    return null;
  }
}

function weeksAt(date, data, search = '', stored = null) {
  const menu = new Element();
  const topics = new Element('ul');
  topics.querySelectorAll = () => ['first', 'second', 'extra'].map(page => ({
    innerHTML: page, getAttribute: () => `./${page}.html`,
  }));
  menu.querySelector = () => topics;
  const nav = new Element('nav');
  nav.innerHTML = 'original topics navigation';
  const controls = ['topics', 'weeks'].map(view => {
    const button = new Element('button'); button.dataset.view = view; return button;
  });
  let ready;
  const document = {
    addEventListener: (_, fn) => { ready = fn; },
    querySelector: selector => ({
      '#quarto-sidebar .sidebar-menu-container': menu,
      'nav.page-navigation': nav,
      '#quarto-sidebar .sidebar-search': { insertAdjacentElement() {} },
    })[selector],
    createElement: tag => {
      const el = new Element(tag);
      el.querySelectorAll = () => controls;
      return el;
    },
    getElementById: () => null,
  };
  const RealDate = Date;
  class FixedDate extends RealDate { constructor() { super(`${date}T12:00:00`); } }
  const context = {
    document, window: { PM_WEEK_VIEW: data }, Date: FixedDate,
    location: { pathname: '/course/first.html', search }, URLSearchParams,
    localStorage: { getItem: () => stored, setItem() {} },
  };
  vm.runInNewContext(weekCode, context);
  ready();
  return { weeks: menu.children[0], topics, nav, controls };
}

const data = {
  'course-end': '2027-04-08', 'course-info': [],
  weeks: [
    { week: 1, date: 'Feb 22–28', start: '2027-02-22', axis: 'Agentic Workflow', read: ['first'] },
    { week: 2, date: 'Mar 1–7', start: '2027-03-01', axis: 'Discovery', read: ['second'] },
    { week: 7, date: 'Apr 5–8', start: '2027-04-05', axis: 'Wrap-up', read: [] },
  ],
};

for (const [date, current] of [
  ['2027-02-21', null], ['2027-02-22', 1], ['2027-02-28', 1],
  ['2027-03-01', 2], ['2027-04-05', 7], ['2027-04-08', 7], ['2027-04-09', null],
]) {
  test(`weekly navigation highlights ${current ?? 'no week'} on ${date}`, () => {
    const { weeks } = weeksAt(date, data);
    assert.equal(weeks.innerHTML.includes('This week'), current !== null);
    if (current !== null) assert.match(weeks.innerHTML, new RegExp(`Week ${current} <span class="wk-now">This week`));
  });
}

test('weekly navigation remains usable with missing dates', () => {
  const undated = structuredClone(data);
  delete undated.weeks[1].start;
  delete undated.weeks[1].date;
  const { weeks, nav } = weeksAt('2027-03-02', undated);
  assert.doesNotMatch(weeks.innerHTML, /This week|undefined/);
  assert.match(weeks.innerHTML, /Dates: ________/);
  assert.match(weeks.innerHTML, /second.html/);
  assert.match(nav.innerHTML, /second.html/);
});

test('Topics preference and explicit Weeks override preserve both navigation orders', () => {
  const topics = weeksAt('2027-03-02', data, '', 'topics');
  assert.equal(topics.weeks.hidden, true);
  assert.equal(topics.nav.innerHTML, 'original topics navigation');
  const weeks = weeksAt('2027-03-02', data, '?view=weeks', 'topics');
  assert.equal(weeks.weeks.hidden, false);
  assert.match(weeks.weeks.innerHTML, /Appendix and references/);
  assert.match(weeks.weeks.innerHTML, /extra.html/);
  assert.match(weeks.nav.innerHTML, /Week 2/);
});

function learning({ secure = true, reject = false, exec = true } = {}) {
  const heading = new Element('h2');
  heading.setAttribute('data-learn', '#real-section');
  const body = new Element('body');
  const copied = [], fallback = [], timers = [];
  const document = {
    readyState: 'complete', body,
    querySelectorAll: () => [heading],
    createElement: tag => new Element(tag),
    execCommand: () => { copied.push(body.children.at(-1).value); return exec; },
  };
  const context = {
    document, URL,
    navigator: { platform: 'MacIntel', clipboard: { writeText: text => {
      copied.push(text); return reject ? Promise.reject(new Error('Denied')) : Promise.resolve();
    } } },
    window: { isSecureContext: secure, prompt: (label, text) => fallback.push({ label, text }) },
    location: { href: 'http://localhost:4200/adaptation/chapter.html?view=weeks#previous' },
    setTimeout: fn => { timers.push(fn); return timers.length; }, clearTimeout() {},
  };
  vm.runInNewContext(learnCode, context);
  return { heading, copied, fallback, body, timers };
}

test('Codex is first, Claude is available, and copied prompts target the active section', async () => {
  const state = learning();
  assert.deepEqual(state.heading.children.map(x => x.dataset.agent), ['Codex', 'Claude']);
  for (const button of state.heading.children) {
    button.handlers.click();
    await Promise.resolve();
    const text = state.copied.at(-1);
    assert.match(text, new RegExp(`using ${button.dataset.agent}`));
    assert.match(text, /http:\/\/localhost:4200\/adaptation\/chapter.html#real-section/);
    assert.doesNotMatch(text, /byu-strategy|refresh-skills|\.claude\/skills|view=weeks/);
    assert.match(text, /cannot access it, ask me to paste/);
    assert.equal(button.label.textContent, 'Copied');
    state.timers.at(-1)();
    assert.equal(button.label.textContent, button.dataset.label);
  }
});

test('non-secure clipboard fallback copies the prompt and removes its temporary field', async () => {
  const state = learning({ secure: false });
  state.heading.children[0].handlers.click();
  await Promise.resolve();
  assert.equal(state.copied.length, 1);
  assert.equal(state.body.children.length, 0);
  assert.equal(state.fallback.length, 0);
});

for (const options of [{ reject: true }, { secure: false, exec: false }]) {
  test(`clipboard failure offers the actual prompt for manual copying: ${JSON.stringify(options)}`, async () => {
    const state = learning(options);
    state.heading.children[1].handlers.click();
    await Promise.resolve();
    assert.equal(state.fallback.length, 1);
    assert.match(state.fallback[0].label, /Claude/);
    assert.match(state.fallback[0].text, /chapter.html#real-section/);
  });
}
