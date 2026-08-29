import time
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from config import config
from database import DatabaseManager
from monitors import DataIngestionEngine
from notifier import SlackNotifier
from agent_pond import start_telemetry_server

db = DatabaseManager()
ingest_engine = DataIngestionEngine()
notifier = SlackNotifier()

def run_ingestion_pipeline():
    print("[INFO] Starting scheduled GTM ingestion run...")
    new_signals_count = 0

    yc_companies = ingest_engine.fetch_yc_directory()
    speedrun_companies = ingest_engine.fetch_speedrun_directory()
    x_signals = ingest_engine.fetch_x_early_signals()
    linkedin_signals = ingest_engine.fetch_linkedin_early_signals()

    all_signals = yc_companies + speedrun_companies + x_signals + linkedin_signals
    total_scanned = len(all_signals)

    for sig in all_signals:
        inserted = db.insert_signal(sig)
        if inserted:
            new_signals_count += 1
            print(f"[SIGNAL DETECTED] {sig['company_name']} via {sig['source_platform']}")
            notifier.send_signal_alert(sig)

    db.record_metrics(scanned=total_scanned, new_signals=new_signals_count, status="SUCCESS")
    print(f"[INFO] Ingestion completed. Scanned: {total_scanned}, New Alerts: {new_signals_count}")

def get_telemetry_status():
    stats = db.get_stats()
    return {
        "status": "HEALTHY",
        "agent_name": "YC_Speedrun_GTM_Tracker",
        "pond_integration": "ACTIVE",
        "metrics": stats
    }

if __name__ == "__main__":
    print("[INIT] Starting YC & Speedrun Early Signal Bot Agent...")
    
    start_telemetry_server(config.TELEMETRY_PORT, get_telemetry_status)
    print(f"[POND] Telemetry server listening on http://0.0.0.0:{config.TELEMETRY_PORT}/healthz")

    run_ingestion_pipeline()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_ingestion_pipeline,
        'interval',
        hours=config.POLL_INTERVAL_HOURS,
        id='gtm_signal_ingestion_job'
    )
    scheduler.start()
    print(f"[SCHEDULER] Engine active. Intervening polling every {config.POLL_INTERVAL_HOURS} hours.")

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[SHUTDOWN] Bot agent halted cleanly.")
