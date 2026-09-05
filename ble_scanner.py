
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

logger = logging.getLogger(__name__)

# Apple Bluetooth Company ID
APPLE_COMPANY_ID = 0x004C

# Apple Continuity Protocol - Proximity Pairing message type
PROXIMITY_PAIRING_TYPE = 0x07

# Expected length of the proximity pairing manufacturer data (bytes, after Company ID)
PROXIMITY_PAIRING_DATA_LEN = 27

# Known AirPods / Beats model identifiers (hex chars 4-7 of manufacturer data)
AIRPODS_MODELS: Dict[str, str] = {
    "0220": "AirPods 1",
    "0F20": "AirPods 2",
    "1320": "AirPods 3",
    "1920": "AirPods 4",
    "0E20": "AirPods Pro",
    "1420": "AirPods Pro 2",
    "2420": "AirPods Pro 3",
    "0A20": "AirPods Max",
    "0520": "Beats X",
    "0620": "Beats Solo 3",
    "0920": "Beats Studio 3",
    "1020": "Beats Solo Pro",
    "0320": "Powerbeats 3",
    "0B20": "Powerbeats Pro",
    "0D20": "Beats Flex",
}


@dataclass
class AirPodsBattery:

    left: int             # 0-100 percentage, -1 if disconnected
    right: int            # 0-100 percentage, -1 if disconnected
    case: int             # 0-100 percentage, -1 if disconnected
    left_charging: bool  = False
    right_charging: bool = False
    case_charging: bool  = False
    model: str           = "AirPods"
    rssi: int            = -100

    @property
    def min_pod_battery(self) -> int:

        levels = [lv for lv in (self.left, self.right) if lv >= 0]
        return min(levels) if levels else -1

    @property
    def is_connected(self) -> bool:
        return self.left >= 0 or self.right >= 0



def _nibble_to_battery(hex_char: str) -> int:

    val = int(hex_char, 16)
    if val > 10:          # 0xF (15) = disconnected; values 11-14 are invalid
        return -1
    return val * 10       # 0 -> 0%, 1 -> 10%, ... 10 -> 100%


def parse_proximity_pairing(data: bytes, rssi: int = -100) -> Optional[AirPodsBattery]:

    if len(data) < 27:
        return None


    if data[0] != PROXIMITY_PAIRING_TYPE:
        return None

    hex_str = data.hex()


    model_id = hex_str[4:8].upper()

    model_name = AIRPODS_MODELS.get(model_id, "AirPods 3")


    is_flipped = (int(hex_str[10], 16) & 0x02) != 0


    left_char  = hex_str[12]
    right_char = hex_str[13]

    if is_flipped:
        left_char, right_char = right_char, left_char

    left_battery  = _nibble_to_battery(left_char)
    right_battery = _nibble_to_battery(right_char)
    case_battery  = _nibble_to_battery(hex_str[15])

 
    charge_bits = int(hex_str[14], 16)
    left_charging  = bool(charge_bits & 0x01)
    right_charging = bool(charge_bits & 0x02)
    case_charging  = bool(charge_bits & 0x04)

    if is_flipped:
        left_charging, right_charging = right_charging, left_charging

    return AirPodsBattery(
        left=left_battery,
        right=right_battery,
        case=case_battery,
        left_charging=left_charging,
        right_charging=right_charging,
        case_charging=case_charging,
        model=model_name,
        rssi=rssi,
    )


def _find_proximity_pairing(manufacturer_data: bytes) -> Optional[bytes]:
    offset = 0
    while offset < len(manufacturer_data) - 1:
        msg_type = manufacturer_data[offset]
        msg_len  = manufacturer_data[offset + 1]

        end = offset + 2 + msg_len
        if end > len(manufacturer_data):
            break

        if msg_type == PROXIMITY_PAIRING_TYPE and msg_len >= 25:
            return manufacturer_data[offset:end]

        offset = end

    return None


import time

class AirPodsScanner:


    def __init__(
        self,
        callback: Callable[[Optional[AirPodsBattery]], None],
        scan_duration: float = 3.0,
        scan_interval: float = 10.0,
        timeout: float = 25.0,  # 25 seconds before considering them disconnected
    ):
        self._callback = callback
        self._scan_duration = scan_duration
        self._scan_interval = scan_interval
        self._timeout = timeout
        self._running = False

 
        self._candidates: List[AirPodsBattery] = []

        self._last_result: Optional[AirPodsBattery] = None
        self._last_seen_time: float = 0.0



    def _on_advertisement(
        self, device: BLEDevice, adv: AdvertisementData
    ) -> None:

        if APPLE_COMPANY_ID not in adv.manufacturer_data:
            return

        raw = adv.manufacturer_data[APPLE_COMPANY_ID]


        result = parse_proximity_pairing(raw, rssi=adv.rssi)


        if result is None:
            chunk = _find_proximity_pairing(raw)
            if chunk is not None:
                result = parse_proximity_pairing(chunk, rssi=adv.rssi)

        if result is not None and result.is_connected:
            self._candidates.append(result)

    def _pick_best(self) -> Optional[AirPodsBattery]:

        if not self._candidates:
            return None


        airpods3 = [c for c in self._candidates if "AirPods 3" in c.model]
        pool = airpods3 if airpods3 else self._candidates
        return max(pool, key=lambda c: c.rssi)

    

    async def scan_once(self) -> Optional[AirPodsBattery]:
       
        self._candidates.clear()

        scanner = BleakScanner(detection_callback=self._on_advertisement)
        try:
            await scanner.start()
            await asyncio.sleep(self._scan_duration)
            await scanner.stop()
        except OSError as exc:
            logger.warning("BLE scan failed (Bluetooth off?): %s", exc)
            return None
        except Exception as exc:
            logger.error("Unexpected BLE error: %s", exc)
            return None

        return self._pick_best()

    async def run(self) -> None:

        self._running = True
        logger.info("AirPods BLE scanner started (interval=%ss)", self._scan_interval)

        while self._running:
            result = await self.scan_once()
            now = time.time()

            if result is not None:
                self._last_result = result
                self._last_seen_time = now
                logger.debug(
                    "AirPods found: L=%s%% R=%s%% Case=%s%% model=%s RSSI=%s",
                    result.left, result.right, result.case,
                    result.model, result.rssi,
                )
            else:

                if self._last_result is not None and (now - self._last_seen_time) < self._timeout:
                    result = self._last_result
                    logger.debug("Missed beacon, using cached battery state")
                else:
                    self._last_result = None

            self._callback(result)


            for _ in range(int(self._scan_interval)):
                if not self._running:
                    break
                await asyncio.sleep(1.0)

        logger.info("AirPods BLE scanner stopped")

    def stop(self) -> None:
        self._running = False
