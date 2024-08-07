cmake_minimum_required(VERSION 3.12)

include($ENV{PICO_SDK_PATH}/external/pico_sdk_import.cmake)

# Set project name
set(PROJECT_NAME PNC_ETHERNET_RP2040)
project(${PROJECT_NAME} C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

include(${PICO_SDK_PATH}/pico_sdk_init.cmake)

# Initialize the SDK
pico_sdk_init()

set(TARGET_NAME firmware_magtrix)

add_executable(${TARGET_NAME} firmware_magtrix.c)

target_include_directories(firmware_magtrix PRIVATE ${CMAKE_CURRENT_LIST_DIR})

include(FreeRTOS-Kernel/portable/ThirdParty/GCC/RP2040/FreeRTOS_Kernel_import.cmake)

target_include_directories(${TARGET_NAME} PRIVATE
		)


# Link FreeRTOS and other required libraries
target_link_libraries(firmware_magtrix
    pico_stdlib
	hardware_spi
	hardware_pio
	hardware_dma
	hardware_adc
	hardware_pwm
	hardware_irq
	hardware_timer
    FreeRTOS-Kernel 
	FreeRTOS-Kernel-Heap4
)


target_compile_definitions(
	firmware_magtrix PUBLIC
	PICO_XOSC_STARTUP_DELAY_MULTIPLIER=128
)

add_compile_options(
        -Wall
		-Wextra
)

pico_enable_stdio_usb(${TARGET_NAME} 1)
pico_enable_stdio_uart(${TARGET_NAME} 0)

pico_add_extra_outputs(${TARGET_NAME})
