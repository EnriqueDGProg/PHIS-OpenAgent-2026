"""Explicit activation steps for the Zetaris direct REST integration."""

import argparse
import json
import sys

from .zetaris import ZetarisBlocked, ZetarisClient, ZetarisConfig, registration_sql
from .zetaris_export import export_csv


def main(argv=None, *, transport=None, environ=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    prepare = actions.add_parser("prepare", help="write only fictional observations locally")
    prepare.add_argument("--out", required=True)
    actions.add_parser("preflight", help="read-only REST and SELECT 1")
    register = actions.add_parser("register", help="register a server-visible synthetic CSV")
    register.add_argument("--server-path", required=True)
    register.add_argument("--execute", action="store_true", help="send two CREATE statements")
    actions.add_parser("query", help="read-only bounded synthetic query")
    args = parser.parse_args(argv)
    try:
        if args.action == "prepare":
            result = export_csv(args.out)
        elif args.action == "register" and not args.execute:
            result = {"status": "DRY_RUN", "sql": registration_sql(args.server_path),
                      "note": "The CSV must already be visible inside the Zetaris server."}
        else:
            client = ZetarisClient(ZetarisConfig.from_env(environ), transport=transport)
            preflight = client.preflight()
            if args.action == "preflight":
                result = preflight
            elif args.action == "register":
                result = {"status": "EXECUTED_UNVERIFIED", "registration_traces":
                          client.register_synthetic_csv(args.server_path),
                          "note": "Run query to verify returned synthetic rows."}
            else:
                result = client.query_synthetic()
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except FileExistsError:
        print(json.dumps({"status": "BLOCKED", "reason": "Output file already exists"}), file=sys.stderr)
        return 2
    except (ZetarisBlocked, ValueError) as error:
        # Error types and missing variable names are safe. Never print request,
        # response, server path or credentials here.
        print(json.dumps({"status": "BLOCKED", "reason": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
