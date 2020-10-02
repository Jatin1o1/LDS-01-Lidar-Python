# LDS-01-Lidar-Python
Python script to view LDS-01 Lidar sensor data

## Code explanation

From the datasheet, we can see that a packet of data consists of 42 bytes (See Table: Data Information, pg. 5 of 8). However, you will note when reading the byte descriptions that each packet of data consists of:

* One sync byte (index 0)
* Six angles and their data (indexes 1-39)
* Two checksum bytes (indexes 40-41)

The line “if (result[-1] == result[-2]” is checking if the two checksum bytes in indexes 40 and 41 are identical (negative indexes count backwards from the last index). If they are, the data packet is valid and not corrupted/miscalculated by the device.

Because only six angles worth of data is being received at any one time, we need to know the base angle for those six angles so we know whether they’re angles 90-95, 63-68, etc.

From the datasheet, there is a note next to the table that says “angle = angle index*6 + offset”. As we are looking for the base angle, ignore the offset for now, so our translation of that information can be “base_angle = angle_index*6”. However, if we look at the last column of the Data Information Table, it says that the angle_index will be in the range of 0xA0 to 0xDB. This is hexadecimal representation of the range 160 to 219. The line below this says that the range 0xA0 to 0xDB should be equivalent to 0 to 60. But we just established it is sending 160 to 219. To convert “160 to 219” to “0 to 60”, you need an offset of 160 then multiply it by 6 as per the original equation “base_angle = angle_index*6”. Hence the line “base_angle = (result[1] - 160)*6”.

Now, the line “rpm = result[3]*256 + result[2]” is creating data that isn’t being used but you will need to understand how this works if you want to correct for result skew. Essentially, because the LIDAR system is rotating, the angle at which the outgoing laser is transmitting is different to the angle at which that same information will be received by the LIDAR (because it has since rotated a small amount). This means that if you put your LIDAR in a rectangular box, the resulting scan will likely be a slightly skewed rectangular box. You can correct for this and the maths isn’t all that difficult but I left it out because I’m using this LIDAR for a sumo-robot competition where the constant information stream means my robot will correct for any skew as it intercepts the target.

Anyway, according to the table, the RPM information is made up of bytes 2 and 3. Byte 2 is the “low” portion of the data according to the last column, and Byte 3 is the “high” portion of the data. What this means is your RPM is made up of the concatenation or joining of Bytes 2 to 3. E.g. if Byte 2 is 5 and Byte 3 is 7, the RPM is 75. If the High/Low were reversed, your result would be 57. Now, to get those bytes in the correct positions is known as “bit-shifting”. I like the method of high_byte*(2^x) where x is the amount of positions you’re shifting. Because a byte is 4 bits, and we want Byte 3 to start in bit position 8 so that is [BYTE 3][BYTE 2] we want high_byte*(2^8) which is high_byte*(256), then add the low byte to the front of it so its high_byte*(256) + low_byte.

You can follow the same logic for “Intensity” and see the quality of your reflected signal.

Now, to calculate each of the six angles within the six provided by each data packet, we use similar bit shifting but we want to dynamically calculate which bytes of the data packet we operate on rather than hard-coding all 6 angles. There is no difference performance-wise but if for example you wanted to report intensity as well as the distance measured, you only change one line of code rather than 6. Let’s dissect the line “distance = result[((6*(x+1))+1)]*256 + result[((6*(x+1)))]”.

This line operates within a for-loop ranging from 0 to 5, representing the 6 angular offsets.

The “result[((6*(x+1))+1)]” is just a formula for working out which byte of the 42 bytes is the HIGH byte for the particular angles distance. Looking at the table for example, each angle is separated by 12 bytes. Similarly, “result[((6*(x+1)))]” calculates which byte of the 42 byes is the LOW byte for the angles distance. Again, this is then bit-shifted to create the correct result.
