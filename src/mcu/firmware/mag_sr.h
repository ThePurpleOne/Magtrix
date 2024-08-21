/**
 * Shift Register library
 * Author: Jonas Stirnemann
 * Date: 15/08/2024
 *
 *
 * Datasheet shift register:
 * https://www.ti.com/lit/ds/symlink/sn74hcs16507.pdf?ts=1723718777444&ref_url=https%253A%252F%252Fwww.mouser.ch%252F
 */

#pragma once

#include "hardware/spi.h"
#include "pico/stdlib.h"

#include <stdbool.h>
#include <stdint.h>


// mag_sr_t
typedef struct
{
	uint8_t data_pin;
	uint8_t clock_pin;
	uint8_t latch_pin;
	uint8_t en_pin;
} mag_sr_t;

bool mag_sr_init(mag_sr_t* sr,
				 uint8_t   data_pin,
				 uint8_t   clock_pin,
				 uint8_t   latch_pin,
				 uint8_t   en_pin);

void mag_sr_write(mag_sr_t* sr, uint16_t data);
void mag_sr_power_row(mag_sr_t* sr, uint8_t row);