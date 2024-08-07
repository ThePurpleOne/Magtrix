#pragma once

/**
 * PWM peripheral lib
 * Author: Jonas Stirnemann
 * Date: 08/07/2024
 *
 * Fan : https://www.delta-fan.com/Download/Spec/GFM0812DUB7S.pdf
 *
 * FAN DATASHEET : https://www.delta-fan.com/Download/Spec/GFM0812DUB7S.pdf
 *
 * PWM Example : https://forums.raspberrypi.com/viewtopic.php?t=303116
 *
 * PWM peripheral explained :
 * https://www.i-programmer.info/programming/148-hardware/14849-the-pico-in-c-basic-pwm.html?start=1
 */

#include <stdio.h>
#include <string.h>
// --
#include "hardware/clocks.h"
#include "hardware/dma.h"
#include "hardware/irq.h"
#include "hardware/pwm.h"
#include "hardware/spi.h"
#include "hardware/structs/clocks.h"
#include "hardware/structs/pll.h"
#include "pico/stdlib.h"


typedef struct
{
	uint8_t	 gpio;	 // GPIO pin
	uint32_t slice;	 // Slice number
	uint32_t chan;	 // Channel number
	uint32_t freq;	 // Frequency of the PWM signal
	float	 duty;	 // Duty cycle of the PWM signal between 0 and 1
	uint32_t wrap;	 // Value at which the counter wraps around to 0
	uint32_t div_16; // Current Clock divider
} ws_pwm_t;

#define CLK_FREQ 125000000

void ws_pwm_init_from_gpio(ws_pwm_t* pwm, uint gpio, uint freq, float duty);
void ws_pwms_init_from_gpios(uint8_t	nb_pwms,
							 ws_pwm_t** pwms,
							 uint*		gpios,
							 uint		freq,
							 uint		initial_duty);

void ws_pwm_init(ws_pwm_t* pwm, uint slice, uint chan, uint32_t freq, float initial_duty);
void ws_pwm_set_duty(ws_pwm_t* pwm, float duty);

void ws_pwm_enable(ws_pwm_t* pwm);
void ws_pwms_enable(uint8_t nb_pwms, ws_pwm_t** pwms);