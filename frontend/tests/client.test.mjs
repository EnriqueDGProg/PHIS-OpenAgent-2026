import test from 'node:test';
import assert from 'node:assert/strict';
import { fetchInvestigation, validateInvestigation } from '../client.mjs';

const base = () => ({
  contract_version:'investigation.v1', run_id:'SYN-RUN-test', parent_run_id:null,
  dataset_id:'PHIS-SYN-84D-v1', mode:'SYNTHETIC_LOCAL_ONLY', scenario:'normal',
  status:'PASS', reason_code:null, question:'Why has my energy changed?', timezone:'Europe/Madrid',
  window:{start:'2026-08-27',end:'2026-10-21'}, summary:'Descriptive observation',
  coverage:[], series:[{variable:'energy',unit:'score/10',points:[
    {local_date:'2026-08-27',value:null,source_record_id:null},
    {local_date:'2026-08-28',value:7,source_record_id:'SYN-029-ENERGY'},
  ]}], comparison:{baseline:{mean:7},comparison:{mean:5},difference:-2,source_record_ids:['SYN-029-ENERGY']},
  findings:[], tool_trace:[], sponsor_proofs:[{sponsor:'zetaris',status:'NOT_CONNECTED',trace_id:null}],
});

test('client accepts sourced gaps and rejects fabricated sponsor proof', () => {
  assert.equal(validateInvestigation(base()).status,'PASS');
  const fake = base(); fake.sponsor_proofs[0].status='VERIFIED';
  assert.throws(() => validateInvestigation(fake), /Unexpected Zetaris proof|local mode/);
});

test('client accepts only an Engine proof tied to a returned event', () => {
  const run=base();
  const eventId='a'.repeat(64);
  run.tool_trace=[{trace_id:eventId,tool:'PLAN',phase:'PLAN',status:'PASS',detail:'local event',source_record_ids:[]}];
  run.sponsor_proofs.push({sponsor:'meterless_engine',status:'VERIFIED',trace_id:eventId});
  assert.equal(validateInvestigation(run).sponsor_proofs[1].status,'VERIFIED');
  run.sponsor_proofs[1].trace_id='b'.repeat(64);
  assert.throws(() => validateInvestigation(run), /sponsor proof|trace/i);
  run.sponsor_proofs[1].trace_id=eventId;
  run.tool_trace[0].tool='zetaris.synthetic_query';
  assert.throws(() => validateInvestigation(run), /Engine/);
});

test('client rejects numeric point without source and comparison in abstention', () => {
  const badPoint=base(); badPoint.series[0].points[1].source_record_id=null;
  assert.throws(() => validateInvestigation(badPoint), /source ID|source/i);
  const blocked=base(); blocked.status='BLOCKED';
  assert.throws(() => validateInvestigation(blocked), /Comparison|non-PASS/i);
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
    assert.throws(() => validateInvestigation(run), /Comparison|non-PASS/i);
  }
});

test('client sends follow-up and rejects HTTP errors', async () => {
  let sent;
  const accepted = await fetchInvestigation('How did my sleep change?',{parentRunId:'SYN-RUN-previous',fetcher:async (_,options)=>{
    sent=JSON.parse(options.body); return {ok:true,json:async()=>base()};
  }});
  assert.equal(accepted.run_id,'SYN-RUN-test');
  assert.equal(sent.parent_run_id,'SYN-RUN-previous');
  await assert.rejects(fetchInvestigation('error',{fetcher:async()=>({ok:false,status:503,json:async()=>({error:'Service unavailable'})})}),/Service unavailable/);
});

test('client accepts agent phases and rejects fabricated phase', () => {
  const run=base(); run.tool_trace=[{trace_id:'a'.repeat(64),tool:'PLAN · trend',status:'PASS',
    detail:'Planned step',source_record_ids:[],phase:'PLAN',reason_code:'planned',parent_event_id:null}];
  assert.equal(validateInvestigation(run).tool_trace[0].phase,'PLAN');
  run.tool_trace[0].phase='SPONSOR_VERIFIED';
  assert.throws(()=>validateInvestigation(run), /Unknown trace/i);
});

test('live mode requires a Zetaris query matching the verified proof', () => {
  const run=base(); run.mode='LIVE_SYNTHETIC_ZETARIS';
  const ids=Array.from({length:156},(_,i)=>`SYN-${String(i).padStart(3,'0')}-ENERGY`);
  run.sponsor_proofs[0]={sponsor:'zetaris',status:'VERIFIED',trace_id:'real-request-id'};
  run.tool_trace=[{trace_id:'real-request-id',tool:'zetaris.synthetic_query',status:'PASS',
    detail:'Verified query',source_record_ids:ids,phase:'EVIDENCE',reason_code:'source_verified',parent_event_id:null,
    query_id:'test-query-id',sql_sha256:'a'.repeat(64)}];
  assert.equal(validateInvestigation(run).mode,'LIVE_SYNTHETIC_ZETARIS');
  run.sponsor_proofs[0].trace_id='invented-request-id';
  assert.throws(()=>validateInvestigation(run), /Zetaris proof not traceable|traceable/i);
  run.sponsor_proofs[0].trace_id='real-request-id';
  run.sponsor_proofs.push({sponsor:'meterless_runtime',status:'VERIFIED',trace_id:'fake'});
  assert.throws(()=>validateInvestigation(run), /sponsor proof|trace/i);
});

test('live source failure has no result or sponsor verification', () => {
  const run=base(); run.mode='LIVE_SYNTHETIC_ZETARIS'; run.status='ERROR';
  run.reason_code='source_error';
  run.series=[]; run.comparison=null;
  run.sponsor_proofs[0]={sponsor:'zetaris',status:'FAILED',trace_id:null};
  assert.equal(validateInvestigation(run).status,'ERROR');
  run.series=base().series;
  assert.throws(()=>validateInvestigation(run), /Source error state|unexpected data/i);
});
