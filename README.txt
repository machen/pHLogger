FILES:

pH_Stat_Final.py: Run this (double click or from IDLE). Input parameters as prompted.
NOTE THAT LARGE pH CHANGES (<2 units) will result in non-function as pump will not run.
Also note that there isn't any handling for closing the serial port for the pump after.

pumpReset.py: Simply opens pump port, resets, then closes (CRUCIAL) the port.

At the moment, the algorithm does not

Notes on the PID algorithm:

In short:
error(t) = Setpoint-currentValue(t)
PIDValues = Kp*error(t)+Ki*SUM(error(T) for T = 0 to t)+Kd*(error(t)-error(tprevious))
NewPumpRate = PIDValues*100

Kp=Higher values weight the algorithm toward adjusting to what the current error is
Ki=Higher values weight the algorithm toward adjusting how the error is changing in time (higher values mean that a static error results in an increase of pumping rate)
Kd=Higher values will adjust for how quickly the pumping rate is changing

Previous defaults were (2,0,1) for (Kp,Ki,Kd). I would probably recommend (1,0.5,2).

Be careful increasing Kp or Ki, as it will induce additional overshoot, which this particular system does not handle well.


FIX LIST:

-Recognize pump maximum speed and limit infusion via that.