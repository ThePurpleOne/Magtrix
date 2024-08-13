/**
 * Coil map header
 * Author: Jonas Stirnemann
 * Date: 07/08/2024
 */

#pragma once

#include <stdbool.h>
#include <stdint.h>

#define NB_ROWS 13
#define NB_COLS 13
#define NON		0xFF // This is put as index when it does not exist

typedef enum
{
	OK,
	ROW_OOR, // Out of range
	COL_OOR, // Out of range
} coord_err_t;

typedef struct
{
	uint8_t		row, col;
	coord_err_t err;
} coord_t;

const coord_t coords[NB_COLS][NB_ROWS];

coord_err_t is_coord_valid(coord_t coord);
