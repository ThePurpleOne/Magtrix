/**
 * Shift Register library
 * Author: Jonas Stirnemann
 * Date: 15/08/2024
 *
 *
 * data_pinsheet shift register:
 * https://www.ti.com/lit/ds/symlink/sn74hcs16507.pdf?ts=1723718777444&ref_url=https%253A%252F%252Fwww.mouser.ch%252F
 */


#include "mag_sr.h"

#include "pico/stdlib.h"

#include <stdio.h>


bool mag_sr_init(mag_sr_t* sr,
				 uint8_t   data_pin,
				 uint8_t   clock_pin,
				 uint8_t   latch_pin,
				 uint8_t   en_pin)
{
	// Clock pin can only be spi0 clk
	const uint8_t possible_clk[]	  = { 2, 6, 18 };
	const uint8_t possible_data_pin[] = { 3, 7, 19 };

	// Check if the pins are valid
	bool valid = false;
	for (int i = 0; i < 3; i++)
	{
		if (possible_clk[i] == clock_pin && possible_data_pin[i] == data_pin)
		{
			valid = true;
			break;
		}
	}
	if (!valid)
	{
		printf("Invalid pins for shift register\n");
		return false;
	}


	sr->data_pin  = data_pin;
	sr->clock_pin = clock_pin;
	sr->latch_pin = latch_pin;
	sr->en_pin	  = en_pin;

	spi_init(spi0, 1000);
	spi_set_format(spi0, 16, SPI_CPOL_0, SPI_CPHA_0, SPI_MSB_FIRST);
	spi_set_slave(spi0, false);

	gpio_set_function(data_pin, GPIO_FUNC_SPI);
	gpio_set_function(clock_pin, GPIO_FUNC_SPI);

	gpio_init(latch_pin);
	gpio_set_dir(latch_pin, GPIO_OUT);

	gpio_init(en_pin);
	gpio_set_dir(en_pin, GPIO_OUT);

	return true;
}

void mag_sr_write(mag_sr_t* sr, uint16_t data)
{
	spi_write16_blocking(spi0, &data, 1);

	gpio_put(sr->latch_pin, 1);
	sleep_us(1);
	gpio_put(sr->latch_pin, 0);
}

void mag_sr_power_row(mag_sr_t* sr, uint8_t row)
{
	mag_sr_write(sr, 1 << row);
}