import test from 'node:test';
import assert from 'node:assert/strict';
import { fetchInvestigation, validateScientificInvestigation } from '../client.mjs';

function response() {
  const digest = 'a'.repeat(64);
  return {
    contract_version: 'investigation.v2', synthetic: true, mode: 'SYNTHETIC_LOCAL_ONLY', status: 'PASS',
    run_id: 'SYN-RUN-TEST', window: {start:'2026-07-30',end:'2026-10-21'},
    summary: 'Descriptive finding only.', series: [], coverage: [], comparison: null,
    findings: [{kind:'observation',source_record_ids:[]}],
    tool_trace: [{tool:'meterless.world_model.append',trace_id:digest,engine_event_id:'evt_test',phase:'EVIDENCE',status:'PASS',source_record_ids:[]}],
    sponsor_proofs: [
      {sponsor:'zetaris',status:'NOT_CONNECTED',trace_id:null},
      {sponsor:'meterless_engine',status:'VERIFIED',trace_id:digest},
    ],
    scientific_evidence: {hypothesis_count:16,signals:Array.from({length:16},()=>({exposure:'sleep_hours',classification:'weak_candidate'})),
      plan_sha256:digest,record_digest_sha256:digest,source_query:{request_ids:[]}},
  };
}

test('v2 client sends explicit opt-in and validates the 16-child evidence family', async () => {
  let posted;
  const result = await fetchInvestigation('Why is my energy changing?', {
    analysisVersion:'v2', fetcher:async (_url,options) => {
      posted=JSON.parse(options.body);
      return {ok:true,json:async()=>response()};
    },
  });
  assert.equal(posted.analysis_version,'v2');
  assert.equal(result.scientific_evidence.hypothesis_count,16);
});

test('v2 client rejects untraced live proof and stale scientific evidence', () => {
  const live=response(); live.mode='LIVE_SYNTHETIC_ZETARIS';
  live.sponsor_proofs[0]={sponsor:'zetaris',status:'VERIFIED',trace_id:'invented'};
  assert.throws(()=>validateScientificInvestigation(live),/Zetaris/);
  const failed=response(); failed.status='ERROR';
  assert.throws(()=>validateScientificInvestigation(failed),/Stale/);
});
