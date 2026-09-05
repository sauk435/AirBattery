

import asyncio
import logging
import sys
import threading

from ble_scanner import AirPodsScanner
from tray_icon import AirPodsTray


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("airpods")


def main() -> None:
    tray = AirPodsTray()
    scanner = AirPodsScanner(
        callback=tray.update,
        scan_duration=3.0,
        scan_interval=10.0,
    )


    def setup(icon):
        """Runs in the pystray setup thread."""
        icon.visible = True
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(scanner.run())
        except Exception:
            logger.exception("Scanner crashed")
        finally:
            loop.close()
            logger.info("Scanner thread exited")

    try:
        logger.info("AirPods Battery Monitor starting...")
        tray.run(setup_callback=setup, stop_callback=scanner.stop)
    except KeyboardInterrupt:
        scanner.stop()
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)

    logger.info("AirPods Battery Monitor stopped.")


if __name__ == "__main__":
    main()
