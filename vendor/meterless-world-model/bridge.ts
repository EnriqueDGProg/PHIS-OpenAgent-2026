// PHIS adapter to the unmodified Meterless World Model reference Engine.
// One request per process makes every read exercise durable rehydration.
import path from "node:path";
import { WorldModel } from "./src/index.ts";

type Request = {
  operation: "append" | "read";
  statePath: string;
  runId: string;
  event?: Record<string, unknown>;
};

const chunks: Buffer[] = [];
for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk));

function records(world: WorldModel, runId: string) {
  return world.events().filter((item) => item.kind === "upsertEntity")
    .map((item) => ({ event: (item.payload as { attrs?: { event?: Record<string, unknown> } }).attrs?.event,
                      engine_event_id: item.id }))
    .filter((item) => item.event?.run_id === runId);
}

try {
  const request = JSON.parse(Buffer.concat(chunks).toString("utf8")) as Request;
  if (!/^[A-Za-z0-9_-]+$/.test(path.parse(request.statePath).name) ||
      !/^SYN-RUN-[A-Za-z0-9_-]{1,64}$/.test(request.runId)) {
    throw new Error("Invalid synthetic World Model scope");
  }
  const worldOptions = {
    storage: "local" as const,
    namespace: path.parse(request.statePath).name,
    directory: path.dirname(path.resolve(request.statePath)),
  };
  const world = new WorldModel(worldOptions);
  if (request.operation === "append") {
    const event = request.event;
    if (!event || event.run_id !== request.runId || event.synthetic !== true ||
        typeof event.event_id !== "string" || !/^[a-f0-9]{64}$/.test(event.event_id)) {
      throw new Error("Invalid synthetic event");
    }
    const existing = records(world, request.runId).find((item) => item.event?.event_id === event.event_id);
    if (!existing) {
      const at = "2026-10-22T00:00:00.000Z";
      const source = { kind: "agent", by: "phis-synthetic-agent", at, runId: request.runId };
      await world.upsertContext({
        type: "synthetic-run", externalKey: { system: "phis", id: request.runId },
        attrs: { synthetic: true }, source,
      });
      await world.upsertEntity({
        type: "synthetic-run-event", externalKey: { system: "phis", id: event.event_id },
        attrs: { event }, source,
      });
    }
    // Re-open from disk: a successful append is only acknowledged if the
    // canonical Engine event log can supply the same record to a new process.
    const reopened = new WorldModel(worldOptions);
    const receipt = records(reopened, request.runId).find((item) => item.event?.event_id === event.event_id);
    if (!receipt || JSON.stringify(receipt.event) !== JSON.stringify(event)) {
      throw new Error("World Model durable readback failed");
    }
    process.stdout.write(JSON.stringify({ event, engine_event_id: receipt.engine_event_id, durable_readback: true }));
  } else if (request.operation === "read") {
    process.stdout.write(JSON.stringify({ records: records(world, request.runId) }));
  } else {
    throw new Error("Unsupported World Model operation");
  }
} catch (error) {
  // Keep input and event payloads out of logs.
  process.stderr.write(`Meterless World Model bridge: ${(error as Error).message}\n`);
  process.exitCode = 1;
}
