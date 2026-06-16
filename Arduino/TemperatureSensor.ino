#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <DHT.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

// DHT setup
#define DHTPIN  A0     // change if needed
#define DHTTYPE DHT11    // or DHT22 if you're using that

DHT dht(DHTPIN, DHTTYPE);

// Your name
const char* candidateName = "ESTHER KALIZA";

// timing
unsigned long lastRead = 0;
unsigned long lastScroll = 0;
unsigned long lastSerial = 0;

const unsigned long readInterval = 2000;   // DHT needs slower reading
const unsigned long scrollInterval = 400;
const unsigned long serialInterval = 2000;

float currentTemp = 0;
float currentHum = 0;

int scrollPos = 0;

void setup() {
  lcd.init();
  lcd.backlight();

  Serial.begin(9600);

  dht.begin();

  lcd.clear();
}

void loop() {
  unsigned long now = millis();

  // 🌡️ Read DHT sensor
  if (now - lastRead >= readInterval) {
    lastRead = now;

    float temp = dht.readTemperature();
    float hum = dht.readHumidity();

    // check if reading failed
    if (isnan(temp) || isnan(hum)) {
      lcd.setCursor(0, 1);
      lcd.print("Sensor Error   ");
      return;
    }

    currentTemp = temp;
    currentHum = hum;

    // display temperature
    lcd.setCursor(0, 1);
    lcd.print("T:");
    lcd.print(currentTemp, 1);
    lcd.print((char)223);
    lcd.print("C ");

    lcd.print("H:");
    lcd.print(currentHum, 0);
    lcd.print("%   ");
  }

  // 🔁 scroll name
  if (now - lastScroll >= scrollInterval) {
    lastScroll = now;
    displayName();
  }

  // 📡 send to serial (for your frontend)
  if (now - lastSerial >= serialInterval) {
    lastSerial = now;

    Serial.print("TEMP:");
    Serial.print(currentTemp, 1);
    Serial.print(",HUM:");
    Serial.println(currentHum, 1);
  }
}

// 📝 scrolling name function
void displayName() {
  String name = String(candidateName);

  lcd.setCursor(0, 0);

  if (name.length() <= 16) {
    lcd.print(name);
    for (int i = name.length(); i < 16; i++) lcd.print(" ");
    return;
  }

  String scrollText = name + "   ";
  String window = "";

  for (int i = 0; i < 16; i++) {
    window += scrollText[(scrollPos + i) % scrollText.length()];
  }

  lcd.print(window);

  scrollPos++;
  if (scrollPos >= scrollText.length()) scrollPos = 0;
}