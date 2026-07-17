# Assumptions & Limitations - Smart ICU Equipment Monitoring Platform

This document outlines the operational boundaries, simulated elements, and limitations of this analytics platform compared to a production medical system.

---

## 1. Simulated vs. Production Elements

To ensure transparency for interviewers and stakeholders, we explicitly demarcate the simulated aspects of this capstone project:

### A. Synthetic Timestamps
- **Simulation**: Telemetry records are mapped to hourly readings starting from `2026-01-01 00:00:00` and ending in `2027-02-21`.
- **Reality**: In a hospital setting, equipment logs are event-driven, irregular, and continuous. Ventilators upload data every few seconds during patient ventilation, while CT scanners log telemetry during patient scans. Real systems stream data via IoT protocols (like MQTT or AMQP) rather than static, uniform CSV sequences.

### B. Industrial-to-Healthcare Telemetry Reframing
- **Simulation**: Telemetry parameters (Process Temp, Rotational Speed, Torque, Tool Wear) from the AI4I Predictive Maintenance dataset are renamed to match Ventilator, CT, and MRI parameters.
- **Reality**: This mapping is conceptual. A real CT scanner sensor suite tracks parameters such as X-ray tube heat units, voltage (kV), current (mA), gantry balance, and sub-millimeter positioning. A ventilator tracks pressure, volume flow, gas mixtures, and valve wear. Real telemetry is far more complex and highly specific to the device manufacturer (e.g., GE HealthCare proprietary sensor APIs).

### C. Failure Risk Index and Health Score
- **Simulation**: The Failure Risk Index is a linear combination of normalized inputs ($30\%$ temp difference, $30\%$ torque load, $40\%$ runtime wear).
- **Reality**: These weights are **not clinically validated** or certified. They are analytical heuristics. A real-world risk engine would utilize physics-based models, specialized sensor limits, and extensive historical testing to establish safety thresholds. Clinical algorithms are highly regulated and subject to FDA certification.

---

## 2. Production Constraints & Future Ingestion Architectures

In a production clinical environment, a data engineering solution for medical equipment monitoring would need to support the following:

- **FHIR & HL7 Messaging Standards**: Medical systems communicate data via standard HL7 messages or FHIR (Fast Healthcare Interoperability Resources) APIs to ensure interoperability across hospital Electronic Health Records (EHRs) and PACS.
- **Real-Time Streaming Pipelines**: Telemetry would be ingested in real-time using streaming queues (Apache Kafka or AWS Kinesis) and processed in micro-batches (Apache Spark or Apache Flink) to detect failures instantly.
- **HIPAA and Patient Data Privacy**: Since equipment logs can sometimes be linked to patient scan events, all telemetry must undergo strict anonymization (removing HIPAA-defined Protected Health Information, or PHI) to protect patient privacy.
- **Fail-Safe High Availability**: Clinical monitoring systems must have $99.999\%$ uptime, automated failover mechanisms, and backup servers to prevent failures during critical patient operations.
