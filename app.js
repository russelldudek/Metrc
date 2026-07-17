const scenarios = {
  modernization: {
    label: 'Platform modernization',
    state: 'Traceable - protect migration reliability',
    outcome: 'Modernize the platform while preserving regulatory continuity and user confidence.',
    owner: 'CTO + Product, with explicit cross-functional executive sponsorship',
    dependencies: 'Migration sequencing, regulator readiness, support readiness, product adoption',
    clock: 'Escalate when a dependency threatens a committed release or service threshold',
    evidence: 'Performance, defect patterns, adoption, support demand, regulator/licensee feedback',
    learning: 'Convert release evidence into the next portfolio decision and retire redundant reporting',
    brief: 'Keep the modernization program visible as one business outcome, not a collection of technical workstreams.',
    tag: 1
  },
  market: {
    label: 'New-market implementation',
    state: 'Escalate - dependency custody is unclear',
    outcome: 'Launch a market with regulator confidence and licensee readiness.',
    owner: 'Market implementation leader with named executive sponsor',
    dependencies: 'Configuration, data transition, training, communications, partner readiness',
    clock: 'Escalate when launch-critical ownership or evidence is missing',
    evidence: 'Readiness checkpoints, issue closure, training completion, go-live risk disposition',
    learning: 'Capture repeatable rollout patterns without erasing legitimate market differences',
    brief: 'Separate state-specific requirements from avoidable internal variation before the launch clock becomes the decision-maker.',
    tag: 2
  },
  reliability: {
    label: 'Customer reliability pattern',
    state: 'Hold - evidence required before closure',
    outcome: 'Restore service confidence and eliminate the repeat failure mechanism.',
    owner: 'Customer Success + Support + Product/Engineering, with one closure owner',
    dependencies: 'Incident containment, root cause, customer communication, release decision',
    clock: 'Escalate repeat patterns and unresolved customer impact, not every isolated ticket',
    evidence: 'Recurrence, affected workflows, time to containment, corrective-action verification',
    learning: 'Turn recurring support demand into product and operating improvement',
    brief: 'Do not confuse activity with closure: the trace ends only when the repeat mechanism is addressed and the customer outcome is verified.',
    tag: 3
  },
  ecosystem: {
    label: 'Ecosystem integration',
    state: 'Clarify - authority and handoff need one record',
    outcome: 'Create a lower-friction ecosystem while preserving contract, data, and decision boundaries.',
    owner: 'Partnerships + Product + Legal/Compliance, with a single integration lead',
    dependencies: 'Commercial terms, technical interfaces, operating handoffs, support model',
    clock: 'Escalate when decision rights or customer-facing ownership are ambiguous',
    evidence: 'Integration performance, support handoffs, customer friction, control effectiveness',
    learning: 'Use partnership evidence to refine the platform and operating model',
    brief: 'A partnership becomes operational only when customers and teams can trace who owns the next decision.',
    tag: 5
  }
};

function setScenario(key) {
  const s = scenarios[key];
  if (!s) return;
  document.querySelectorAll('.scenario-button').forEach(btn => {
    btn.setAttribute('aria-selected', String(btn.dataset.scenario === key));
  });
  const map = {
    scenarioLabel: s.label, contractState: s.state, outcome: s.outcome, owner: s.owner,
    dependencies: s.dependencies, clock: s.clock, evidence: s.evidence, learning: s.learning,
    decisionBrief: s.brief, heroDecision: s.brief, heroState: s.state
  };
  Object.entries(map).forEach(([id, value]) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  });
  document.querySelectorAll('.trace-tag').forEach((tag, idx) => tag.classList.toggle('active', idx + 1 === s.tag));
}

document.querySelectorAll('.scenario-button').forEach(btn => {
  btn.addEventListener('click', () => setScenario(btn.dataset.scenario));
  btn.addEventListener('keydown', e => {
    if (!['ArrowDown','ArrowUp','ArrowLeft','ArrowRight'].includes(e.key)) return;
    e.preventDefault();
    const buttons = [...document.querySelectorAll('.scenario-button')];
    const i = buttons.indexOf(btn);
    const next = buttons[(i + (e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : -1) + buttons.length) % buttons.length];
    next.focus(); next.click();
  });
});

const menu = document.querySelector('.menu-button');
const navLinks = document.querySelector('.nav-links');
if (menu && navLinks) {
  menu.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });
}

setScenario('modernization');

const heroTrace = (() => {
  const hero = document.querySelector('.hero');
  const field = document.querySelector('.trace-field');
  const stage = document.querySelector('.trace-stage');
  const beam = document.querySelector('.scan-beam');
  const tags = [...document.querySelectorAll('.trace-tag')];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const delays = [0, 0.12, 0.24, 0.36, 0.48];
  const duration = 0.48;
  let frame = 0;

  if (!hero || !field || !stage || !tags.length) return null;

  const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value));
  const smoothstep = value => value * value * (3 - 2 * value);

  function progressForScroll() {
    const nav = document.querySelector('.site-nav');
    const navHeight = nav ? nav.getBoundingClientRect().height : 0;
    const start = hero.offsetTop - navHeight;
    const end = hero.offsetTop + hero.offsetHeight - window.innerHeight;
    if (end <= start) return 1;
    return clamp((window.scrollY - start) / (end - start));
  }

  function render() {
    frame = 0;
    const progress = reducedMotion.matches ? 1 : progressForScroll();
    const fieldWidth = field.clientWidth;

    tags.forEach((tag, index) => {
      const local = clamp((progress - delays[index]) / duration);
      const eased = smoothstep(local);
      const leftInset = parseFloat(getComputedStyle(tag).left) || 24;
      const rightInset = leftInset;
      const travel = Math.max(0, fieldWidth - tag.offsetWidth - leftInset - rightInset);
      tag.style.setProperty('--trace-x', `${(travel * eased).toFixed(2)}px`);
      tag.dataset.tracePhase = local <= 0 ? 'queued' : local >= 1 ? 'arrived' : 'moving';
    });

    if (beam) {
      const beamTravel = fieldWidth * 1.42;
      beam.style.setProperty('--scan-x', `${(beamTravel * progress).toFixed(2)}px`);
    }
    stage.style.setProperty('--trace-scroll-progress', progress.toFixed(4));
  }

  function schedule() {
    if (frame) return;
    frame = window.requestAnimationFrame(render);
  }

  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  if (typeof reducedMotion.addEventListener === 'function') reducedMotion.addEventListener('change', schedule);
  render();

  return { render, progressForScroll };
})();
