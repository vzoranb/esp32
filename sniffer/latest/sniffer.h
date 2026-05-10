#include "esphome.h"
#include <esp_wifi.h>
#include <esp_event.h>
#include <esp_netif.h>
#include <esp_log.h>
#include <string.h>

static const char *TAG = "mac_sniffer";
static const uint8_t TARGET_MAC[6] = {0xdc, 0xe5, 0x5b, 0x06, 0x5b, 0xf9};

static uint8_t current_channel = 1;

static void promiscuous_rx_cb(void *buf, wifi_promiscuous_pkt_type_t type) {
  wifi_promiscuous_pkt_t *pkt = (wifi_promiscuous_pkt_t *)buf;
  
  // Ensure the packet is at least long enough to contain the 802.11 MAC headers (16 bytes)
  if (pkt->rx_ctrl.sig_len < 16) return;

  uint8_t *payload = pkt->payload;
  uint8_t *addr1 = &payload[4];  // Receiver Address (RA) / Destination
  uint8_t *addr2 = &payload[10]; // Transmitter Address (TA) / Source

  // Check if the packet was sent TO or FROM the target phone
  if (memcmp(addr1, TARGET_MAC, 6) == 0 || memcmp(addr2, TARGET_MAC, 6) == 0) {
    int8_t rssi = pkt->rx_ctrl.rssi;
    ESP_LOGI("SNIFFER", "TARGET_DETECTED:%02X:%02X:%02X:%02X:%02X:%02X|RSSI:%d", 
             TARGET_MAC[0], TARGET_MAC[1], TARGET_MAC[2], TARGET_MAC[3], TARGET_MAC[4], TARGET_MAC[5], rssi);
  }
}

void sniffer_setup() {
  ESP_LOGI(TAG, "Setting up MAC Sniffer for Pixel 6 Pro...");

  esp_netif_init();
  esp_event_loop_create_default();

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  esp_err_t err = esp_wifi_init(&cfg);
  if (err != ESP_OK) {
      ESP_LOGE(TAG, "esp_wifi_init failed: %s", esp_err_to_name(err));
      return;
  }
  
  esp_wifi_set_storage(WIFI_STORAGE_RAM);
  esp_wifi_set_mode(WIFI_MODE_NULL);
  esp_wifi_start();

  esp_wifi_set_promiscuous_rx_cb(&promiscuous_rx_cb);
  esp_wifi_set_promiscuous(true);
  
  ESP_LOGI(TAG, "MAC Sniffer Setup Complete! Hopping channels...");
}

void sniffer_loop() {
  current_channel++;
  if (current_channel > 11) {
    current_channel = 1;
  }
  esp_wifi_set_channel(current_channel, WIFI_SECOND_CHAN_NONE);
}

void sniffer_heartbeat() {
  ESP_LOGI(TAG, "Heartbeat: Sniffer active on channel %d", current_channel);
}
