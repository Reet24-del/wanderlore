const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

// Exercise the actual scheduler with a controlled clock and media state.
// Chapter generation is the external boundary; record when it is requested.
const source = fs.readFileSync(path.join(__dirname, '../web/app.js'), 'utf8');
const scheduler = source.slice(source.indexOf('function schedule(){'), source.indexOf('async function next('));
function harness() {
  const timers = new Map(), advances = [];
  let serial = 0;
  const state = {
    auto: true, busy: false, autoTimer: null,
    walk: {status: 'active', beats: [{final: false, choices: [{id: 'ask'}]}]},
    audio: {src: '/audio/chapter.wav', ended: true, paused: true},
    currentAudio: '/audio/chapter.wav', document: {hidden: false},
    setTimeout(fn, delay) {const id = ++serial; timers.set(id, {fn, delay}); return id;},
    clearTimeout(id) {timers.delete(id);},
    next(automatic) {advances.push(automatic); return Promise.resolve();},
    report(error) {throw error;},
  };
  state.stopTimer = () => state.clearTimeout(state.autoTimer);
  vm.createContext(state);
  vm.runInContext(scheduler, state);
  return {state, timers, advances, tick() {
    const [id, timer] = timers.entries().next().value;
    timers.delete(id); timer.fn();
  }};
}

test('offered choices do not prevent automatic chapter generation', () => {
  const h = harness(); h.state.schedule();
  assert.equal(h.timers.size, 1, 'automatic mode should queue the next chapter without a choice');
  assert.ok([...h.timers.values()][0].delay <= 15000, 'the quiet pause should be short');
  h.tick(); assert.deepEqual(h.advances, [true]);
});
test('automatic continuation does not cut off narration', () => {
  const h = harness(); h.state.audio.ended = false; h.state.audio.paused = false;
  h.state.walk.beats[0].choices = [];
  h.state.schedule();
  if (h.timers.size) h.tick();
  assert.deepEqual(h.advances, []);
  h.state.audio.ended = true; h.state.audio.paused = true;
  h.state.schedule(); h.tick(); assert.deepEqual(h.advances, [true]);
});
test('switching automatic continuation off cancels a pending chapter', () => {
  const h = harness(); h.state.walk.beats[0].choices = []; h.state.schedule();
  assert.equal(h.timers.size, 1);
  h.state.auto = false; h.state.schedule();
  assert.equal(h.timers.size, 0); assert.deepEqual(h.advances, []);
});
test('paused walks and closing chapters do not schedule another chapter', () => {
  for (const status of ['paused', 'finished']) {
    const h = harness(); h.state.walk.status = status; h.state.schedule();
    assert.equal(h.timers.size, 0);
  }
  const h = harness(); h.state.walk.beats[0].final = true; h.state.schedule();
  assert.equal(h.timers.size, 0);
});
test('a late timer does not advance after the walk is paused', () => {
  const h = harness(); h.state.walk.beats[0].choices = []; h.state.schedule();
  assert.equal(h.timers.size, 1);
  h.state.walk.status = 'paused'; h.tick(); assert.deepEqual(h.advances, []);
});
