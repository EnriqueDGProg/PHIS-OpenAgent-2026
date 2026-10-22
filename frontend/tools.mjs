import { records, fixtureMeta } from './fixture.mjs';

/** @typedef {'success'|'insufficient'|'unsupported'|'error'} RunStatus */
/** @typedef {{id:string,label:string,status:'complete'|'blocked'|'error',detail:string}} TraceStep */
/** @typedef {{id:string,kind:'observation'|'hypothesis'|'uncertainty'|'abstention',title:string,body:string,sourceIds:string[]}} Finding */
/** @typedef {{id:string,question:string,status:RunStatus,summary:string,coverage:{eligible:number,energy:number,sleep:number},trend:readonly import('./fixture.mjs').DailyRecord[],periods?:{earlier:{n:number,mean:number},recent:{n:number,mean:number}},findings:Finding[],trace:TraceStep[],source:typeof fixtureMeta}} Investigation */

const mean = values => values.reduce((sum, value) => sum + value, 0) / values.length;
const round1 = value => Math.round(value * 10) / 10;

export function getVariableCoverage(data = records) {
  return { eligible: data.length, energy: data.filter(row => row.energy !== null).length, sleep: data.filter(row => row.sleepHours !== null).length };
}

export function getLongitudinalTrend(data = records) {
  return data.map(row => ({ ...row }));
}

export function comparePeriods(data = records) {
  const midpoint = Math.floor(data.length / 2);
  const earlierValues = data.slice(0, midpoint).flatMap(row => row.energy === null ? [] : [row.energy]);
  const recentValues = data.slice(midpoint).flatMap(row => row.energy === null ? [] : [row.energy]);
  if (earlierValues.length < 7 || recentValues.length < 7) return null;
  return { earlier: { n: earlierValues.length, mean: round1(mean(earlierValues)) }, recent: { n: recentValues.length, mean: round1(mean(recentValues)) } };
}

/** Local, deterministic fixture adapter. Never describes sponsor or backend calls. */
export async function investigate(question, options = {}) {
  const id = `LOCAL-${Date.now()}`;
  const normalized = question.trim().toLocaleLowerCase('es');
  const trace = [{ id: 'plan', label: 'Plan local', status: 'complete', detail: 'Clasificación acotada de la pregunta sobre el fixture sintético.' }];
  const coverage = getVariableCoverage(options.data || records);
  const base = { id, question, coverage, trend: [], findings: [], trace, source: fixtureMeta };
  if (options.failTool) {
    trace.push({ id: 'coverage', label: 'get_variable_coverage', status: 'error', detail: 'Fallo de herramienta de prueba. Ningún resultado se presenta como válido.' });
    return { ...base, status: 'error', summary: 'No se pudo completar la exploración local. Vuelve a intentarlo.', findings: [{ id: 'ERR-01', kind: 'abstention', title: 'Resultado no disponible', body: 'La herramienta de cobertura falló; no mostramos cifras ni inferencias.', sourceIds: [] }] };
  }
  if (/medicaci[oó]n|diagn[oó]stic|tratamiento|receta|dosis/.test(normalized)) {
    trace.push({ id: 'scope', label: 'Comprobación de alcance', status: 'blocked', detail: 'La pregunta solicita consejo clínico fuera del alcance de esta demo.' });
    return { ...base, status: 'unsupported', summary: 'No puedo recomendar cambios de medicación ni establecer un diagnóstico.', findings: [{ id: 'SCOPE-01', kind: 'abstention', title: 'Fuera del alcance', body: 'Puedes explorar cómo variaron tus registros de energía y sueño, sin convertirlos en consejo médico.', sourceIds: [] }] };
  }
  if (!/energ|sueñ|sueno|dorm|descans|cansan|fatig/.test(normalized)) {
    trace.push({ id: 'scope', label: 'Comprobación de alcance', status: 'blocked', detail: 'No hay una herramienta local autorizada para esta pregunta.' });
    return { ...base, status: 'unsupported', summary: 'Esta vista local solo explora registros de energía y sueño.', findings: [{ id: 'SCOPE-02', kind: 'abstention', title: 'Pregunta no cubierta', body: 'Pregunta por la evolución de energía o sueño durante este periodo.', sourceIds: [] }] };
  }
  trace.push({ id: 'coverage', label: 'get_variable_coverage', status: 'complete', detail: `${coverage.energy} registros de energía y ${coverage.sleep} de sueño en ${coverage.eligible} días elegibles.` });
  const data = options.data || records;
  if (coverage.energy < 14) {
    trace.push({ id: 'trend', label: 'get_longitudinal_trend', status: 'blocked', detail: 'Cobertura insuficiente para la comparación local de periodos.' });
    return { ...base, status: 'insufficient', summary: 'Hay pocos registros de energía para comparar los dos periodos.', findings: [{ id: 'COV-01', kind: 'abstention', title: 'Evidencia insuficiente', body: `${coverage.energy} de ${coverage.eligible} días tienen energía registrada. No se calcula una comparación.`, sourceIds: data.filter(row => row.energy !== null).map(row => row.id) }] };
  }
  const trend = getLongitudinalTrend(data);
  trace.push({ id: 'trend', label: 'get_longitudinal_trend', status: 'complete', detail: 'Serie diaria leída del fixture; los días ausentes permanecen como huecos.' });
  const periods = comparePeriods(data);
  trace.push({ id: 'compare', label: 'compare_periods', status: periods ? 'complete' : 'blocked', detail: periods ? 'Medias descriptivas calculadas para mitades consecutivas de 21 días.' : 'No hay cobertura suficiente en ambos periodos.' });
  const sourceIds = data.filter(row => row.energy !== null).map(row => row.id);
  const findings = [];
  if (periods) findings.push({ id: 'OBS-01', kind: 'observation', title: 'Cambio observado en energía', body: `La media registrada fue ${periods.earlier.mean.toFixed(1)} en los primeros 21 días y ${periods.recent.mean.toFixed(1)} en los últimos 21 (${periods.earlier.n} y ${periods.recent.n} registros).`, sourceIds });
  findings.push({ id: 'HYP-01', kind: 'hypothesis', title: 'Sueño como línea de investigación', body: 'El sueño tiene registros en el mismo periodo. Podría explorarse con un análisis validado; esta vista local no calcula asociación estadística.', sourceIds: data.filter(row => row.sleepHours !== null).map(row => row.id) });
  findings.push({ id: 'UNC-01', kind: 'uncertainty', title: 'Lo que estos datos no establecen', body: 'Una comparación descriptiva no identifica causas. No se ha ejecutado una prueba de asociación ni un análisis causal.', sourceIds: [] });
  trace.push({ id: 'discovery', label: 'run_predeclared_discovery', status: 'blocked', detail: 'Motor científico no conectado en modo fixture. No se emiten asociaciones.' });
  trace.push({ id: 'evidence', label: 'get_evidence_package', status: 'complete', detail: 'IDs de registros sintéticos enlazados a cada observación.' });
  return { ...base, status: 'success', summary: periods ? `En esta muestra sintética, la energía registrada pasó de ${periods.earlier.mean.toFixed(1)} a ${periods.recent.mean.toFixed(1)} entre los dos periodos. La causa sigue sin establecerse.` : 'No hay suficientes datos para comparar los periodos.', trend, periods, findings, trace };
}
