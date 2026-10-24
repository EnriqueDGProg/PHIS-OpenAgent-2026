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

export function trajectoryClass(difference) {
  return difference < -0.05 ? 'down' : difference > 0.05 ? 'up' : 'flat';
}

export function trajectoryArrow(difference) {
  return difference < -0.05 ? '▼' : difference > 0.05 ? '▲' : '→';
}
