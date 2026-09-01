#!/bin/bash
# Kafka topic initialization script for Smart Rental Tracking System (Phase 3)

echo "Waiting for Kafka broker to be ready..."
cub kafka-ready -b kafka:9092 1 30

echo "Creating Kafka topics..."
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic smart-rental.telemetry.events --partitions 3 --replication-factor 1
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic smart-rental.rental.events --partitions 3 --replication-factor 1
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic smart-rental.anomaly.events --partitions 3 --replication-factor 1
kafka-topics --bootstrap-server kafka:9092 --create --if-not-exists --topic smart-rental.recommendation.events --partitions 3 --replication-factor 1

echo "Kafka topics successfully initialized."
