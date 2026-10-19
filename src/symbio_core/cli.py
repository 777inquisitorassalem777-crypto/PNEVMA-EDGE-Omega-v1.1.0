import argparse, json, os
from .engine import SymbioEngine

def main():
    p = argparse.ArgumentParser(prog="symbio-core")
    sub = p.add_subparsers(dest="cmd", required=True)
    tick = sub.add_parser("tick"); tick.add_argument("--observation", required=True)
    for name, default in [("harm-risk",0.0),("benefit",0.5),("consent",0.5),("reversibility",0.5),("uncertainty",0.5)]:
        tick.add_argument("--"+name, type=float, default=default)
    sub.add_parser("report")
    run = sub.add_parser("run"); run.add_argument("--interval", type=float, default=.5); run.add_argument("--report-interval", type=float, default=1800)
    args = p.parse_args()
    engine = SymbioEngine(os.getenv("SYMBIO_DB_PATH", "data/symbio_core.sqlite3"))
    if args.cmd == "tick":
        context = {"proposed_action": {"harm_risk": args.harm_risk, "benefit": args.benefit,
            "consent": args.consent, "reversibility": args.reversibility, "uncertainty": args.uncertainty}}
        print(json.dumps(engine.tick(args.observation, context), ensure_ascii=False, indent=2))
        engine.memory.close()
    elif args.cmd == "report":
        print(json.dumps(engine.report(), ensure_ascii=False, indent=2)); engine.memory.close()
    else: engine.run(args.interval, args.report_interval)

if __name__ == "__main__": main()
