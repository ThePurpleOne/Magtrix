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

// ! PWM GENERATORS
#define PWM_FREQ 25000 // 25 Khz prefered in datasheet
// #define NB_PWMS	  13
#define NB_PWMS	  6
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
// const PWM_PINS pwms_gpios[NB_PWMS] = { PWM_0, PWM_1, PWM_2, PWM_3,	PWM_4,	PWM_5, PWM_6,
//									   PWM_7, PWM_8, PWM_9, PWM_10, PWM_11, PWM_12 };
const PWM_PINS pwms_gpios[NB_PWMS] = { PWM_0, PWM_1, PWM_2, PWM_3, PWM_4, PWM_5 };


#define NB_ROWS 12
typedef enum
{
	ROW_0  = 16,
	ROW_1  = 17,
	ROW_2  = 24,
	ROW_3  = 25,
	ROW_4  = 26,
	ROW_5  = 27,
	ROW_6  = 28,
	ROW_7  = 29,
	ROW_8  = 18,
	ROW_9  = 19,
	ROW_10 = 21,
	ROW_11 = 23
} col_pins_t;
col_pins_t rows_gpios[NB_ROWS]
  = { ROW_0, ROW_1, ROW_2, ROW_3, ROW_4, ROW_5, ROW_6, ROW_7, ROW_8, ROW_9, ROW_10, ROW_11 };


// ! TASKS
typedef struct
{
	int frequency; // Hz
} task_arg;


typedef struct
{
	int			frequency; // Hz
	mag_pwm_t*	pwms;
	col_pins_t* rows_gpios;
} coils_args_t;


void t_debug(void* p);
void t_coils(void* p);

static void od_gpio_down(uint gpio);
static void od_gpio_up(uint gpio);

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

	//// ! SET GPIOS HIGH (transistors disabled)
	// for (uint8_t i = 0; i < NB_ROWS; i++)
	//	od_gpio_up(rows_gpios[i]);


	TaskHandle_t coils_handle;
	UBaseType_t	 coils_affinity_mask;
	coils_args_t arg_coils = { .frequency = 1, .pwms = pwms, .rows_gpios = rows_gpios };
	xTaskCreate(t_coils, "COILS", 1024 * 10, &arg_coils, 10, &coils_handle);
	coils_affinity_mask = 0x02;
	vTaskCoreAffinitySet(coils_handle, coils_affinity_mask);


	// TaskHandle_t debug_handle;
	// UBaseType_t	 spi_write_affinity_mask;
	// task_arg	 arg_debug = { .frequency = 50 };
	// xTaskCreate(t_debug, "DEBUG", 512, &arg_debug, 1, &debug_handle);
	// spi_write_affinity_mask = 0x01;
	// vTaskCoreAffinitySet(debug_handle, spi_write_affinity_mask);


	vTaskStartScheduler();

	while (true)
		;
}

// Stack overflow hook
void vApplicationStackOverflowHook(TaskHandle_t xTask, char* pcTaskName)
{
	(void)xTask;
	(void)pcTaskName;
	printf("Stack overflow in task %s\n", pcTaskName);
}

// Malloc failed hook
void vApplicationMallocFailedHook(void)
{
	gpio_put(LED_STATUS_PIN, 1);
	printf("Malloc failed\n");
}


void t_coils(void* p)
{
	coils_args_t* a			 = (coils_args_t*)p;
	uint64_t	  period	 = 1000 / a->frequency;
	mag_pwm_t*	  pwms		 = a->pwms;
	col_pins_t*	  rows_gpios = a->rows_gpios;
	uint8_t		  index_col	 = 0;
	uint8_t		  index_row	 = 0;
	bool		  flag		 = false;

	while (true)
	{
		// ! Power the row
		// for (uint8_t i = 0; i < NB_ROWS; i++)
		//	od_gpio_up(rows_gpios[i]);

		// od_gpio_down(rows_gpios[0]);

		// Turn off every coils
		for (uint8_t i = 0; i < NB_PWMS; i++)
			mag_pwm_set_duty(&pwms[i], 0.0);

		// ! Power the coil
		mag_pwm_set_duty(&pwms[index_col], 0.9);

		printf("TURNING ON COIL %d\n", index_col);

		if (flag)
		{
			if (index_col >= NB_PWMS - 1)
			{
				index_col = NB_PWMS - 2;
				flag	  = false;
			}
			else
			{
				index_col++;
			}
		}
		else
		{
			if (index_col <= 0)
			{
				index_col = 1;
				flag	  = true;
			}
			else
			{
				index_col--;
			}
		}


		// if (index_row >= NB_ROWS - 1)
		//	index_row = 0;
		// else
		//	index_row++;

		vTaskDelay(period * portTICK_PERIOD_MS);

		// printf("t_coils : core %d\n", get_core_num());
	}
}


static void od_gpio_down(uint gpio)
{
	// Set the GPIO as output
	gpio_init(gpio);
	gpio_set_dir(gpio, GPIO_OUT);
	gpio_put(gpio, 0);
}

/**
 * There is no open drain mode
 * on the RP2040 so we just set the GPIO as input
 * to simulate the open drain mode
 */
static void od_gpio_up(uint gpio)
{
	// ? Set the GPIO as input
	gpio_init(gpio);
	gpio_set_dir(gpio, GPIO_IN);

	// ? disable the pulls
	gpio_set_pulls(gpio, false, false);
}