

import serial 


def main():
	ser = serial.Serial('/dev/ttyACM0', 115200)

	START_BYTE = 0x02
	STOP_BYTE = 0x03
	x = '1'
	y = '2'

	#for i in range(10):
	print("Sending data")
	data = [START_BYTE, ord(x), ord(y), STOP_BYTE]
	ser.write(data)
	print("Data sent")


	ser.close()


if __name__ == '__main__':
	main()