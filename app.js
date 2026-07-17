const scenarios = {
  modernization: {
    intent: 'Modernize the platform without destabilizing daily regulatory work.',
    owner: 'CTO with CEO-sponsored cross-functional ownership.',
    dependency: 'Product, engineering, support, customer experience, regulators, and integrators.',
    decision: 'Release scope, migration posture, readiness threshold, and exception path.',
    outcome: 'Higher reliability and usability with controlled adoption.',
    state: 'Traceable - decision threshold defined',
    risk: 'A technically sound release can still fail through fragmented readiness and communication.'
  },
  market: {
    intent: 'Launch a new jurisdiction with confidence and minimal operating disruption.',
    owner: 'Market implementation leader with executive escalation rights.',
    dependency: 'Government affairs, product configuration, training, support, licensees, and partners.',
    decision: 'Credentialing readiness, cutover sequence, issue severity, and go-live posture.',
    outcome: 'A safe, comprehensible transition for regulators and operators.',
    state: 'Traceable - cross-functional cutover mapped',
    risk: 'The visible launch date can conceal unresolved training, support, or data dependencies.'
  },
  retail: {
    intent: 'Scale Retail ID from compliance utility into trusted post-sale visibility.',
    owner: 'Product and growth leaders with explicit public-safety and operator outcomes.',
    dependency: 'Brands, retailers, integrators, regulators, support, marketing, and data quality.',
    decision: 'Market sequence, adoption friction, partner readiness, and evidence of value.',
    outcome: 'More item-level traceability, consumer confidence, and operational efficiency.',
    state: 'Traceable - adoption evidence connected',
    risk: 'Adoption volume alone can obscure whether the workflow is easier and the data is trusted.'
  },
  partnership: {
    intent: 'Create strategic leverage while preserving accountability and continuity.',
    owner: 'CEO-designated executive owner with clear entity and interface boundaries.',
    dependency: 'Legal, finance, product, government customers, operations, and partner leadership.',
    decision: 'Decision rights, integration boundaries, service continuity, and success evidence.',
    outcome: 'Expanded capability without blurred ownership or customer confusion.',
    state: 'Traceable - boundary and handoff explicit',
    risk: 'Partnership value erodes when interfaces are assumed instead of instrumented.'
  }
};

function setScenario(key) {
  const s = scenarios[key];
  if (!s) return;
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.setAttribute('aria-pressed', String(btn.dataset.scenario === key));
  });
  const bindings = ['intent','owner','dependency','decision','outcome','state','risk'];
  bindings.forEach(name => {
    document.querySelectorAll(`[data-bind="${name}"]`).forEach(el => {
      el.textContent = s[name];
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => setScenario(btn.dataset.scenario));
  });
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle.setAttribute('aria-expanded','false');
    }));
  }
  setScenario('modernization');
});
