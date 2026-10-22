/** @typedef {{id:string,date:string,energy:number|null,sleepHours:number|null,source:'synthetic-daily-checkin'}} DailyRecord */
/** @type {readonly DailyRecord[]} */
export const records = Object.freeze(Array.from({ length: 42 }, (_, index) => {
  const day = new Date(Date.UTC(2026, 8, 9 + index));
  const date = day.toISOString().slice(0, 10);
  const missingEnergy = [7, 8, 24, 25, 26, 37].includes(index);
  const missingSleep = [5, 6, 18, 24, 25, 33].includes(index);
  const energy = missingEnergy ? null : Math.max(2, Math.min(9, Math.round((index < 21 ? 7.2 : 5.5) + Math.sin(index * 1.3) * 0.9)));
  const sleepHours = missingSleep ? null : Math.round(((index < 21 ? 7.45 : 6.85) + Math.sin(index * 0.83) * 0.52) * 10) / 10;
  return Object.freeze({ id: `SYN-${String(index + 1).padStart(3, '0')}`, date, energy, sleepHours, source: 'synthetic-daily-checkin' });
}));

export const fixtureMeta = Object.freeze({
  id: 'PHIS-SYN-ENERGY-01',
  label: 'Participante ficticio · registros generados para la demo',
  createdFor: 'PHIS Open Agent Hackathon 2026',
  source: 'Fixture local, sin conexión a servicios ni datos de salud reales',
  energyUnit: 'escala subjetiva 1–10',
  sleepUnit: 'horas autodeclaradas'
});
