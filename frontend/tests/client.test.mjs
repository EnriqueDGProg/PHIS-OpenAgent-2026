import test from 'node:test';
import assert from 'node:assert/strict';
import { fetchInvestigation, validateInvestigation } from '../client.mjs';

const base = () => ({
  contract_version:'investigation.v1',run_id:'SYN-RUN-test',parent_run_id:null,
  dataset_id:'PHIS-SYN-84D-v1',mode:'SYNTHETIC_LOCAL_ONLY',scenario:'normal',
  status:'PASS',reason_code:null,question:'Energía',timezone:'Europe/Madrid',
  window:{start:'2026-08-27',end:'2026-10-21'},summary:'Observación descriptiva',
  coverage:[],series:[{variable:'energy',unit:'score/10',points:[
    {local_date:'2026-08-27',value:null,source_record_id:null},
    {local_date:'2026-08-28',value:7,source_record_id:'SYN-029-ENERGY'},
  ]}],comparison:{baseline:{mean:7},comparison:{mean:5},difference:-2,source_record_ids:['SYN-029-ENERGY']},
  findings:[],tool_trace:[],sponsor_proofs:[{sponsor:'zetaris',status:'NOT_CONNECTED',trace_id:null}],
});

test('client accepts sourced gaps and rejects fabricated sponsor proof', () => {
  assert.equal(validateInvestigation(base()).status,'PASS');
  const fake = base(); fake.sponsor_proofs[0].status='VERIFIED';
  assert.throws(() => validateInvestigation(fake),/patrocinador/);
});

test('client rejects numeric point without source and comparison in abstention', () => {
  const badPoint=base(); badPoint.series[0].points[1].source_record_id=null;
  assert.throws(() => validateInvestigation(badPoint),/fuente/);
  const blocked=base(); blocked.status='BLOCKED';
  assert.throws(() => validateInvestigation(blocked),/Comparación/);
});

test('client accepts source IDs for sleep_hours follow-up', () => {
  const sleep=base();
  sleep.series[0].variable='sleep_hours'; sleep.series[0].unit='hours';
  sleep.series[0].points[1].source_record_id='SYN-029-SLEEP_HOURS';
  assert.equal(validateInvestigation(sleep).series[0].variable,'sleep_hours');
});

test('insufficient and tool failure cannot retain a previous numeric comparison', () => {
  for (const status of ['INSUFFICIENT_DATA','ERROR']) {
    const run=base();
    run.status=status; run.comparison=null;
    if (status === 'ERROR') run.series=[];
    assert.equal(validateInvestigation(run).status,status);
    run.comparison=base().comparison;
    assert.throws(() => validateInvestigation(run),/Comparación/);
  }
});

test('client sends follow-up and rejects HTTP errors', async () => {
  let sent;
  const accepted = await fetchInvestigation('¿Y el sueño?',{parentRunId:'SYN-RUN-previous',fetcher:async (_,options)=>{
    sent=JSON.parse(options.body); return {ok:true,json:async()=>base()};
  }});
  assert.equal(accepted.run_id,'SYN-RUN-test');
  assert.equal(sent.parent_run_id,'SYN-RUN-previous');
  await assert.rejects(fetchInvestigation('error',{fetcher:async()=>({ok:false,status:503,json:async()=>({error:'No disponible'})})}),/No disponible/);
});
