"""Check scientific perturbation properties in local-only validation JSON outputs.

Accepts only derived synthetic statistics; it never loads PHIS source or records.
"""

import argparse
import json
from pathlib import Path


def read(path, mode):
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    assert value["mode"] == mode, f"wrong mode in {path}"
    assert value["rows"] == 504, f"wrong row count in {path}"
    return value


def check(baseline, ablate, reverse, low_coverage):
    for family in ("energy", "sleep"):
        assert baseline[family]["count"] == 16
        assert not baseline[family]["negative_control_promoted"]
        assert not ablate[family]["negative_control_promoted"]
        assert baseline[family]["plan_sha256"] == ablate[family]["plan_sha256"]
    energy = baseline["energy"]["selected"][0]
    caffeine = baseline["sleep"]["selected"][0]
    assert energy["exposure"] == "sleep_hours" and energy["class"] == "candidate_signal"
    assert caffeine["exposure"] == "late_caffeine" and caffeine["class"] != "candidate_signal"
    assert ablate["energy"]["target"]["class"] != "candidate_signal"
    assert ablate["sleep"]["target"]["class"] != "candidate_signal"
    assert abs(ablate["energy"]["target"]["r"]) < abs(energy["r"])
    assert abs(ablate["sleep"]["target"]["r"]) < abs(caffeine["r"])
    assert reverse["energy"]["plan_sha256"] == baseline["energy"]["plan_sha256"]
    assert reverse["energy"]["target"]["r"] * energy["r"] < 0
    assert abs(abs(reverse["energy"]["target"]["r"]) - abs(energy["r"])) < 1e-10
    assert not reverse["energy"]["negative_control_promoted"]
    assert low_coverage["energy"]["plan_sha256"] == baseline["energy"]["plan_sha256"]
    assert low_coverage["energy"]["target"]["class"] == "insufficient_data"
    assert low_coverage["energy"]["target"]["coverage"] < 0.7
    assert not low_coverage["energy"]["negative_control_promoted"]


def main():
    parser = argparse.ArgumentParser()
    for mode in ("baseline", "ablate", "reverse", "low-coverage"):
        parser.add_argument(mode.replace("-", "_"), type=Path)
    paths = vars(parser.parse_args())
    check(*(read(paths[mode.replace("-", "_")], mode)
            for mode in ("baseline", "ablate", "reverse", "low-coverage")))
    print("PASS: baseline, ablation, sign reversal, low coverage, control, plan identity")


if __name__ == "__main__":
    main()

