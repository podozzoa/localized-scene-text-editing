from __future__ import annotations

from harness.runners.common import execute_manifest, load_run_config, parse_runner_args, write_run_bundle


def main() -> None:
    args = parse_runner_args()
    config = load_run_config(args.config, benchmark_manifest=args.benchmark_manifest, run_name=args.run_name, output_root=args.output_root)
    run_result = execute_manifest(config)
    destination = run_result["config_snapshot"]["output_root"]
    path = write_run_bundle(run_result, str(destination), config_path=args.config)
    print(f"candidate_run_result: {path}")


if __name__ == "__main__":
    main()
