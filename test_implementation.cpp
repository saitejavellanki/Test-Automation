```cpp
#include <gtest/gtest.h>
#include <gmock/gmock.h>
#include <chrono>
#include <thread>
#include <future>
#include <random>
#include <algorithm>
#include <iostream>
#include <vector>
#include <memory>
#include <stdexcept>  // For std::runtime_error

// Forward declarations and defines, mimicking BLE driver interfaces and data structures

// --- Defines ---
#define BLE_SUCCESS 0
#define BLE_ERROR_INITIALIZATION_FAILED -1
#define BLE_ERROR_HCI_COMMAND_FAILED -2
#define BLE_ERROR_ACL_DATA_FAILED -3
#define BLE_ERROR_CONNECTION_FAILED -4
#define BLE_ERROR_INVALID_PARAMETER -5
#define BLE_CONTROLLER_STATUS_INITIALIZED 1
#define BLE_CONTROLLER_STATUS_UNINITIALIZED 0

// --- Data Structures ---
typedef struct {
    uint8_t addr[6];
} ble_address_t;

typedef struct {
    uint16_t connection_handle;
    // Other connection parameters
} ble_connection_t;

typedef struct {
  uint16_t service_uuid;
  //other service details
} ble_gatt_service_t;

typedef struct {
  uint16_t characteristic_uuid;
  // other characteristic details
} ble_gatt_characteristic_t;

// --- Mockable BLE Driver Interface ---
class BleDriverInterface {
public:
    virtual ~BleDriverInterface() {}
    virtual int init() = 0;
    virtual int sendHciCommand(uint16_t opcode, const uint8_t* params, uint8_t len) = 0;
    virtual int receiveHciEvent(uint8_t eventCode, const uint8_t* data, uint8_t len) = 0;
    virtual int sendAclData(uint16_t connectionHandle, const uint8_t* data, uint16_t len) = 0;
    virtual int receiveAclData(uint16_t connectionHandle, uint8_t* data, uint16_t len) = 0;
    virtual int connect(const ble_address_t& address, ble_connection_t& connection) = 0;
    virtual int disconnect(uint16_t connectionHandle) = 0;
    virtual int startAdvertising() = 0;
    virtual int stopAdvertising() = 0;
    virtual int startScanning() = 0;
    virtual int stopScanning() = 0;
    virtual int gattDiscoverServices(uint16_t connectionHandle, std::vector<ble_gatt_service_t>& services) = 0;
    virtual int gattReadCharacteristic(uint16_t connectionHandle, uint16_t characteristicHandle, uint8_t* value, uint16_t& len) = 0;
    virtual int gattWriteCharacteristic(uint16_t connectionHandle, uint16_t characteristicHandle, const uint8_t* value, uint16_t len) = 0;
    virtual int setBleAddress(const ble_address_t& address) = 0;
    virtual int getBleAddress(ble_address_t& address) = 0;
    virtual void setAdvertisingParameters(uint16_t interval, uint8_t type) = 0;
    virtual void setScanningParameters(uint16_t interval, uint16_t window) = 0;
    virtual int otaUpdateFirmware(const uint8_t* firmwareData, uint32_t firmwareSize) = 0;
    virtual int connectionParameterUpdate(uint16_t connectionHandle, uint16_t connectionInterval, uint16_t supervisionTimeout) = 0;
    virtual int getControllerStatus() = 0; // Mock ability to get controller status
    virtual bool isThreadSafe() = 0;
};

// --- Mock Class ---
class MockBleDriver : public BleDriverInterface {
public:
    MOCK_METHOD(int, init, (), (override));
    MOCK_METHOD(int, sendHciCommand, (uint16_t opcode, const uint8_t* params, uint8_t len), (override));
    MOCK_METHOD(int, receiveHciEvent, (uint8_t eventCode, const uint8_t* data, uint8_t len), (override));
    MOCK_METHOD(int, sendAclData, (uint16_t connectionHandle, const uint8_t* data, uint16_t len), (override));
    MOCK_METHOD(int, receiveAclData, (uint16_t connectionHandle, uint8_t* data, uint16_t len), (override));
    MOCK_METHOD(int, connect, (const ble_address_t& address, ble_connection_t& connection), (override));
    MOCK_METHOD(int, disconnect, (uint16_t connectionHandle), (override));
    MOCK_METHOD(int, startAdvertising, (), (override));
    MOCK_METHOD(int, stopAdvertising, (), (override));
    MOCK_METHOD(int, startScanning, (), (override));
    MOCK_METHOD(int, stopScanning, (), (override));
    MOCK_METHOD(int, gattDiscoverServices, (uint16_t connectionHandle, std::vector<ble_gatt_service_t>& services), (override));
    MOCK_METHOD(int, gattReadCharacteristic, (uint16_t connectionHandle, uint16_t characteristicHandle, uint8_t* value, uint16_t& len), (override));
    MOCK_METHOD(int, gattWriteCharacteristic, (uint16_t connectionHandle, uint16_t characteristicHandle, const uint8_t* value, uint16_t len), (override));
    MOCK_METHOD(int, setBleAddress, (const ble_address_t& address), (override));
    MOCK_METHOD(int, getBleAddress, (ble_address_t& address), (override));
    MOCK_METHOD(void, setAdvertisingParameters, (uint16_t interval, uint8_t type), (override));
    MOCK_METHOD(void, setScanningParameters, (uint16_t interval, uint16_t window), (override));
     MOCK_METHOD(int, otaUpdateFirmware, (const uint8_t* firmwareData, uint32_t firmwareSize), (override));
    MOCK_METHOD(int, connectionParameterUpdate, (uint16_t connectionHandle, uint16_t connectionInterval, uint16_t supervisionTimeout), (override));
     MOCK_METHOD(int, getControllerStatus, (), (override));
     MOCK_METHOD(bool, isThreadSafe, (), (override));
};

// --- Test Fixture ---
class BleDriverTest : public ::testing::Test {
protected:
    void SetUp() override {
        mockDriver = std::make_shared<MockBleDriver>();
    }

    void TearDown() override {
         // Reset the mock object after each test
        ::testing::Mock::VerifyAndClearExpectations(mockDriver.get());
    }

    std::shared_ptr<MockBleDriver> mockDriver;
};

// --- Test Cases ---

// FUNC-TC-001: Verify successful initialization of the BLE controller.
TEST_F(BleDriverTest, InitSuccess) {
    EXPECT_CALL(*mockDriver, init())
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, getControllerStatus())
        .Times(1)
        .WillOnce(::testing::Return(BLE_CONTROLLER_STATUS_INITIALIZED));

    ASSERT_EQ(mockDriver->init(), BLE_SUCCESS);
    ASSERT_EQ(mockDriver->getControllerStatus(), BLE_CONTROLLER_STATUS_INITIALIZED);
}

// FUNC-TC-001: Verify initialization failure
TEST_F(BleDriverTest, InitFailure) {
    EXPECT_CALL(*mockDriver, init())
        .Times(1)
        .WillOnce(::testing::Return(BLE_ERROR_INITIALIZATION_FAILED));

     EXPECT_CALL(*mockDriver, getControllerStatus())
        .Times(1)
        .WillOnce(::testing::Return(BLE_CONTROLLER_STATUS_UNINITIALIZED));


    ASSERT_EQ(mockDriver->init(), BLE_ERROR_INITIALIZATION_FAILED);
    ASSERT_EQ(mockDriver->getControllerStatus(), BLE_CONTROLLER_STATUS_UNINITIALIZED);
}

// FUNC-TC-002: Verify the driver can send HCI commands to the BLE controller.
TEST_F(BleDriverTest, SendHciCommandSuccess) {
    uint16_t opcode = 0x0C03; // HCI Reset Command
    uint8_t params[] = {0x01, 0x02, 0x03};
    uint8_t len = sizeof(params);

    EXPECT_CALL(*mockDriver, sendHciCommand(opcode, ::testing::Pointee(params[0]), len))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    ASSERT_EQ(mockDriver->sendHciCommand(opcode, params, len), BLE_SUCCESS);
}

// FUNC-TC-003: Verify the driver can receive HCI events from the BLE controller.
TEST_F(BleDriverTest, ReceiveHciEventSuccess) {
    uint8_t eventCode = 0x0E; // HCI Command Complete Event
    uint8_t data[] = {0x01, 0x00, 0x0C, 0x03, 0x00};
    uint8_t len = sizeof(data);

    EXPECT_CALL(*mockDriver, receiveHciEvent(eventCode, ::testing::Pointee(data[0]), len))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    ASSERT_EQ(mockDriver->receiveHciEvent(eventCode, data, len), BLE_SUCCESS);
}

// FUNC-TC-004: Verify the driver can send and receive ACL data packets.
TEST_F(BleDriverTest, SendAndReceiveAclDataSuccess) {
    uint16_t connectionHandle = 0x0040;
    uint8_t data[] = {0x01, 0x02, 0x03, 0x04, 0x05};
    uint16_t len = sizeof(data);

    EXPECT_CALL(*mockDriver, sendAclData(connectionHandle, ::testing::Pointee(data[0]), len))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, receiveAclData(connectionHandle, ::testing::NotNull(), len))
        .Times(1)
        .WillOnce(::testing::Invoke(
            [&](uint16_t connectionHandle, uint8_t* receivedData, uint16_t len) {
                std::copy(data, data + len, receivedData);
                return BLE_SUCCESS;
            }));

    ASSERT_EQ(mockDriver->sendAclData(connectionHandle, data, len), BLE_SUCCESS);
    uint8_t receivedData[sizeof(data)];
    ASSERT_EQ(mockDriver->receiveAclData(connectionHandle, receivedData, len), BLE_SUCCESS);
    ASSERT_THAT(receivedData, ::testing::ElementsAreArray(data));
}

// FUNC-TC-005: Verify connection management (establishing and disconnecting BLE connections).
TEST_F(BleDriverTest, ConnectAndDisconnectSuccess) {
    ble_address_t address = {{0x01, 0x02, 0x03, 0x04, 0x05, 0x06}};
    ble_connection_t connection;
    connection.connection_handle = 0x0040;

    EXPECT_CALL(*mockDriver, connect(::testing::_, ::testing::An<ble_connection_t&>()))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, disconnect(connection.connection_handle))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    ASSERT_EQ(mockDriver->connect(address, connection), BLE_SUCCESS);
    ASSERT_EQ(mockDriver->disconnect(connection.connection_handle), BLE_SUCCESS);
}

// FUNC-TC-006: Verify advertising and scanning functionalities.
TEST_F(BleDriverTest, AdvertisingAndScanningSuccess) {
    EXPECT_CALL(*mockDriver, startAdvertising())
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, stopAdvertising())
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, startScanning())
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, stopScanning())
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    ASSERT_EQ(mockDriver->startAdvertising(), BLE_SUCCESS);
    ASSERT_EQ(mockDriver->stopAdvertising(), BLE_SUCCESS);
    ASSERT_EQ(mockDriver->startScanning(), BLE_SUCCESS);
    ASSERT_EQ(mockDriver->stopScanning(), BLE_SUCCESS);
}

// FUNC-TC-007: Verify GATT client functionality (service discovery, characteristic read/write/notify).
TEST_F(BleDriverTest, GattClientFunctionalitySuccess) {
  uint16_t connectionHandle = 0x0040;
  std::vector<ble_gatt_service_t> discoveredServices;
  ble_gatt_service_t service1 = {0x1800}; // Generic Access Service UUID
  ble_gatt_service_t service2 = {0x1801}; // Generic Attribute Service UUID
  discoveredServices.push_back(service1);
  discoveredServices.push_back(service2);

  uint16_t characteristicHandle = 0x2A00; // Device Name Characteristic UUID
  uint8_t readValue[20] = {0};
  uint16_t readLen = sizeof(readValue);
  const uint8_t writeValue[] = "New Device Name";
  uint16_t writeLen = sizeof(writeValue) - 1; // Exclude null terminator

  EXPECT_CALL(*mockDriver, gattDiscoverServices(connectionHandle, ::testing::An<std::vector<ble_gatt_service_t>&>()))
    .Times(1)
    .WillOnce(::testing::Invoke(
      [&](uint16_t connectionHandle, std::vector<ble_gatt_service_t>& services) {
        services = discoveredServices;
        return BLE_SUCCESS;
      }));

  EXPECT_CALL(*mockDriver, gattReadCharacteristic(connectionHandle, characteristicHandle, ::testing::NotNull(), ::testing::An<uint16_t&>()))
    .Times(1)
    .WillOnce(::testing::Invoke(
      [&](uint16_t connectionHandle, uint16_t characteristicHandle, uint8_t* value, uint16_t& len) {
        std::string deviceName = "Test Device";
        len = std::min((size_t)len, deviceName.length());
        std::copy(deviceName.begin(), deviceName.begin() + len, value);
        return BLE_SUCCESS;
      }));

  EXPECT_CALL(*mockDriver, gattWriteCharacteristic(connectionHandle, characteristicHandle, ::testing::Pointee(writeValue[0]), writeLen))
    .Times(1)
    .WillOnce(::testing::Return(BLE_SUCCESS));

  std::vector<ble_gatt_service_t> services;
  ASSERT_EQ(mockDriver->gattDiscoverServices(connectionHandle, services), BLE_SUCCESS);
  ASSERT_EQ(services.size(), discoveredServices.size());
  ASSERT_EQ(services[0].service_uuid, discoveredServices[0].service_uuid);
  ASSERT_EQ(services[1].service_uuid, discoveredServices[1].service_uuid);

  ASSERT_EQ(mockDriver->gattReadCharacteristic(connectionHandle, characteristicHandle, readValue, readLen), BLE_SUCCESS);
  ASSERT_EQ(std::string((char*)readValue, 11), "Test Device");

  ASSERT_EQ(mockDriver->gattWriteCharacteristic(connectionHandle, characteristicHandle, writeValue, writeLen), BLE_SUCCESS);
}

// FUNC-TC-012: Verify the API for setting and getting the BLE address.
TEST_F(BleDriverTest, SetAndGetBleAddressSuccess) {
    ble_address_t setAddress = {{0x01, 0x02, 0x03, 0x04, 0x05, 0x06}};
    ble_address_t getAddress = {{0}};

    EXPECT_CALL(*mockDriver, setBleAddress(::testing::Eq(setAddress)))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, getBleAddress(::testing::An<ble_address_t&>()))
        .Times(1)
        .WillOnce(::testing::Invoke(
            [&](ble_address_t& address) {
                address = setAddress;
                return BLE_SUCCESS;
            }));

    ASSERT_EQ(mockDriver->setBleAddress(setAddress), BLE_SUCCESS);
    ASSERT_EQ(mockDriver->getBleAddress(getAddress), BLE_SUCCESS);
    ASSERT_THAT(getAddress.addr, ::testing::ElementsAreArray(setAddress.addr));
}

// FUNC-TC-014: Verify the API for configuring advertising parameters.
TEST_F(BleDriverTest, SetAdvertisingParametersSuccess) {
    uint16_t interval = 100;
    uint8_t type = 0x05;

    EXPECT_CALL(*mockDriver, setAdvertisingParameters(interval, type))
        .Times(1);

    mockDriver->setAdvertisingParameters(interval, type);
}

// FUNC-TC-017: Verify Over-The-Air (OTA) firmware updates.
TEST_F(BleDriverTest, OtaUpdateFirmwareSuccess) {
    std::vector<uint8_t> firmwareData = {0x01, 0x02, 0x03, 0x04, 0x05};
    uint32_t firmwareSize = firmwareData.size();
    const uint8_t* firmwarePtr = firmwareData.data();

    EXPECT_CALL(*mockDriver, otaUpdateFirmware(::testing::Pointee(firmwareData[0]), firmwareSize))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    ASSERT_EQ(mockDriver->otaUpdateFirmware(firmwarePtr, firmwareSize), BLE_SUCCESS);
}

//FUNC-TC-018: Verify Connection Parameter Update procedure
TEST_F(BleDriverTest, ConnectionParameterUpdateSuccess) {
    uint16_t connectionHandle = 0x0040;
    uint16_t connectionInterval = 50;
    uint16_t supervisionTimeout = 200;

    EXPECT_CALL(*mockDriver, connectionParameterUpdate(connectionHandle, connectionInterval, supervisionTimeout))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    ASSERT_EQ(mockDriver->connectionParameterUpdate(connectionHandle, connectionInterval, supervisionTimeout), BLE_SUCCESS);
}

// INTF-TC-003: Verify the mechanism for registering callback functions for handling HCI events and ACL data.
// This test requires a more complex setup with actual callbacks, which is difficult to represent in a pure mock test.

// PERF-TC-001: Verify BLE connection establishment time.
TEST_F(BleDriverTest, ConnectionEstablishmentTime) {
    ble_address_t address = {{0x01, 0x02, 0x03, 0x04, 0x05, 0x06}};
    ble_connection_t connection;
    connection.connection_handle = 0x0040;

    EXPECT_CALL(*mockDriver, connect(::testing::_, ::testing::An<ble_connection_t&>()))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    auto startTime = std::chrono::high_resolution_clock::now();
    ASSERT_EQ(mockDriver->connect(address, connection), BLE_SUCCESS);
    auto endTime = std::chrono::high_resolution_clock::now();

    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime).count();
    std::cout << "Connection establishment time: " << duration << " ms" << std::endl;
    ASSERT_LE(duration, 100);
}

// ERR-TC-001: Verify error detection and handling during BLE controller initialization.
TEST_F(BleDriverTest, InitErrorHandling) {
    EXPECT_CALL(*mockDriver, init())
        .Times(1)
        .WillOnce(::testing::Return(BLE_ERROR_INITIALIZATION_FAILED));

    ASSERT_EQ(mockDriver->init(), BLE_ERROR_INITIALIZATION_FAILED);
}

// SAFE-TC-001: The driver shall not cause a system crash or data corruption in case of unexpected errors.
// This requires more elaborate fault injection and system monitoring, which is beyond the scope of simple unit tests.

// PWR-TC-001: The driver shall support low-power modes (e.g., sleep, deep sleep) to minimize power consumption when idle.
// This requires power measurement equipment and specific hardware support.

// --- Parameterized Tests ---
// Example: Testing different advertising intervals
class AdvertisingIntervalTest : public BleDriverTest, public ::testing::WithParamInterface<uint16_t> {
};

TEST_P(AdvertisingIntervalTest, SetValidAdvertisingInterval) {
    uint16_t interval = GetParam();
    uint8_t type = 0x00; // Default advertising type

    EXPECT_CALL(*mockDriver, setAdvertisingParameters(interval, type))
        .Times(1);

    mockDriver->setAdvertisingParameters(interval, type);
}

INSTANTIATE_TEST_SUITE_P(
    AdvertisingIntervals,
    AdvertisingIntervalTest,
    ::testing::Values(100, 200, 500, 1000) // Different advertising intervals in ms
);

// --- Thread Safety Test ---
TEST_F(BleDriverTest, ThreadSafety) {
    EXPECT_CALL(*mockDriver, isThreadSafe())
        .Times(1)
        .WillOnce(::testing::Return(true));

    if (!mockDriver->isThreadSafe()) {
        GTEST_SKIP() << "Driver is not thread-safe, skipping thread safety test.";
    }

    // Simulate concurrent access to the driver
    std::future<int> future1 = std::async(std::launch::async, [&]() {
        return mockDriver->startAdvertising();
    });

    std::future<int> future2 = std::async(std::launch::async, [&]() {
        ble_address_t address = {{0x01, 0x02, 0x03, 0x04, 0x05, 0x06}};
        ble_connection_t connection;
        return mockDriver->connect(address, connection);
    });

    // Wait for the tasks to complete
    int result1 = future1.get();
    int result2 = future2.get();

    // Add assertions based on the expected behavior
    ASSERT_EQ(result1, BLE_SUCCESS); // Or expected error code
    ASSERT_EQ(result2, BLE_SUCCESS); // Or expected error code

}

// --- Error Injection Test ---
TEST_F(BleDriverTest, ErrorInjection) {
    // Simulate an error during HCI command sending
    EXPECT_CALL(*mockDriver, sendHciCommand(::testing::_, ::testing::_, ::testing::_))
        .Times(1)
        .WillOnce(::testing::Return(BLE_ERROR_HCI_COMMAND_FAILED));

    uint16_t opcode = 0x0C03; // HCI Reset Command
    uint8_t params[] = {0x01, 0x02, 0x03};
    uint8_t len = sizeof(params);

    ASSERT_EQ(mockDriver->sendHciCommand(opcode, params, len), BLE_ERROR_HCI_COMMAND_FAILED);

    // Verify that the error is handled appropriately (e.g., retry mechanism, error reporting)
    // This may involve additional mock calls to verify the error handling logic
}

// Helper function for generating random data
std::vector<uint8_t> generateRandomData(size_t size) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> distrib(0, 255);

    std::vector<uint8_t> data(size);
    std::generate(data.begin(), data.end(), [&]() { return distrib(gen); });
    return data;
}

// Hardware Requirements Tests
TEST_F(BleDriverTest, HW_004_DMA_Transfer) {
    //Simulate DMA transfer and verify data integrity.
    uint16_t connectionHandle = 0x0040;
    std::vector<uint8_t> data = generateRandomData(1024); // Simulate a larger data packet
    uint16_t len = data.size();

    EXPECT_CALL(*mockDriver, sendAclData(connectionHandle, ::testing::Pointee(data[0]), len))
        .Times(1)
        .WillOnce(::testing::Return(BLE_SUCCESS));

    EXPECT_CALL(*mockDriver, receiveAclData(connectionHandle, ::testing::NotNull(), len))
        .Times(1)
        .WillOnce(::testing::Invoke(
            [&](uint16_t connectionHandle, uint8_t* receivedData, uint16_t len) {
                std::copy(data.begin(), data.end(), receivedData);
                return BLE_SUCCESS;
            }));

    ASSERT_EQ(mockDriver->sendAclData(connectionHandle, data.data(), len), BLE_SUCCESS);
    std::vector<uint8_t> receivedData(len);
    ASSERT_EQ(mockDriver->receiveAclData(connectionHandle, receivedData.data(), len), BLE_SUCCESS);
    ASSERT_THAT(receivedData, ::testing::ElementsAreArray(data));
}

TEST_F(BleDriverTest, HW_011_ThreadSafetyInRTOS) {
    EXPECT_CALL(*mockDriver, isThreadSafe())
        .Times(1)
        .WillOnce(::testing::Return(true));

    if (!mockDriver->isThreadSafe()) {
        GTEST_SKIP() << "Driver is not thread-safe, skipping RTOS thread safety test.";
    }

    // Simulate multiple threads accessing the driver concurrently
    std::vector<std::future<int>> futures;
    for (int i = 0; i < 5; ++i) {
        futures.push_back(std::async(std::launch::async, [&]() {
            ble_address_t address = {{0x01, 0x02, 0x03, 0x04, 0x05, 0x06}};
            ble_connection_t connection;
            return mockDriver->connect(address, connection);
        }));
    }

    // Wait for all threads to complete and check results
    for (auto& future : futures) {
        ASSERT_EQ(future.get(), BLE_SUCCESS);
    }
}

TEST_F(BleDriverTest, ERR_013_OTA_RevertOnFailure) {
    std::vector<uint8_t> firmwareData = {0x01, 0x02, 0x03, 0x04, 0x05};
    uint32_t firmwareSize = firmwareData.size();
    const uint8_t* firmwarePtr = firmwareData.data();

    // Simulate an error during OTA update
    EXPECT_CALL(*mockDriver, otaUpdateFirmware(::testing::Pointee(firmwareData[0]), firmwareSize))
        .Times(1)
        .WillOnce(::testing::Return(BLE_ERROR_HCI_COMMAND_FAILED)); // Simulate OTA failure

    // Expect the driver to attempt to revert to the last known good firmware
    // This could involve additional mock calls to a "revertFirmware" function, which are not included here for brevity.

    ASSERT_EQ(mockDriver->otaUpdateFirmware(firmwarePtr, firmwareSize), BLE_ERROR_HCI_COMMAND_FAILED);

    // Add assertions to verify that the driver attempts to revert to the last known good firmware version
    // For example, verify that a "revertFirmware" function is called.
}
```