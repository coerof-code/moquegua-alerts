"""
Automated Scheduler for Moquegua Alert System
Runs alert checks 3 times per day at configured times
"""

import sys
from pathlib import Path
from datetime import datetime
import yaml
import pytz
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from src.get_alerts import main as get_alerts_main
from src.generate_maps import main as generate_maps_main


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_logging(config):
    """Setup logging configuration"""
    log_dir = Path(config['paths']['logs'])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


def run_alert_check():
    """Execute alert check and map generation"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=" * 60)
        logger.info("🔄 STARTING SCHEDULED ALERT CHECK")
        logger.info("=" * 60)
        
        # Run alert extraction
        logger.info("Step 1: Extracting alerts...")
        get_alerts_main()
        
        # Run map generation
        logger.info("\nStep 2: Generating maps...")
        generate_maps_main()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ SCHEDULED CHECK COMPLETED SUCCESSFULLY")
        logger.info("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"❌ ERROR during scheduled check: {str(e)}", exc_info=True)


def main():
    """Main scheduler function"""
    config = load_config()
    logger = setup_logging(config)
    
    # Get timezone
    tz = pytz.timezone(config['schedule']['timezone'])
    
    # Create scheduler
    scheduler = BlockingScheduler(timezone=tz)
    
    logger.info("=" * 60)
    logger.info("🤖 MOQUEGUA ALERT MONITORING SCHEDULER")
    logger.info("=" * 60)
    logger.info(f"Timezone: {config['schedule']['timezone']}")
    logger.info(f"Check times: {', '.join(config['schedule']['check_times'])}")
    logger.info("=" * 60 + "\n")
    
    # Add jobs for each check time
    for check_time in config['schedule']['check_times']:
        hour, minute = check_time.split(':')
        
        trigger = CronTrigger(
            hour=int(hour),
            minute=int(minute),
            timezone=tz
        )
        
        scheduler.add_job(
            run_alert_check,
            trigger=trigger,
            id=f'alert_check_{check_time}',
            name=f'Alert Check at {check_time}'
        )
        
        logger.info(f"✅ Scheduled check at {check_time}")
    
    logger.info("\n🚀 Scheduler started. Press Ctrl+C to stop.\n")
    
    # Run initial check
    logger.info("🔄 Running initial check...")
    run_alert_check()
    
    # Start scheduler
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n⏹️  Scheduler stopped by user")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
