# This helps computing the power considering the resistance of the coils
# to compute the maximum voltage we can put without frying the Transistors
# Datasheet transistor : https://assets.nexperia.com/documents/data-sheet/BUK6D120-40E.pdf




if __name__ == "__main__":
    


    rdson_at_3V3 = 0.3 # Ohms
    coil_ohm = 0.7 # Ohms
    vcc = 1 # volts
    vds_fet = vcc * (rdson_at_3V3 / (coil_ohm + rdson_at_3V3))
    voltage_coil = vcc - vds_fet

    power_fet_3V3 = (vds_fet**2) / rdson_at_3V3
    power_coil_3 = (voltage_coil**2) / coil_ohm

    current = voltage_coil / coil_ohm

    print(f"USING BUK6D120-40E")
    print(f"Voltage on coil {coil_ohm} [Ohms] : {voltage_coil:6.02f} [V]")
    print(f"Voltage on fet {rdson_at_3V3} [Ohms] : {vds_fet:6.02f} [V]")
    print(f"Power dissipated by the fet at VCC = {vcc} [V]: {power_fet_3V3:6.02f} W")
    print(f"Power dissipated by the coil at VCC = {vcc} [V]: {power_coil_3:6.02f} W")
    print(f"Current in the coil : {current:6.02f} [A]")