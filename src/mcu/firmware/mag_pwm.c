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


// ! NOTE : The PWM slices all have 2 channels, every channels of each slice can only have the same
// frequency but can have different duty cycles

#include "mag_pwm.h"


void ws_pwms_init_from_gpios(uint8_t	nb_pwms,
							 ws_pwm_t** pwms,
							 uint*		gpios,
							 uint		freq,
							 uint		initial_duty)
{
	for (int i = 0; i < nb_pwms; i++)
		ws_pwm_init_from_gpio(pwms[i], gpios[i], freq, initial_duty);
}

void ws_pwm_init_from_gpio(ws_pwm_t* pwm, uint gpio, uint freq, float duty)
{
	pwm->gpio = gpio;

	gpio_set_function(gpio, GPIO_FUNC_PWM);
	uint slice = pwm_gpio_to_slice_num(gpio);
	uint chan  = pwm_gpio_to_channel(gpio);

	ws_pwm_init(pwm, slice, chan, freq, duty);
}


/**
 * Setup a PWM channel with the desired frequency and duty cycle

 * This will chose the best clock divider to get the desired frequency
 * and set the wrap value accordingly
 * while still having the maximum resolution for the duty cycle
 *
 */
void ws_pwm_init(ws_pwm_t* pwm, uint slice, uint chan, uint32_t freq, float initial_duty)
{
	pwm->slice = slice;
	pwm->chan  = chan;
	pwm->freq  = freq;
	pwm->duty  = initial_duty;

	// Little trick for ceiling
	uint32_t div_16 = CLK_FREQ / freq / 4096 + (CLK_FREQ % (freq * 4096) != 0);

	if (div_16 / 16 == 0)
		div_16 = 16;

	uint32_t wrap = CLK_FREQ * 16 / div_16 / freq - 1;
	pwm->wrap	  = wrap;

	pwm_set_clkdiv_int_frac(slice, div_16 / 16, div_16 & 0x0F);
	pwm_set_wrap(slice, wrap);
	ws_pwm_set_duty(pwm, initial_duty);
}

/**
 * Set the PWM duty cycle from a value between 0 and 1
 */
void ws_pwm_set_duty(ws_pwm_t* pwm, float duty)
{
	if (duty > 1)
		duty = 1.0;
	else if (duty < 0)
		duty = 0.0;

	pwm->duty = duty;

	uint16_t level = pwm->wrap * duty;

	pwm_set_chan_level(pwm->slice, pwm->chan, level);
}


void ws_pwm_enable(ws_pwm_t* pwm)
{
	pwm_set_enabled(pwm->slice, true);
}

void ws_pwms_enable(uint8_t nb_pwms, ws_pwm_t** pwms)
{
	for (int i = 0; i < nb_pwms; i++)
		ws_pwm_enable(pwms[i]);
}
