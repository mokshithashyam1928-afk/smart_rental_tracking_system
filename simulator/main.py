"""
IoT Equipment Telemetry Simulator entry point.
Publishes telemetry streams to MQTT broker and/or Django backend HTTP endpoint.
"""
import json
import logging
import time
import requests
from config import (
    MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_TOPIC_PREFIX,
    BACKEND_API_URL, SIMULATION_INTERVAL_SECONDS,
    SITES, SIMULATED_FLEET
)
from generator import TelemetryGenerator

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [SIMULATOR] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_site_by_code(site_code):
    for site in SITES:
        if site['site_code'] == site_code:
            return site
    return SITES[0]


def init_generators():
    generators = []
    for machine in SIMULATED_FLEET:
        site = get_site_by_code(machine.get('site_code'))
        gen = TelemetryGenerator(machine, site)
        generators.append(gen)
    return generators


def send_via_rest(telemetry_data: dict):
    """Send telemetry point directly to Django backend API."""
    try:
        response = requests.post(BACKEND_API_URL, json=telemetry_data, timeout=3.0)
        if response.status_code in [200, 201]:
            logger.info(f"REST Ingest SUCCESS -> {telemetry_data['equipment_id']} (speed: {telemetry_data['speed']} km/h, fuel: {telemetry_data['fuel_level']}%)")
        else:
            logger.debug(f"REST Ingest status {response.status_code} for {telemetry_data['equipment_id']}")
    except Exception as e:
        logger.debug(f"REST Ingest error: {e}")


def main():
    logger.info("Initializing IoT Equipment Telemetry Simulator...")
    generators = init_generators()
    logger.info(f"Initialized {len(generators)} simulated machines across {len(SITES)} construction sites.")

    # Try optional MQTT client
    mqtt_client = None
    try:
        import paho.mqtt.client as mqtt
        mqtt_client = mqtt.Client(client_id="smart-rental-iot-simulator")
        mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
        mqtt_client.loop_start()
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}")
    except Exception as e:
        logger.warning(f"MQTT broker not connected ({e}). Defaulting to direct REST ingestion.")

    logger.info("Simulator running. Emitting telemetry ticks...")
    try:
        while True:
            for gen in generators:
                telemetry = gen.next_telemetry()
                topic = f"{MQTT_TOPIC_PREFIX}/{telemetry['equipment_id']}"

                # 1. Publish to MQTT if connected
                if mqtt_client and mqtt_client.is_connected():
                    mqtt_client.publish(topic, json.dumps(telemetry))

                # 2. Ingest via REST
                send_via_rest(telemetry)

            time.sleep(SIMULATION_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logger.info("Stopping telemetry simulator.")
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()


if __name__ == '__main__':
    main()
