export function windowDays(run) {
  if (run?.window?.start && run?.window?.end)
    return Math.round((Date.parse(run.window.end) - Date.parse(run.window.start)) / 86400000) + 1;
  return run?.window_days ?? run?.coverage?.[0]?.eligible ?? 180;
}

export function sourceLabel(run) {
  const proof = run?.sponsor_proofs?.find(item => item.sponsor === 'zetaris');
  if (run?.mode === 'LIVE_SYNTHETIC_ZETARIS' && proof?.status === 'VERIFIED')
    return 'SYNTHETIC · LIVE ZETARIS';
  if (run?.mode === 'LIVE_SYNTHETIC_ZETARIS') return 'SYNTHETIC · ZETARIS FAILED';
  return 'SYNTHETIC · LOCAL';
}

export function isOfflineScientificRun(run) {
  return run?.mode === 'SYNTHETIC_LOCAL_ONLY' &&
    run?.sponsor_proofs?.find(item => item.sponsor === 'zetaris')?.status === 'NOT_CONNECTED' &&
    !!run?.scientific_evidence;
}

// Presentation only: changes of 0.05 or less in the returned unit are shown as
// broadly stable. This is not a Discovery gate, clinical threshold, or test.
export const MEANINGFUL_DISPLAY_DELTA = 0.05;

export function displayChange(difference) {
  if (!Number.isFinite(difference)) return 'unknown';
  return difference < -MEANINGFUL_DISPLAY_DELTA ? 'down'
    : difference > MEANINGFUL_DISPLAY_DELTA ? 'up' : 'flat';
}

export function trajectoryClass(difference) { return displayChange(difference); }

export function trajectoryArrow(difference) {
  return { down: '▼', up: '▲', flat: '→', unknown: '→' }[displayChange(difference)];
}

// User-facing language is derived only from typed investigation evidence.
// The original scientific text, signal table, and identifiers remain in the audit view.
const names = {
  energy_central: 'energy', sleep_hours: 'sleep', stress_score: 'stress',
  caffeine_units: 'caffeine', activity_minutes: 'activity',
};

export function plainDate(iso) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso ?? '')) return '—';
  return new Date(`${iso}T12:00:00Z`).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC',
  });
}

export function comparisonExplanation(run) {
  const comparison = run?.comparison;
  if (!comparison || run?.status !== 'PASS') return null;
  const { baseline, comparison: recent, difference, unit } = comparison;
  if (![baseline?.mean, recent?.mean, difference].every(Number.isFinite) ||
      ![baseline?.observed, recent?.observed].every(Number.isInteger)) return null;
  const subject = comparison.variable === 'sleep_hours' ? 'sleep' : 'energy';
  const unitText = unit === 'hours' ? 'hours' : 'points on a 1–10 scale';
  const meanUnit = unit === 'hours' ? ' hours' : '/10';
  const direction = displayChange(difference);
  const magnitude = Math.abs(difference).toFixed(2);
  const stable = direction === 'flat';
  const directionWord = direction === 'up' ? 'increased' : 'decreased';
  return {
    title: stable ? `Recorded ${subject} remained broadly stable` :
      `Recorded ${subject} ${directionWord} in the recent period`,
    text: `The rounded averages were ${baseline.mean.toFixed(2)}${meanUnit} earlier and ${recent.mean.toFixed(2)}${meanUnit} recently. Using unrounded averages, the difference was ${difference < 0 ? '−' : difference > 0 ? '+' : ''}${magnitude} ${unitText}${stable ? ', within the ±0.05 display band and broadly stable' : `; recorded ${subject} ${directionWord}`}.`,
    coverage: `${subject[0].toUpperCase() + subject.slice(1)} was recorded on ${baseline.observed} of 28 days in the earlier period and ${recent.observed} of 28 days in the recent period. Missing measurements were not filled in.`,
    earlier: `${plainDate(baseline.start)}–${plainDate(baseline.end)}`,
    recent: `${plainDate(recent.start)}–${plainDate(recent.end)}`,
  };
}

export function signalExplanation(signal) {
  if (!signal || !['candidate_signal', 'unstable_candidate'].includes(signal.classification) ||
      !Number.isFinite(signal.effect) || !Number.isInteger(signal.lag_days) ||
      typeof signal.exposure !== 'string' || typeof signal.outcome !== 'string') return null;
  const exposure = names[signal.exposure] ?? signal.exposure.replaceAll('_', ' ');
  const outcome = names[signal.outcome] ?? signal.outcome.replaceAll('_', ' ');
  const timing = signal.lag_days === 0 ? 'on the same day'
    : signal.lag_days > 0 ? `${signal.lag_days} day${signal.lag_days === 1 ? '' : 's'} later`
      : `with a ${Math.abs(signal.lag_days)}-day separation`;
  const direction = signal.effect > 0 ? 'higher' : signal.effect < 0 ? 'lower' : null;
  if (!direction) return null;
  const association = `Higher recorded ${exposure} was associated with ${direction} recorded ${outcome} ${timing}.`;
  const lagLabel = signal.lag_days === 0 ? 'same day' : signal.lag_days === 1 ? 'next day'
    : signal.lag_days > 1 ? `${signal.lag_days} days later` : `${Math.abs(signal.lag_days)}-day separation`;
  const pair = `${exposure[0].toUpperCase() + exposure.slice(1)} and ${outcome}`;
  return signal.classification === 'candidate_signal'
    ? { title: `${pair} — ${lagLabel} · Supported association`, text: `${association} This specific pre-planned test met the scientific checks.` }
    : { title: `${pair} — ${lagLabel} · Exploratory only`, text: `${association} This specific pre-planned test did not pass every scientific check.` };
}

export function findingExplanation(run, finding) {
  if (finding.kind === 'observation') return comparisonExplanation(run) ?? finding;
  if (finding.evidence_signal_id) {
    const signal = run?.scientific_evidence?.signals?.find(item => item.signal_id === finding.evidence_signal_id);
    const explanation = signalExplanation(signal);
    if (explanation) {
      const sameDayQualified = run.scientific_evidence.signals.some(item =>
        item.exposure === 'sleep_hours' && item.outcome === 'energy_central' &&
        item.lag_days === 0 && item.classification === 'candidate_signal');
      if (signal.exposure === 'sleep_hours' && signal.outcome === 'energy_central' &&
          signal.lag_days === 1 && signal.classification === 'unstable_candidate' &&
          sameDayQualified) return { ...explanation,
        text: `${explanation.text} It is a different test from the supported same-day sleep–energy pattern.` };
      return explanation;
    }
  }
  if (finding.kind === 'uncertainty') return {
    title: 'Study limitation',
    text: 'Sleep, stress and caffeine may change together, so this analysis cannot isolate which one explains the pattern.',
  };
  if (finding.kind === 'unsupported_hypothesis') return {
    title: 'No factor met the scientific checks',
    text: 'The pre-planned tests did not identify a qualified association for this outcome. That does not prove no relationship exists.',
  };
  return { title: finding.title, text: finding.text };
}

export function canContinueFrom(run) {
  return run?.status === 'PASS' &&
    ['investigation.v3', 'investigation.v4'].includes(run.contract_version) &&
    typeof run.run_id === 'string' && !!run.scientific_evidence &&
    run.sponsor_proofs?.some(proof =>
      proof.sponsor === 'meterless_engine' && proof.status === 'VERIFIED') === true;
}

export const TRACE_GROUPS = [
  { phases: ['PLAN'], label: 'Plan investigation' },
  { phases: ['TOOLS'], label: 'Analyze scientific evidence' },
  { phases: ['EVIDENCE', 'VERIFY'], label: 'Save and check evidence' },
  { phases: ['RESPOND', 'ABSTAIN'], label: 'Prepare explained result' },
];
