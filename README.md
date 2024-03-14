# Smart Classroom Ventilation System

## Overview
The Smart Classroom Ventilation System is an IoT-based solution designed to monitor and regulate indoor air quality in classrooms in real-time. By leveraging sensors and IoT technology, the system aims to create safer and healthier learning environments, particularly in response to the heightened awareness of airborne diseases such as COVID-19 and seasonal flu.

## Features
- Monitors temperature, humidity, eCO2 (carbon dioxide equivalent), and TVOCs (total volatile organic compounds) levels.
- Alerts teachers when sensor values exceed predefined thresholds, indicating potential air quality concerns.
- Allows manual control of ventilation settings via a desktop application installed on teachers' computers.
- Provides real-time visualization of sensor data and status updates.

## Components
The system consists of the following components:
- Air quality sensor: Measures eCO2 and TVOCs levels.
- DHT sensor: Measures temperature and humidity.
- Relay sensor: Controls the opening and closing of windows based on manual input or sensor readings.
- Teacher Dashboard: Desktop application for monitoring sensor data and controlling ventilation settings.


## Usage
1. Run the MQTT broker server.
2. Run the teacher dashboard application on teachers' computers.
3. Ensure sensors are properly connected and publishing data to the MQTT broker.
4. Monitor sensor readings and ventilation status on the teacher dashboard.
5. Manually control ventilation settings as needed.
