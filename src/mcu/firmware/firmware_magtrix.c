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
#include "mag_sr.h"
#include "queue.h"
#include "task.h"
// ---


#define LED_STATUS_PIN 25

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
} PWM_PINS;
const PWM_PINS pwms_gpios[NB_PWMS]
  = { PWM_0, PWM_1, PWM_2, PWM_3, PWM_4, PWM_5, PWM_6, PWM_7, PWM_8, PWM_9, PWM_10, PWM_11 };


// ! SHIFT REGISTER
#define SR_DATA_PIN	  19
#define SR_CLOCK_PIN  18
#define SR_LATCH_PIN  17
#define SR_ENABLE_PIN 21

// ! TASKS
typedef struct
{
	int frequency; // Hz
} task_arg;

typedef struct
{
	int		  frequency; // Hz
	mag_sr_t* shift_register;
} sr_args_t;

typedef struct
{
	int		   frequency; // Hz
	mag_pwm_t* pwms;
} blink_args_t;


void t_debug(void* p);
void t_blink(void* p);
void t_shift_register(void* p);

// ! FUNCTIONS
// ! PWM
int main()
{
	stdio_init_all();
	sleep_ms(2000);

	// ! PWM (COLS)
	mag_pwm_t pwms[NB_PWMS];
	for (uint8_t i = 0; i < NB_PWMS; i++)
	{
		mag_pwm_init_from_gpio(&pwms[i], pwms_gpios[i], PWM_FREQ, 0.0);
		mag_pwm_enable(&pwms[i]);
	}

	// ! SHIFT REGISTER (ROWS)
	mag_sr_t sr;
	bool	 ret;
	ret = mag_sr_init(&sr, SR_DATA_PIN, SR_CLOCK_PIN, SR_LATCH_PIN, SR_ENABLE_PIN);
	if (!ret)
	{
		while (1)
		{
			printf("Error initializing shift register\n");
			sleep_ms(1000);
		}
	}


	TaskHandle_t debug_handle;
	UBaseType_t	 spi_write_affinity_mask;
	task_arg	 arg_debug = { .frequency = 50 };
	xTaskCreate(t_debug, "DEBUG", 512, &arg_debug, 1, &debug_handle);
	spi_write_affinity_mask = 0x01;
	vTaskCoreAffinitySet(debug_handle, spi_write_affinity_mask);


	TaskHandle_t sr_handle;
	UBaseType_t	 sr_affinity_mask;
	sr_args_t	 arg_sr = { .frequency = 1, .shift_register = &sr };
	xTaskCreate(t_shift_register, "SHIFT", 512, &arg_sr, 5, &sr_handle);
	sr_affinity_mask = 0x01;
	vTaskCoreAffinitySet(sr_handle, sr_affinity_mask);

	TaskHandle_t blink_handle;
	UBaseType_t	 blink_affinity_mask;
	blink_args_t arg_blink = { .frequency = 5, .pwms = pwms };
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
 */
void t_debug(void* p)
{
	task_arg* a		 = (task_arg*)p;
	uint64_t  period = 1000 / a->frequency;

	while (true)
	{
		printf("t_debug : core %d\n", get_core_num());
		vTaskDelay(period * portTICK_PERIOD_MS);
	}
}

void t_shift_register(void* p)
{
	sr_args_t* a	  = (sr_args_t*)p;
	uint64_t   period = 1000 / a->frequency;
	mag_sr_t*  sr	  = a->shift_register; 

	while (true)
	{
		mag_sr_write(sr, 0x5555);
		printf("t_shift_register : core %d\n", get_core_num());
		vTaskDelay(period * portTICK_PERIOD_MS);
	}
}

void t_blink(void* p)
{
	blink_args_t* a		 = (blink_args_t*)p;
	uint64_t	  period = 1000 / a->frequency;
	mag_pwm_t*	  pwms	 = a->pwms;

	// ! Setup PWM
	mag_pwm_enable(pwms);

	while (true)
	{
		for (uint8_t i = 0; i < NB_PWMS; i++)
			mag_pwm_set_duty(&pwms[i], 0.1 * (i + 1));
		vTaskDelay(period * portTICK_PERIOD_MS);
		for (uint8_t i = 0; i < NB_PWMS; i++)
			mag_pwm_set_duty(&pwms[i], 0.0);
		vTaskDelay(period * portTICK_PERIOD_MS);
		printf("t_blink : core %d\n", get_core_num());
	}
}
