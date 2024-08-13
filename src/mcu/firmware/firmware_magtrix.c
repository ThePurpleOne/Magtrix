/**
 * Magtrix firmware
 * Author: Jonas Stirnemann

 * Date: 26/07/2024
 *
 *
 * These is the full firmware to put on the RP2040 Edge A and B
 * The firmware of the RP edge C is different and is in another file
 *
 *
 * Source for SMP support (Important docs too)
 * https://github.com/Evlers/pico-freertos/tree/master

 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <tusb.h>

// ---
#include "FreeRTOSConfig.h"
// ---
#include "hardware/clocks.h"
#include "hardware/dma.h"
#include "hardware/irq.h"
#include "hardware/pio.h"
#include "hardware/spi.h"
#include "hardware/structs/clocks.h"
#include "hardware/structs/pll.h"
#include "pico/binary_info.h"
#include "pico/stdlib.h"
// ---
#include "FreeRTOS.h"
#include "mag_pwm.h"
#include "queue.h"
#include "task.h"
// ---


#define LED_STATUS_PIN 25


// ! TASKS
typedef struct
{
	int frequency; // Hz
} task_arg;

typedef struct
{
	int		  frequency; // Hz
	ws_pwm_t* led_pwm;
} blilnk_args_t;


void t_debug(void* p);
void t_blink(void* p);

// ! FUNCTIONS
// ! PWM GENERATORS
#define PWM_FREQ  25000 // 25 Khz prefered in datasheet
#define NB_PWMS	  12
#define BASE_DUTY 0.0
typedef enum
{
	PWM_0  = 0,
	PWM_1  = 1,
	PWM_2  = 2,
	PWM_3  = 3,
	PWM_4  = 4,
	PWM_5  = 5,
	PWM_6  = 6,
	PWM_7  = 7,
	PWM_8  = 8,
	PWM_9  = 9,
	PWM_10 = 10,
	PWM_11 = 11,
	PWM_12 = 12,
} PWM_PINS;
const PWM_PINS pwms_gpios[NB_PWMS] = { PWM_0, PWM_1, PWM_2, PWM_3,	PWM_4,	PWM_5, PWM_6,
									   PWM_7, PWM_8, PWM_9, PWM_10, PWM_11, PWM_12 };
float		   g_duties[NB_PWMS]   = { 0.0 };
ws_pwm_t	   g_pwms[NB_PWMS];

int main()
{
	stdio_init_all();
	sleep_ms(2000);

	// Setup every pwm
	ws_pwms_init_from_gpios(NB_PWMS, &g_pwms, (uint*)pwms_gpios, PWM_FREQ, 0);

	TaskHandle_t debug_handle;
	UBaseType_t	 spi_write_affinity_mask;
	task_arg	 arg_debug = { .frequency = 50 };
	xTaskCreate(t_debug, "DEBUG", 512, &arg_debug, 2, &debug_handle);
	spi_write_affinity_mask = 0x01;
	vTaskCoreAffinitySet(debug_handle, spi_write_affinity_mask);

	TaskHandle_t  blink_handle;
	UBaseType_t	  blink_affinity_mask;
	blilnk_args_t arg_blink = { .frequency = 50, .led_pwm = &led_pwm };
	xTaskCreate(t_blink, "BLINK", 1024, &arg_blink, 10, &blink_handle);
	blink_affinity_mask = 0x02;
	vTaskCoreAffinitySet(blink_handle, blink_affinity_mask);

	vTaskStartScheduler();

	while (true)
		;
}

// Stack overflow hook
void vApplicationStackOverflowHook(TaskHandle_t xTask, char* pcTaskName)
{
	(void)xTask;
	(void)pcTaskName;

	gpio_put(LED_STATUS_PIN, 1);
	configASSERT(0);
}

// Malloc failed hook
void vApplicationMallocFailedHook(void)
{
	gpio_put(LED_STATUS_PIN, 1);
	configASSERT(0);
}

/**
 * @brief Just printing some debugging informations
 *
 */
void t_debug(void* p)
{
	task_arg* a		 = (task_arg*)p;
	uint64_t  period = 1000 / a->frequency;

	while (true)
	{
		printf("Hello from core %d\n", get_core_num());
		vTaskDelay(period * portTICK_PERIOD_MS);
	}
}

void t_blink(void* p)
{
	blilnk_args_t* a	   = (blilnk_args_t*)p;
	uint64_t	   period  = 1000 / a->frequency;
	ws_pwm_t*	   led_pwm = a->led_pwm;

	// ! Setup PWM
	ws_pwm_enable(led_pwm);

	while (true)
	{
		ws_pwm_set_duty(led_pwm, 0.5);
		vTaskDelay(period * portTICK_PERIOD_MS);
		ws_pwm_set_duty(led_pwm, 0);
		vTaskDelay(period * portTICK_PERIOD_MS);
		printf("Hello from core %d\n", get_core_num());
	}
}
