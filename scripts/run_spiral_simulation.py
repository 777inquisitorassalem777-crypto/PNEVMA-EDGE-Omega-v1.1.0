import argparse, json, time
from datetime import datetime, timezone
from pathlib import Path
from symbio_core.spiral import LivingSpiral, Experience

CASES=[
 Experience("Обсуждается решение с возможным вредом.",{"proposed_action":{"harm_risk":.7,"benefit":.6,"consent":.4,"reversibility":.5,"uncertainty":.6}},.4,.5,.6),
 Experience("Новые данные требуют пересмотра прежнего мнения.",{"proposed_action":{"harm_risk":.2,"benefit":.7,"consent":.9,"reversibility":.8,"uncertainty":.3}},.7,.1,.3),
 Experience("Недостаточно данных о последствиях для уязвимой группы.",{"proposed_action":{"harm_risk":.6,"benefit":.5,"consent":.4,"reversibility":.7,"uncertainty":.85}},.3,.4,.85)
]
def main():
    p=argparse.ArgumentParser(description="Safe Living Spiral simulation")
    p.add_argument("--cycles",type=int,default=20,help="finite mode cycle count")
    p.add_argument("--interval",type=float,default=.5,help="seconds between cycles")
    p.add_argument("--report-every",type=float,default=1800,help="report interval in seconds (default 30 minutes)")
    p.add_argument("--forever",action="store_true",help="run continuously until Ctrl+C")
    p.add_argument("--ledger",default="data/spiral_ledger.sqlite3")
    p.add_argument("--report-dir",default="results/spiral_reports")
    a=p.parse_args()
    spiral=LivingSpiral(ledger_path=a.ledger)
    report_dir=Path(a.report_dir); report_dir.mkdir(parents=True,exist_ok=True)
    next_report=time.monotonic()+max(1,a.report_every)
    i=0
    try:
        while a.forever or i<max(1,a.cycles):
            spiral.process(CASES[i%len(CASES)])
            i+=1
            now=time.monotonic()
            if now>=next_report:
                report=spiral.report()
                out=report_dir/f"report_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
                out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
                print(json.dumps({"report_saved":str(out),"cycles":i,"ledger_integrity":report["ledger_integrity"]},ensure_ascii=False),flush=True)
                next_report=now+max(1,a.report_every)
            if a.interval>0: time.sleep(a.interval)
        report=spiral.report()
        print(json.dumps(report,ensure_ascii=False,indent=2))
    except KeyboardInterrupt:
        report=spiral.report()
        print(json.dumps({"stopped_by_user":True,"final_report":report},ensure_ascii=False,indent=2))
    finally:
        spiral.close()
if __name__=="__main__": main()
