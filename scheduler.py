import logging
import os
import sys
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv

load_dotenv()

# main.py 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from main import run_generation

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

scheduler = BlockingScheduler(timezone="Asia/Seoul")


def scheduled_job(label: str = ""):
    logger.info(f"⏰ 자동 실행 시작 [{label}] — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    try:
        run_generation()
        logger.info(f"✅ 완료 [{label}]")
    except Exception as e:
        logger.error(f"❌ 오류 [{label}]: {e}", exc_info=True)


# 하루 3회: 오전 9시 / 오후 2시 / 밤 9시
scheduler.add_job(scheduled_job, CronTrigger(hour=9,  minute=0), kwargs={"label": "오전"})
scheduler.add_job(scheduled_job, CronTrigger(hour=14, minute=0), kwargs={"label": "오후"})
scheduler.add_job(scheduled_job, CronTrigger(hour=21, minute=0), kwargs={"label": "저녁"})


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🤖 바이럴 콘텐츠 자동 생성 스케줄러")
    print("=" * 50)
    print("  ├── 09:00  오전 생성")
    print("  ├── 14:00  오후 생성")
    print("  └── 21:00  저녁 생성")
    print("\n  Ctrl+C 로 종료")
    print("=" * 50 + "\n")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n⏹  스케줄러 종료")
