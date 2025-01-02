# Reset/Unlock the hp laptop battery bms HP VI04-4 
 
Try to talk with BQ4050 using i2c (Smbus protocol) on raspberry

My HP Envy 17 2015 laptop battery is dead. I purchaused new LiPo cells (Samsung ICR18650-26 ZLF rechargable battery 18650 Li-Ion 3.7 V 2550 mAh) same specs and replaced the old ones. The battery is not recognized anymore and there is no output on the pins. The BMS board has one TI Bq4050 chip that take control of the charghing unit. I read a lot on the internet and find very helpful information on https://www.karosium.com/ (I'm currently waiting for the board he uses to arrive).

From the datasheet of the component : Supports Two-Wire SMBus v1.1 Interface. 
I have a raspberry pi zero w with i2c and smbus support and so i tried to see if i can read and write command to the chip this way.

I connect the data, clock and ground pin of the bms to my raspberry and run "i2cdetect -y 1" but nothing appears, the bms acts like dead even if there are new charged cells attached to it.

So i decided to try with the bms attached to the laptop and boom i got 2 devices at 0x08 and 0x09.

i tried as a dumb to read and write from these devices and after a write on device 0x08 it disappear and never come back, now i have only 0x09 and it seems to receive only read (i2cget commands).

After this stupid scenario of writing nonsense bytes i understand that i would have to read at least the component datasheet and there it is.

## BQ4050 
Here are some utilities  
[Bq4050 Technical Manual](https://www.ti.com/lit/ug/sluuaq3a/sluuaq3a.pdf)  
[Bq4050 Electrical](https://www.ti.com/lit/ds/slusc67b/slusc67b.pdf?ts=1735761186114)  

Reading the datasheet teach me that my chip could be in a SEAL mode that prevents any sw modification; and it need a password to be unsealed. Unfortunately at this point i cannot see my device anymore using:  
> i2cdetect -y 1

but from the [Ti Forum](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/876359/bq4050-unsealing-gauge-using-i2ctool-issue) i found out that:  

To try to UNSEAL the chip with the default password send this commands:  
> i2cset -f -y 0 0xb 0x00 0x14 0x04 0x0c i  
> sleep 1  
> i2cset -f -y 0 0xb 0x00 0x72 0x36 0x19 i  

These seems the same procedure written on the datasheet of the Bq4050.

# BQ30z55
I've tried to see my device under i2c but nothing appear, the device is gone after a dump write and don't want to come back. I had another hp old laptop (Envy 15 i think) where the battery doesn't have the same size but has the same connector. I tear down it and found a bms with the BQ30z55 chip on it; connect data, clock and gnd a launch a i2cdetect: Nothing, no device!
I've struggles two days reading [BQ30z55 Technical Manual](https://media.digikey.com/pdf/Data%20Sheets/Texas%20Instruments%20PDFs/BQ30Z50,55-R1_TechRef.pdf) and started to check the chip pinout to see if something happen, at one point a also make a small short circuit between first cell ground and first cell positive...i was like "Oh fuck! i bricked another bms fuck" but when i connected it to the raspberry...TADHAAAAA! device 0x0B found!  
I tried to read some bytes with i2cget and everything worked fine, so decided to give a try to [DjI Firmware Tools](https://github.com/o-gs/dji-firmware-tools) where this great guy develop an incredible tools for battery management: [comm_sbs_bqctrl](https://github.com/o-gs/dji-firmware-tools/blob/master/comm_sbs_bqctrl.py).  
With this incredible tool i managed to read my battery status, unseal the device and gain Full Access to reset the fail and error and restore the battery

![Unsealing image](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/bq30z55_unsealing.png)

### Reset Status process
After unsealing the device and obtaining the full Access i started to check the errors present and try to delete them, i run  
> python3.9 comm_sbs_bqctrl.py -vvv --bus "smbus:1" --chip BQ30z55 --dev_address 0xb --verbose monitor BQStatusBitsMA

And i got:    
:white_check_mark: Safety Alert Bits: No error  
:white_check_mark: Safety Status Bits: No error  
:white_check_mark: Permanent Fail Alert Bits: No error  
:x: Permanent Fail Status Bits: 0x04 -> Error on [CUDEP] Copper Deposition    
:x: Operational Status Bits: Error  
![Manufacture Acess](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/manufacturAccess.png)  

:x: Charging Status Bit and Gauging Status bit  
![Manufacture Acess](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/chargingstatus.png)  

:x: Manufacturing Status Bit  
![Manufacture Acess](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/manustatusbiyt.png)  

The battery status is in permanent fail, so i want to try to reset some errors and see what happen:  

So i run  
>python3.9 comm_sbs_bqctrl.py -vvv --bus "smbus:1" --chip BQ30z55 --dev_address 0xb --verbose trigger ManufacturerAccess.PermanentFailDataReset

The command succeed, check again BQStatusBitMA and saBoooooom!  
:white_check_mark: Safety Alert Bits: No error  
:white_check_mark: Safety Status Bits: No error  
:white_check_mark: Permanent Fail Alert Bits: No error  
:white_check_mark: Permanent Fail Status Bits: No Error  
:x: Operational Status Bits: No bad error, but i think that Charging disabled is not good but maybe because is not attached to a power source?!?  ( Shows the differences before and after reset trigger command)
![Operational Status Bit OK](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/operationalStatusBit_OK.png)  





