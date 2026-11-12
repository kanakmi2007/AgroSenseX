/*
 ==============================================================================
  AgroSenseX (TERRAVYX) - ESP32 IoT Perimeter Defense & IR Boundary Firmware
 ==============================================================================
  कल के हार्डवेयर सेटअप के लिए पूर्ण ESP32 Arduino स्केच (Firmware):
  
  [हार्डवेयर कनेक्शन / Wiring Pinout]:
  1. IR Obstacle / Beam Sensor (KY-032 / FC-51 / E18-D80NK):
     - VCC  ---> ESP32 3.3V / 5V (Sensor के अनुसार)
     - GND  ---> ESP32 GND
     - OUT  ---> ESP32 GPIO 13 (Digital Input with Pull-up)
  
  2. Acoustic Deterrent Buzzer / 5V Relay Module (सायरन/बज़र):
     - VCC  ---> ESP32 5V (VIN)
     - GND  ---> ESP32 GND
     - IN   ---> ESP32 GPIO 12 (Digital Output)
  
  3. Status Indicator LED:
     - Built-in Blue LED ---> ESP32 GPIO 2
 ==============================================================================
*/

#include <WiFi.h>
#include <HTTPClient.h>

// ================= 1. WiFi & SERVER CONFIGURATION =================
// अपने मोबाइल हॉटस्पॉट या वाईफाई का नाम और पासवर्ड यहाँ दर्ज करें:
const char* WIFI_SSID     = "Your_WiFi_Or_Hotspot_Name";
const char* WIFI_PASSWORD = "Your_WiFi_Password";

// अपने लैपटॉप का लोकल IP एड्रेस यहाँ दर्ज करें (e.g., cmd में 'ipconfig' चलाकर IPv4 देखें):
// Example: "http://192.168.1.15:8000" या "http://10.0.0.5:8000"
const char* SERVER_BASE_URL = "http://192.168.1.100:8000";

// ================= 2. GPIO PIN DEFINITIONS =================
const int PIN_IR_SENSOR  = 13; // IR Beam Sensor Digital Output Pin
const int PIN_BUZZER     = 12; // Acoustic Buzzer / Relay Trigger Pin
const int PIN_STATUS_LED = 2;  // Built-in Status LED

// ================= 3. STATE VARIABLES =================
bool lastIrState = HIGH;           // Default HIGH when beam is intact
unsigned long lastDebounceTime = 0;
const unsigned long DEBOUNCE_DELAY = 150; // ms

unsigned long lastPollTime = 0;
const unsigned long POLL_INTERVAL = 4000; // Poll server every 4 seconds to sync status

bool isLocalBuzzerActive = false;

// ================= 4. SETUP =================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n=======================================================");
  Serial.println("  TERRAVYX / AgroSenseX - ESP32 Perimeter Node #04");
  Serial.println("  Perimeter Intrusion Detection & Deterrent System Initializing");
  Serial.println("=======================================================");

  // Pin Configurations
  pinMode(PIN_IR_SENSOR, INPUT_PULLUP);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);

  digitalWrite(PIN_BUZZER, LOW);
  digitalWrite(PIN_STATUS_LED, LOW);

  // WiFi Connection
  connectToWiFi();
}

// ================= 5. MAIN LOOP =================
void loop() {
  // Ensure WiFi remains connected
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }

  // 1. Read IR Beam Sensor
  int currentIrReading = digitalRead(PIN_IR_SENSOR);

  // Check if state changed (LOW = Object / Animal broke beam, HIGH = Clear)
  if (currentIrReading != lastIrState && (millis() - lastDebounceTime) > DEBOUNCE_DELAY) {
    lastDebounceTime = millis();
    lastIrState = currentIrReading;

    if (currentIrReading == LOW) {
      // BEAM BROKEN - Animal / Intruder Entered Perimeter!
      Serial.println("\n[ALERT] !!! IR BEAM BROKEN - INTRUSION DETECTED ON BOUNDARY !!!");
      triggerIntrusionAlarm();
    } else {
      // Beam restored
      Serial.println("[INFO] IR Beam Restored - Optical path clear.");
    }
  }

  // 2. Periodic sync with Dashboard backend (Check if farmer silenced buzzer online)
  if (millis() - lastPollTime > POLL_INTERVAL) {
    lastPollTime = millis();
    syncHardwareStateWithServer();
  }

  delay(20);
}

// ================= 6. TRIGGER LOCAL ALARM & SEND TELEMETRY =================
void triggerIntrusionAlarm() {
  // Turn on physical buzzer and blink LED
  digitalWrite(PIN_BUZZER, HIGH);
  digitalWrite(PIN_STATUS_LED, HIGH);
  isLocalBuzzerActive = true;

  // Send POST /hardware/ir-alert to FastAPI Dashboard Server
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String endpoint = String(SERVER_BASE_URL) + "/hardware/ir-alert";

    Serial.print("[HTTP] Sending Hardware Alert to: ");
    Serial.println(endpoint);

    http.begin(endpoint);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String postData = "beam_broken=true&sector=Sector 04 — North Acre";
    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      Serial.print("[HTTP] Server Response Code: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.print("[HTTP] Payload: ");
      Serial.println(response);
    } else {
      Serial.print("[HTTP] Request Error: ");
      Serial.println(http.errorToString(httpResponseCode).c_str());
    }
    http.end();
  }
}

// ================= 7. SYNC HARDWARE STATE WITH SERVER =================
void syncHardwareStateWithServer() {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  String endpoint = String(SERVER_BASE_URL) + "/hardware/status";

  http.begin(endpoint);
  int httpCode = http.GET();

  if (httpCode == HTTP_CODE_OK) {
    String payload = http.getString();

    // Check if farmer clicked "Silence Buzzer" on the web dashboard
    // If buzzer_active is false on server, turn off physical buzzer
    if (payload.indexOf("\"buzzer_active\":false") > 0 || payload.indexOf("\"buzzer_active\": false") > 0) {
      if (isLocalBuzzerActive) {
        Serial.println("[SYNC] Farmer silenced buzzer from Dashboard. Shutting off local siren.");
        digitalWrite(PIN_BUZZER, LOW);
        digitalWrite(PIN_STATUS_LED, LOW);
        isLocalBuzzerActive = false;
      }
    }
  }
  http.end();
}

// ================= 8. WIFI HELPER =================
void connectToWiFi() {
  Serial.print("[WiFi] Connecting to: ");
  Serial.println(WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 25) {
    delay(500);
    Serial.print(".");
    digitalWrite(PIN_STATUS_LED, !digitalRead(PIN_STATUS_LED)); // Blink while connecting
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WiFi] CONNECTED SUCCESSFULLY!");
    Serial.print("[WiFi] ESP32 Assigned IP Address: ");
    Serial.println(WiFi.localIP());
    digitalWrite(PIN_STATUS_LED, HIGH); // Solid ON when connected
  } else {
    Serial.println("\n[WiFi] Connection Failed. Operating in offline standalone tripwire mode.");
    digitalWrite(PIN_STATUS_LED, LOW);
  }
}
