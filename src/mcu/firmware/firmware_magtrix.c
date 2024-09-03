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
#define PWM_FREQ  25000 // 25 Khz prefered in datasheet
#define NB_PWMS	  13
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

typedef struct
{
	uint8_t x;
	uint8_t y;
} coords_t;


void t_coils(void* p);
void t_serial(void* p);

static void od_gpio_down(uint gpio);
static void od_gpio_up(uint gpio);
uint8_t		read_char(void);

TaskHandle_t g_handle_serial_task_to_notify;


// ! GLOBALS
QueueHandle_t coils_queue; // Send from serial to coils task

#define PLAYER_1 true
#define PLAYER_2 false

// These are the cells at which to take the player coins
// These are hardcoded
coords_t g_starting_cells_p1[] = {
	{ 0, 0 },
	{ 0, 4 },
	{ 0, 8 },
	{ 0, 12 },
};
uint8_t index_start_p1 = 0;

coords_t g_starting_cells_p2[] = {
	{ 4, 12 },
	{ 8, 12 },
	{ 12, 12 },
};
uint8_t index_start_p2 = 0;

bool g_player_turn = PLAYER_1;

// ! FUNCTIONS
// ! PWM
int main()
{
	stdio_init_all();
	sleep_ms(2000);

	// Allocate the queue
	coils_queue = xQueueCreate(2, sizeof(coords_t));

	// ! PWM (COLS)
	mag_pwm_t pwms[NB_PWMS];
	for (uint8_t i = 0; i < NB_PWMS; i++)
	{
		mag_pwm_init_from_gpio(&pwms[i], pwms_gpios[i], PWM_FREQ, 0.0);
		mag_pwm_enable(&pwms[i]);
	}


	TaskHandle_t coils_handle;
	UBaseType_t	 coils_affinity_mask;
	coils_args_t arg_coils = { .frequency = 1, .pwms = pwms, .rows_gpios = rows_gpios };
	xTaskCreate(t_coils, "COILS", 1024 * 10, &arg_coils, 10, &coils_handle);
	coils_affinity_mask = 0x02;
	vTaskCoreAffinitySet(coils_handle, coils_affinity_mask);


	TaskHandle_t serial_handle;
	UBaseType_t	 spi_write_affinity_mask;
	task_arg	 arg_serial = { .frequency = 50 };
	xTaskCreate(t_serial, "SERIAL", 1024 * 10, &arg_serial, 1, &serial_handle);
	spi_write_affinity_mask = 0x01;
	vTaskCoreAffinitySet(serial_handle, spi_write_affinity_mask);


	g_handle_serial_task_to_notify = xTaskGetHandle("SERIAL");

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


/**
 * Start byte : 0x02
 * X coordinate : 0 to 2 in ASCII
 * Y coordinate : 0 to 2 in ASCII
 * Stop byte : 0x03
 */
void t_serial(void* p)
{
	uint8_t start_byte = 0x02;
	uint8_t stop_byte  = 0x03;
	uint8_t x, y;

	// printf("STARTED SERIAL TASK\n");
	bool	start = false;
	uint8_t c;
	while (true)
	{
		// ! Wait for the start byte
		while (!start)
		{
			c = read_char();
			if (c == start_byte)
				start = true;
		}
		start = false; // for the next iteration

		x = read_char() - 0x30;
		y = read_char() - 0x30;

		// ! Read the stop byte
		read_char();

		// Now we need to generate the actual coordinates we'll go through
		// In order to get to the right values
		// So we'll need to get determine the best path (going through the buses)

		// ! Send the coordinates to the coils task
		coords_t coords = { .x = x, .y = y };
		// coords_t coords = { .x = 1, .y = 1 };

		xQueueSend(coils_queue, &coords, portMAX_DELAY);

		uint32_t success;

		success = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

		// If = 0 -> Timed out the notification take
		while (success == 0) // Notified by task
		{
			success = ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
			// printf("Coil task finished and told serial task\n");
		}

		// printf("Coil move is over, taking hand again\n");
	}
}

void t_coils(void* p)
{
	coils_args_t* a			 = (coils_args_t*)p;
	uint64_t	  period	 = 1000 / a->frequency;
	mag_pwm_t*	  pwms		 = a->pwms;
	col_pins_t*	  rows_gpios = a->rows_gpios;
	uint8_t		  index_col	 = 0;
	uint8_t		  index_row	 = 0;
	uint8_t		  x			 = 0;
	uint8_t		  y			 = 0;
	coords_t	  goal_coords;

	coords_t path_coords[20]; // Max 20 steps
	uint8_t	 nb_steps = 0;

	// ! START ANIMATION
	// ? X
	for (uint8_t i = 0; i < NB_PWMS; i++)
		mag_pwm_set_duty(&pwms[i], 0.0);

	for (uint8_t x = 0; x < NB_PWMS; x++)
	{
		mag_pwm_set_duty(&pwms[x], 0.3);
		sleep_ms(100);
		mag_pwm_set_duty(&pwms[x], 0.0);
	}

	// ? Y
	for (uint8_t i = 0; i < NB_ROWS; i++)
		od_gpio_up(rows_gpios[i]);

	for (uint8_t y = 0; y < NB_ROWS; y++)
	{
		od_gpio_down(rows_gpios[y]);
		sleep_ms(100);
		od_gpio_up(rows_gpios[y]);
	}

	while (true)
	{
		xQueueReceive(coils_queue, &goal_coords, portMAX_DELAY);


		// ! GAME DRAWN
		if (goal_coords.x == 3)
		{
			// printf("TEST\n");
			//  Animation on the cols
			for (uint8_t i = 0; i < NB_PWMS; i++)
				mag_pwm_set_duty(&pwms[i], 0.0);

			for (uint8_t x = 0; x < NB_PWMS; x++)
			{
				mag_pwm_set_duty(&pwms[x], 0.3);
				sleep_ms(200);
				mag_pwm_set_duty(&pwms[x], 0.0);
			}

			for (uint8_t i = 0; i < NB_PWMS; i++)
				mag_pwm_set_duty(&pwms[i], 0.0);

			// Animation on the rows
			for (uint8_t i = 0; i < NB_ROWS; i++)
				od_gpio_up(rows_gpios[i]);

			for (uint8_t y = 0; y < NB_ROWS; y++)
			{
				od_gpio_down(rows_gpios[y]);
				sleep_ms(200);
				od_gpio_up(rows_gpios[y]);
			}

			for (uint8_t i = 0; i < NB_ROWS; i++)
				od_gpio_up(rows_gpios[i]);

			printf("OK\n");
			xTaskNotifyGive(g_handle_serial_task_to_notify);

			// printf("OK\n");
			// xTaskNotifyGive(g_handle_serial_task_to_notify);
		}
		else
		{
			// ! Process the x and y, to be final coil and not actual index
			// ! Because there is buses
			uint8_t x = (goal_coords.x * 4) + 4;
			uint8_t y = (goal_coords.y * 4) + 4;

			// ! Turn on the corresponding LEDs for the end goal

			// ? X
			for (uint8_t i = 0; i < NB_PWMS; i++)
				mag_pwm_set_duty(&pwms[i], 0.0);

			mag_pwm_set_duty(&pwms[x], 0.3);

			// ? Y
			for (uint8_t i = 0; i < NB_ROWS; i++)
				od_gpio_up(rows_gpios[i]);

			od_gpio_down(rows_gpios[y]);


			// 1. Find the closest bus (horizontal hard coded), closest to the goal column
			// 2. Go to closest row while still being on the bus
			// 3. Go to the goal column
			// 4. Go to goal row

			//// Create a path from start to goal
			//// ! And fill the path_coords array
			// if (g_player_turn == PLAYER_1)
			//{
			//	// ! Go to the closest bus
			//	if (x < goal_coords.x)
			//	{
			//		// ! Go to the right
			//		for (uint8_t i = x; i < goal_coords.x; i++)
			//		{
			//			path_coords[nb_steps].x = i;
			//			path_coords[nb_steps].y = y;
			//			nb_steps++;
			//		}
			//	}
			//	else
			//	{
			//		// ! Go to the left
			//		for (uint8_t i = x; i > goal_coords.x; i--)
			//		{
			//			path_coords[nb_steps].x = i;
			//			path_coords[nb_steps].y = y;
			//			nb_steps++;
			//		}
			//	}

			//	// ! Go to the closest row
			//	if (y < goal_coords.y)
			//	{
			//		// ! Go down
			//		for (uint8_t i = y; i < goal_coords.y; i++)
			//		{
			//			path_coords[nb_steps].x = goal_coords.x;
			//			path_coords[nb_steps].y = i;
			//			nb_steps++;
			//		}
			//	}
			//	else
			//	{
			//		// ! Go up
			//		for (uint8_t i = y; i > goal_coords.y; i--)
			//		{
			//			path_coords[nb_steps].x = goal_coords.x;
			//			path_coords[nb_steps].y = i;
			//			nb_steps++;
			//		}
			//	}
			//}
			// else
			//{
			//	// ! Go to the closest bus
			//	if (x < goal_coords.x)
			//	{
			//		// ! Go to the right
			//		for (uint8_t i = x; i < goal_coords.x; i++)
			//		{
			//			path_coords[nb_steps].x = i;
			//			path_coords[nb_steps].y = y;
			//			nb_steps++;
			//		}
			//	}
			//	else
			//	{
			//		// ! Go to the left
			//		for (uint8_t i = x; i > goal_coords.x; i--)
			//		{
			//			path_coords[nb_steps].x = i;
			//			path_coords[nb_steps].y = y;
			//			nb_steps++;
			//		}
			//	}

			//	// ! Go to the closest row
			//	if (y < goal_coords.y)
			//	{
			//		// ! Go down (up)
			//		for (uint8_t i = y; i < goal_coords.y; i++)
			//		{
			//			path_coords[nb_steps].x = goal_coords.x;
			//			path_coords[nb_steps].y = i;
			//			nb_steps++;
			//		}
			//	}
			//	else
			//	{
			//		// ! Go up (down)
			//		for (uint8_t i = y; i > goal_coords.y; i--)
			//		{
			//			path_coords[nb_steps].x = goal_coords.x;
			//			path_coords[nb_steps].y = i;
			//			nb_steps++;
			//		}
			//	}
			//}


			//// ! Power the row
			// for (uint8_t i = 0; i < NB_ROWS; i++)
			//	od_gpio_up(rows_gpios[i]);

			// od_gpio_down(rows_gpios[coords.y]);

			//// Turn off every coils
			// for (uint8_t i = 0; i < NB_PWMS; i++)
			//	mag_pwm_set_duty(&pwms[i], 0.0);

			//// ! Power the coil
			// mag_pwm_set_duty(&pwms[coords.x], 0.9);

			// if (index_col >= NB_PWMS - 1)
			//	index_col = NB_PWMS - 2;
			// else
			//	index_col++;

			// if (index_row >= NB_ROWS - 1)
			//	index_row = 0;
			// else
			//	index_row++;
			sleep_ms(2000);
			printf("OK\n");
			xTaskNotifyGive(g_handle_serial_task_to_notify);
		}


		// vTaskDelay(period * portTICK_PERIOD_MS);
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


uint8_t read_char(void)
{
	while (1)
	{
		uint8_t	 buf[1];
		uint32_t count = tud_cdc_read(buf, sizeof(buf));
		if (count)
			return buf[0];
		// ! This seems to be necessary in order to have the USB CDC working
		// ! It's normally sent from a timer setup by the SDK
		// ! In case it's stuck and the timer is low priority, send it by hand
		tud_task();
	}
}