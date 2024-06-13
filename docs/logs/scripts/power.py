
# This compute the power dissipated by the mosfet




if __name__ == "__main__":
	

	rdson_at_3V3 = 0.3 # Ohms
	rdson_at_5V = 0.2 # Ohms
	coil_ohm = 5 # Ohms


	power_fet_5 = (5**2) / rdson_at_5V
	power_fet_3 = (3.3**2) / rdson_at_3V3

	power_coil_5 = (5**2) / coil_ohm
	power_coil_3 = (3.3**2) / coil_ohm

	print(f"Power dissipated by the mfet at 5V  : {power_fet_5:6.02f} W")
	print(f"Power dissipated by the mfet at 3.3V: {power_fet_3:6.02f} W")

	print(f"Power dissipated by the coil at 5V  : {power_coil_5:6.02f} W")
	print(f"Power dissipated by the coil at 3.3V: {power_coil_3:6.02f} W")





