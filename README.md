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

The battery status is in permanent fail, so i want to try to reset some errors and see what happen; to do this i run "trigger-list" to list all possible trigger options: PermanentFailDataReset seems good, let's try if it works:    
So i run  
>python3.9 comm_sbs_bqctrl.py -vvv --bus "smbus:1" --chip BQ30z55 --dev_address 0xb --verbose trigger ManufacturerAccess.PermanentFailDataReset

The command succeed, check again BQStatusBitMA and saBoooooom!  
:white_check_mark: Safety Alert Bits: No error  
:white_check_mark: Safety Status Bits: No error  
:white_check_mark: Permanent Fail Alert Bits: No error  
:white_check_mark: Permanent Fail Status Bits: No Error  
:x: Operational Status Bits: No bad error, but i think that Charging disabled is not good but maybe because is not attached to a power source?!?  ( Shows the differences before and after reset trigger command)
![Operational Status Bit OK](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/operationalStatusBit_OK.png)  

:white_check_mark: Charging Status Bit and Gauging Status bit  
![Manufacture Acess OK](https://github.com/enumD/BQ4050-Communication/blob/main/pictures/chargingStatusit_ok.png)  

:x: Manufacturing Status Bit : Not changed, permanent failure is still active here (not anymore in Operational Status Bit)  

The trigger list of available trigger:  
**ManufacturerAccess.BlackBoxRecorder**: Enables/disables Black box recorder function. Toggle switch which allows to control the recorder for ease of manufacturing.  
**ManufacturerAccess.BlackBoxRecorderReset**: Resets the black box recorder data in data flash. Toggle switch which allows to control the Black Box Recorder data in DF for ease of manufacturing.  
**ManufacturerAccess.CALMode**: Outputs the raw ADC and CC data. Output of the raw data on ManufacturingData(), is controllable with 0xF081 and 0xF082 on ManufacturerAccess(). Toggle switch - write the value again to disable the output.  
**ManufacturerAccess.ChargeFET**: Turns on/off CHG FET drive function. Toggle switch which allows to control the Charge FET for ease of testing during manufacturing.  
**ManufacturerAccess.DeviceReset**: Resets the device. This counts as Full Device Reset as well as AFE Reset, the terms used in chip reference doc.  
**ManufacturerAccess.DischargeFET**: Turns on/off DSG FET drive function. Toggle switch which allows to control the Discharge FET for ease of testing during manufacturing.  
**ManufacturerAccess.ExitCalibOutputMode**: Exit Calibration Output Mode. Stop output of ADC or CC data on ManufacturerData() and return to NORMAL data acquisition mode.  
**ManufacturerAccess.FETControl**: Control of the CHG, DSG, and PCHG FET. Toggle switch which allows to either control the 3 FETs by the firmware, or disable automation and allow manual control.  
**ManufacturerAccess.Fuse**: Enables/disables firmware fuse toggle function. Toggle switch which allows to control the fuse for ease of manufacturing.  
**ManufacturerAccess.FuseToggle**: Activate/deactivate FUSE pin. Toggle switch which allows to control the FUSE for ease of testing during manufacturing.  
**ManufacturerAccess.Gauging**: Enable/disable the gauging function. Toggle switch which allows to control the Gauge for ease of testing during manufacturing.  
**ManufacturerAccess.LEDDisplayOn**: Simulates low-high-low detection on the /DISP pin. Toggle switch which allows to control the /DISP pin for ease of manufacturing.  
**ManufacturerAccess.LEDEnable**: Enables/disables LED Display function. Toggle switch which allows to control the LEDs for ease of manufacturing.  
**ManufacturerAccess.LEDToggle**: Activate/deactivate configured LEDs. Toggle switch which allows to control the LEDs for ease of testing during manufacturing.  
**ManufacturerAccess.LifetimeDataCollection**: Enables/disables Lifetime data collection. Toggle switch which allows to control whether Lifetime Data collection feature is working.  
**ManufacturerAccess.LifetimeDataReset**: Resets Lifetime data data in data flash. Clears the flags for ease of manufacturing.  
**ManufacturerAccess.PermanentFailDataReset**: Resets PF data in data flash. Clears permanent fail flags for ease of manufacturing. If the condition which caused the flag to appear is still tripped, the flag will get set again.  
**ManufacturerAccess.PermanentFailure**: Enables/disables Permanent Failure. Toggle switch which allows to control when PF can be triggered for ease of manufacturing.  
**ManufacturerAccess.PreChargeFET**: Turns on/off Pre-CHG FET drive function. Toggle switch which allows to control the FUSE for ease of testing during manufacturing.  
**ManufacturerAccess.ROMMode**: Enables the ROM mode for IF update. On this command, device goes to ROM mode ready for re-programming firmware in Instruction Flash. Thit is often called BootROM mode. Use 0x08 to ManufacturerAccess() to return.  
**ManufacturerAccess.SHIPMode**: Low power SHIP Mode with no physical measurements. Enters a low power mode with no voltage, current, and temperature measurements, FETs are turned off, and the MCU is in a halt state. The device will return to NORMAL mode on SBS communication detection.  
**ManufacturerAccess.SealDevice**: Seals the device, disabling some commands. Certain SBS commands and access to DF are disabled in sealed device.  
**ManufacturerAccess.ShutdownMode**: SHUTDOWN mode with reduced power consumption. The device can be sent to this mode before shipping. The device will wake up when a voltage is applied to PACK.  
**ManufacturerAccess.SleepMode**: Send device to sleep if conditions are met. Some of wake conditions are: Current exceeds Sleep Current, WakeComparator trips, SafetyAlert() or PFAlert() flags are set.  

Lots of command, the most interesting are: BlackBoxRecorderReset, DeviceReset, LifetimeDataReset, PermanentFailDataReset (already tried). Lets see what the documentation says about that:  
**Black Box Recorder Reset**: Just reset the black box recording, usefull to separate old problems from new.  
**ManufacturerAccess.DeviceReset**: documentation do not add usefull info, i will give it a try.  
**ManufacturerAccess.LifetimeDataReset**: I will run this to separate old problems from new and to set cyclecount to zero  
Ok lets run these commands and see what happen:  

**BlackBoxRecorderReset**  
> dario@MotorolaG10:~/dji-firmware-tools $ python3.9 comm_sbs_bqctrl.py -vvv --bus "smbus:1" --chip BQ30z55 --dev_address 0xb --verbose trigger ManufacturerAccess.BlackBoxRecorderReset  
> Opening smbus:1  
> Importing comm_sbs_chips/BQ30z554.py  
> Writing write_word_subcommand command at addr=0xb, cmd=0x0, type=uint16, v=b'', opts={'subcmd': <MANUFACTURER_ACCESS_CMD_BQ30.BlackBoxRecorderReset: 42>}  
> Store ManufacturerAccess.BlackBoxRecorderR eset: 00 WORD=0x2a  
> Write ManufacturerAccess: 00 WORD=0x2a  
> MA.BlackBoxRecorderReset:	trigger	SUCCESS	Trigger switch write accepted

**LifetimeDataReset**  
> dario@MotorolaG10:~/dji-firmware-tools $ python3.9 comm_sbs_bqctrl.py -vvv --bus "smbus:1" --chip BQ30z55 --dev_address 0xb --verbose trigger ManufacturerAccess.LifetimeDataReset  
> Opening smbus:1  
> Importing comm_sbs_chips/BQ30z554.py  
> Writing write_word_subcommand command at addr=0xb, cmd=0x0, type=uint16, v=b'', opts={'subcmd': <MANUFACTURER_ACCESS_CMD_BQ30.LifetimeDataReset: 40>}  
> Store ManufacturerAccess.LifetimeDataReset: 00 WORD=0x28  
> Write ManufacturerAccess: 00 WORD=0x28  
> MA.LifetimeDataReset:	trigger	SUCCESS	Trigger switch write accepted  

Before call the last DeviceReset i want to see the list of write to be sure to have seen everything  
**AtRate**:The AtRate value used in calculations. First half of a two-function call-set used to set the AtRate value used in calculations made by the AtRateTimeToFull(), AtRateTimeToEmpty(), and AtRateOK() functions. The AtRate value may be expressed in either current (mA) or power (10mW) depending on the setting of the BatteryMode()'s CAPACITY_MODE bit.  
**BatteryMode**: Battery modes and capabilities. Selects the various battery operational modes and reports the battery’s capabilities, modes, and flags minor conditions requiring attention.    
**FullChargeCapacity**:Predicted pack capacity when it is fully charged. The value is expressed in either current (mAh at a C/5 discharge rate) or power (10mWh at a P/5 discharge rate) depending on the setting of the BatteryMode()'s CAPACITY_MODE bit.  
**ManufacturerInfo**: Manufacturer Info values. The values from ManufacturerData().  
**ManufacturerInput**: Either Authentication or ManufacturerInfo, depending on use. Direct R/W of this command isn't very useful, it is to be used in compound commands.  
**RemainingCapacity**: Predicted remaining battery capacity. The capacity value is expressed in either current (mAh at a C/5 discharge rate) or power (10mWh at a P/5 discharge rate) depending on the setting of the BatteryMode()'s CAPACITY_MODE bit.  
**RemainingCapacityAlarm**: Low Capacity alarm threshold value. Whenever the RemainingCapacity() falls below the Low Capacity value, the Smart Battery sends AlarmWarning() messages to the SMBus Host with the REMAINING_CAPACITY_ALARM bit set. A Low Capacity value of 0 disables this alarm. Unit depends on BatteryMode()'s CAPACITY_MODE bit.   
**RemainingTimeAlarm**: Remaining Time alarm value. Whenever the AverageTimeToEmpty() falls below the Remaining Time value, the Smart Battery sends AlarmWarning() messages to the SMBus Host with the REMAINING_TIME_ALARM bit set. A Remaining Time value of 0 effectively disables this alarm.  



