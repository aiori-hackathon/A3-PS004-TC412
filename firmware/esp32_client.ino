#include <WiFi.h>

const char* ssid = "NEXORA_iPhone";

// Enter the real password only in your local Arduino IDE.
const char* password = "YOUR_HOTSPOT_PASSWORD";

const char* serverIP = "172.20.10.2";
const uint16_t serverPort = 5050;

WiFiClient client;

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.println("Connecting to NEXORA network...");

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(1000);
    Serial.print(".");
    attempts++;
  }

  Serial.println();

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi connection failed!");
    return;
  }

  Serial.println("Wi-Fi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  if (client.connect(serverIP, serverPort)) {
    Serial.println("Connected to laptop!");

    client.println("Hey laptop! NEXORA is online!");

    Serial.println("Message sent successfully!");

    unsigned long start = millis();

    while (!client.available() &&
           millis() - start < 5000) {
      delay(10);
    }

    if (client.available()) {
      String reply = client.readStringUntil('\n');

      Serial.print("Laptop replied: ");
      Serial.println(reply);
    } else {
      Serial.println("No reply received.");
    }

    client.stop();
  } else {
    Serial.println("Laptop connection failed!");
  }
}

void loop() {
}
