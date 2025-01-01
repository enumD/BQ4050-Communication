# BQ4050-Communication
Try to talk with BQ4050 using i2c (Smbus) on raspberry

My HP Envy 17 2015 laptop battery is dead. I purchaused new LiPo cells and replaced the old ones. The battery is not recognized anymore and there is no output on the pins. The BMS board with the TI Bq4050 chip that take control of the charghing unit. I read a lot on the internet and find very helpful information on https://www.karosium.com/ (I'm currently waiting for the board he uses to arrive).

From the datasheet of the component : Supports Two-Wire SMBus v1.1 Interface. 
I have a raspberry pi zero 2 w with i2c and smbus support and so i tried to see if i can read and write command to the chip this way.

I connect the data, clock and ground pin of the bms to my raspberry and run "i2cdetect -y 1" but nothing appears, the bms acts like dead even if there are new charged cells attached to it.

So i decided to try with the bms attached to the laptop and boom i got 2 devices at 0x08 and 0x09.

i tried as a dumb to read and write from these devices and after a write on device 0x08 it disappear and never come back, now i have only 0x09 and it seems to receive only read (i2cget commands).

After this stupid scenario of writing nonsense bytes i understand that the Bq4050 talks with messages formatted and composed as this:

[Command Byte] [Data Bytes] [Crc]

And i discover that my chip could be in a SEAL mode that prevents any sw modification. 

From Ti forum https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/876359/bq4050-unsealing-gauge-using-i2ctool-issue:

  read operational status
  To check the status of the chip one should send this message:  
  i2cset -f -y 0 0xb 0x44 0x54 0x00 s  
  i2cget -f -y 0 0xb 0x44 i 7  
  7: 0x06 0x54 0x00 0x87 0x03 0x00 0x00  
                          0x03 mean ^^^ still sealed  

But my i2cset says wrong format, it doesn't seems the correct syntax to read more than one byte

From the same post i found: To try to UNSEAL the chip with the default password send this commands:  
i2cset -f -y 0 0xb 0x00 0x14 0x04 0x0c i  
sleep 1  
i2cset -f -y 0 0xb 0x00 0x72 0x36 0x19 i  

These seeems me corrects but before sending this i want to be able to read the status of the Bq4050.
I'm trying to write down a simple python file that take in command byte and data bytes, calculate crc and send it to the chip; this is the purpose of dump_Bq4050.py file.
