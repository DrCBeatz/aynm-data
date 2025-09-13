# tests/test_etl.py

import pandas as pd
import subprocess, sys, json, os

def run_cli(args):
    return subprocess.run([sys.executable, "stocky_to_coast.py"] + args, capture_output=True, text=True)

def test_happy_path(tmp_path):
    outdir = tmp_path / "runs"
    res = run_cli(["--po","999","--input","tests/fixtures/good.csv","--outdir",str(outdir)])
    assert res.returncode == 0
    summary = json.loads(res.stdout)
    assert summary["rows_out"] == 2
    assert summary["status"] == "OK"

def test_missing_required_column(tmp_path):
    outdir = tmp_path / "runs"
    res = run_cli(["--po","1000","--input","tests/fixtures/bad_missing_col.csv","--outdir",str(outdir)])
    assert res.returncode == 1
    assert "VALIDATION ERROR" in res.stderr

def test_totals_mismatch_fails(tmp_path):
    outdir = tmp_path / "runs"
    res = run_cli(["--po","1001","--input","tests/fixtures/bad_totals.csv","--outdir",str(outdir)])
    assert res.returncode == 1

def test_dedupes_and_recalculates(tmp_path):
    outdir = tmp_path / "runs"
    res = run_cli(["--po","1002","--input","tests/fixtures/good.csv","--outdir",str(outdir)])
    assert res.returncode == 0
    # assert deduped output has expected totals/rows
