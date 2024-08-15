/**
 * Coil map code
 * Author: Jonas Stirnemann
 * Date: 07/08/2024
 *
 * This file remaps the actual coils to the rows and cols to activate
 * this also contains the functions to trigger the actual coils
 */

#include "magtrix.h"

#include "mag_pwm.h"
#include "mag_sr.h"

// This is a matrix representing the coil matrix
// with the actual row and column to activate the coils
// according to their indices
const coord_t coil_map[NB_COLS][NB_ROWS] = { // --
	{
	  // ! ROW 0
	  { .row = 0, .col = 0 },  // 0, 0
	  { .row = 0, .col = 1 },  // 0, 1
	  { .row = 0, .col = 2 },  // 0, 2
	  { .row = 0, .col = 3 },  // 0, 3
	  { .row = 0, .col = 4 },  // 0, 4
	  { .row = 0, .col = 5 },  // 0, 5
	  { .row = 0, .col = 6 },  // 0, 6
	  { .row = 0, .col = 7 },  // 0, 7
	  { .row = 0, .col = 8 },  // 0, 8
	  { .row = 0, .col = 9 },  // 0, 9
	  { .row = 0, .col = 10 }, // 0, 10
	  { .row = 0, .col = 11 }, // 0, 11
	  { .row = 0, .col = 12 }, // 0, 12
							   // --
	},

	{
	  // ! ROW 1
	  { .row = 1, .col = 0 },	  // 1, 0
	  { .row = NON, .col = NON }, // 1, 1
	  { .row = 1, .col = 2 },	  // 1, 2
	  { .row = NON, .col = NON }, // 1, 3
	  { .row = 1, .col = 4 },	  // 1, 4
	  { .row = NON, .col = NON }, // 1, 5
	  { .row = 1, .col = 6 },	  // 1, 6
	  { .row = NON, .col = NON }, // 1, 7
	  { .row = 1, .col = 8 },	  // 1, 8
	  { .row = NON, .col = NON }, // 1, 9
	  { .row = 1, .col = 10 },	  // 1, 10
	  { .row = NON, .col = NON }, // 1, 11
	  { .row = 1, .col = 12 },	  // 1, 12
								  // --
	},

	{
	  // ! ROW 2
	  { .row = 2, .col = 0 },  // 2, 0
	  { .row = 1, .col = 1 },  // 2, 1
	  { .row = 2, .col = 2 },  // 2, 2
	  { .row = 1, .col = 3 },  // 2, 3
	  { .row = 2, .col = 4 },  // 2, 4
	  { .row = 1, .col = 5 },  // 2, 5
	  { .row = 2, .col = 6 },  // 2, 6
	  { .row = 1, .col = 7 },  // 2, 7
	  { .row = 2, .col = 8 },  // 2, 8
	  { .row = 1, .col = 9 },  // 2, 9
	  { .row = 2, .col = 10 }, // 2, 10
	  { .row = 1, .col = 11 }, // 2, 11
	  { .row = 2, .col = 12 }, // 2, 12
							   // --
	},

	{
	  // ! ROW 3
	  { .row = 3, .col = 0 },	  // 3, 0
	  { .row = NON, .col = NON }, // 3, 1
	  { .row = 3, .col = 2 },	  // 3, 2
	  { .row = NON, .col = NON }, // 3, 3
	  { .row = 3, .col = 4 },	  // 3, 4
	  { .row = NON, .col = NON }, // 3, 5
	  { .row = 3, .col = 6 },	  // 3, 6
	  { .row = NON, .col = NON }, // 3, 7
	  { .row = 3, .col = 8 },	  // 3, 8
	  { .row = NON, .col = NON }, // 3, 9
	  { .row = 3, .col = 10 },	  // 3, 10
	  { .row = NON, .col = NON }, // 3, 11
	  { .row = 3, .col = 12 },	  // 3, 12
								  // --
	},

	{
	  // ! ROW 4
	  { .row = 4, .col = 0 },  // 4, 0
	  { .row = 2, .col = 1 },  // 4, 1
	  { .row = 4, .col = 2 },  // 4, 2
	  { .row = 2, .col = 3 },  // 4, 3
	  { .row = 4, .col = 4 },  // 4, 4
	  { .row = 2, .col = 5 },  // 4, 5
	  { .row = 4, .col = 6 },  // 4, 6
	  { .row = 2, .col = 7 },  // 4, 7
	  { .row = 4, .col = 8 },  // 4, 8
	  { .row = 2, .col = 9 },  // 4, 9
	  { .row = 4, .col = 10 }, // 4, 10
	  { .row = 2, .col = 11 }, // 4, 11
	  { .row = 4, .col = 12 }, // 4, 12
							   // --
	},

	{
	  // ! ROW 5
	  { .row = 5, .col = 0 },	  // 5, 0
	  { .row = NON, .col = NON }, // 5, 1
	  { .row = 5, .col = 2 },	  // 5, 2
	  { .row = NON, .col = NON }, // 5, 3
	  { .row = 5, .col = 4 },	  // 5, 4
	  { .row = NON, .col = NON }, // 5, 5
	  { .row = 5, .col = 6 },	  // 5, 6
	  { .row = NON, .col = NON }, // 5, 7
	  { .row = 5, .col = 8 },	  // 5, 8
	  { .row = NON, .col = NON }, // 5, 9
	  { .row = 5, .col = 10 },	  // 5, 10
	  { .row = NON, .col = NON }, // 5, 11
	  { .row = 5, .col = 12 },	  // 5, 12
								  // --
	},

	{
	  // ! ROW 6
	  { .row = 6, .col = 0 },  // 6, 0
	  { .row = 3, .col = 1 },  // 6, 1
	  { .row = 6, .col = 2 },  // 6, 2
	  { .row = 3, .col = 3 },  // 6, 3
	  { .row = 6, .col = 4 },  // 6, 4
	  { .row = 3, .col = 5 },  // 6, 5
	  { .row = 6, .col = 6 },  // 6, 6
	  { .row = 3, .col = 7 },  // 6, 7
	  { .row = 6, .col = 8 },  // 6, 8
	  { .row = 3, .col = 9 },  // 6, 9
	  { .row = 6, .col = 10 }, // 6, 10
	  { .row = 3, .col = 11 }, // 6, 11
	  { .row = 6, .col = 12 }, // 6, 12
							   // --
	},

	{
	  // ! ROW 7
	  { .row = 7, .col = 0 },	  // 7, 0
	  { .row = NON, .col = NON }, // 7, 1
	  { .row = 7, .col = 2 },	  // 7, 2
	  { .row = NON, .col = NON }, // 7, 3
	  { .row = 7, .col = 4 },	  // 7, 4
	  { .row = NON, .col = NON }, // 7, 5
	  { .row = 7, .col = 6 },	  // 7, 6
	  { .row = NON, .col = NON }, // 7, 7
	  { .row = 7, .col = 8 },	  // 7, 8
	  { .row = NON, .col = NON }, // 7, 9
	  { .row = 7, .col = 10 },	  // 7, 10
	  { .row = NON, .col = NON }, // 7, 11
	  { .row = 7, .col = 12 },	  // 7, 12
								  // --
	},

	{
	  // ! ROW 8
	  { .row = 8, .col = 0 },  // 8, 0
	  { .row = 4, .col = 1 },  // 8, 1
	  { .row = 8, .col = 2 },  // 8, 2
	  { .row = 4, .col = 3 },  // 8, 3
	  { .row = 8, .col = 4 },  // 8, 4
	  { .row = 4, .col = 5 },  // 8, 5
	  { .row = 8, .col = 6 },  // 8, 6
	  { .row = 4, .col = 7 },  // 8, 7
	  { .row = 8, .col = 8 },  // 8, 8
	  { .row = 4, .col = 9 },  // 8, 9
	  { .row = 8, .col = 10 }, // 8, 10
	  { .row = 4, .col = 11 }, // 8, 11
	  { .row = 8, .col = 12 }, // 8, 12
							   // --

	},

	{
	  // ! ROW 9
	  { .row = 9, .col = 0 },	  // 9, 0
	  { .row = NON, .col = NON }, // 9, 1
	  { .row = 9, .col = 2 },	  // 9, 2
	  { .row = NON, .col = NON }, // 9, 3
	  { .row = 9, .col = 4 },	  // 9, 4
	  { .row = NON, .col = NON }, // 9, 5
	  { .row = 9, .col = 6 },	  // 9, 6
	  { .row = NON, .col = NON }, // 9, 7
	  { .row = 9, .col = 8 },	  // 9, 8
	  { .row = NON, .col = NON }, // 9, 9
	  { .row = 9, .col = 10 },	  // 9, 10
	  { .row = NON, .col = NON }, // 9, 11
	  { .row = 9, .col = 12 },	  // 9, 12
	},

	{
	  // ! ROW 10
	  { .row = 10, .col = 0 },	// 10, 0
	  { .row = 5, .col = 1 },	// 10, 1
	  { .row = 10, .col = 2 },	// 10, 2
	  { .row = 5, .col = 3 },	// 10, 3
	  { .row = 10, .col = 4 },	// 10, 4
	  { .row = 5, .col = 5 },	// 10, 5
	  { .row = 10, .col = 6 },	// 10, 6
	  { .row = 5, .col = 7 },	// 10, 7
	  { .row = 10, .col = 8 },	// 10, 8
	  { .row = 5, .col = 9 },	// 10, 9
	  { .row = 10, .col = 10 }, // 10, 10
	  { .row = 5, .col = 11 },	// 10, 11
	  { .row = 10, .col = 12 }, // 10, 12
	},

	{
	  // ! ROW 11
	  { .row = 11, .col = 0 },	  // 11, 0
	  { .row = NON, .col = NON }, // 11, 1
	  { .row = 11, .col = 2 },	  // 11, 2
	  { .row = NON, .col = NON }, // 11, 3
	  { .row = 11, .col = 4 },	  // 11, 4
	  { .row = NON, .col = NON }, // 11, 5
	  { .row = 11, .col = 6 },	  // 11, 6
	  { .row = NON, .col = NON }, // 11, 7
	  { .row = 11, .col = 8 },	  // 11, 8
	  { .row = NON, .col = NON }, // 11, 9
	  { .row = 11, .col = 10 },	  // 11, 10
	  { .row = NON, .col = NON }, // 11, 11
	  { .row = 11, .col = 12 },	  // 11, 12
	},

	{
	  // ! ROW 12
	  { .row = 12, .col = 0 },	// 12, 0
	  { .row = 6, .col = 1 },	// 12, 1
	  { .row = 12, .col = 2 },	// 12, 2
	  { .row = 6, .col = 3 },	// 12, 3
	  { .row = 12, .col = 4 },	// 12, 4
	  { .row = 6, .col = 5 },	// 12, 5
	  { .row = 12, .col = 6 },	// 12, 6
	  { .row = 6, .col = 7 },	// 12, 7
	  { .row = 12, .col = 8 },	// 12, 8
	  { .row = 6, .col = 9 },	// 12, 9
	  { .row = 12, .col = 10 }, // 12, 10
	  { .row = 6, .col = 11 },	// 12, 11
	  { .row = 12, .col = 12 }, // 12, 12
	}
};


/**
 * @brief : Check if the given coordinate is valid
 */
coord_err_t is_coord_valid(coord_t coord)
{
	if (coord.row >= NB_ROWS)
		return ROW_OOR;
	if (coord.col >= NB_COLS)
		return COL_OOR;
	return OK;
}

/**
 * @brief : Get the row and column to power in order
 * 			to activate the coil at the given index
 */
static coord_t get_coil(uint8_t x, uint8_t y)
{
	coord_t coord = { .row = NON, .col = NON, .err = OK };

	coord.err = is_coord_valid(coord);

	if (coord.err != OK)
		return coord;

	coord.row = coil_map[x][y].row;
	coord.col = coil_map[x][y].col;

	return coord;
}

bool power_a_coil(mag_sr_t* sr, mag_pwm_t* pwms, uint8_t x, uint8_t y)
{
	coord_t coord = get_coil(x, y);

	if (coord.err != OK)
		return false;

	// ! Power the row with the shift register
	mag_sr_power_row(sr, coord.row);

	// ! Power the column with the pwm
	mag_pwm_set_duty(&pwms[coord.col], 1.0);

	return true;
}