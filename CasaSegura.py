import network, time, urequests
from machine import Pin, I2C
from utime import sleep
import sh1106
from hcsr04 import HCSR04

device_on = Pin(16, Pin.OUT)   # led verde para simular que el dispositivo esta encendido y trabajando
ligth_on = Pin(17, Pin.OUT)   # led amarillo para simular prender bombillo en el lugar
alarm_on = Pin(19, Pin.OUT)   # led rojo para simular que enciende la alarma y suena el altavoz
leds = [device_on, ligth_on, alarm_on]

# configuracion de pantalla OLED
wide = 128
high = 64
screen = I2C(0, scl=Pin(22), sda=Pin(21))
oled = sh1106.SH1106_I2C(wide, high, screen)

# configuracion de sensor de ultrasonido (distancia)
sensor = HCSR04(trigger_pin=14, echo_pin=12, echo_timeout_us=10000)

# archivo donde se guardara la informacion en tarjeta ESP
file = open('datos.csv','w')

# funcion para conectarse a la red WIFI
def conectaWifi (red, password):
      global miRed
      miRed = network.WLAN(network.STA_IF)     
      if not miRed.isconnected():              #Si no está conectado…
          miRed.active(True)                   #activa la interface
          miRed.connect(red, password)         #Intenta conectar con la red
          print('Conectando a la red', red +"…")
          timeout = time.time ()
          while not miRed.isconnected():           #Mientras no se conecte..
              if (time.ticks_diff (time.time (), timeout) > 10):
                  return False
      return True

if conectaWifi ("ThiagoConde", "Thiago18."):

    print ("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())
      
    url = "https://api.thingspeak.com/update?api_key=H5U6DE2SJTO0R7IY&field1=0"  
    
    # muestra en la pantalla OLED comportamiento del sensor trabajando
    while True:
        device_on.value(1)
        oled.fill(0)
        distance = sensor.distance_cm()
        time.sleep(1)
        oled.text("DISTANCIA", 25, 10)
        oled.text(str(int(distance)), 50, 25)
        oled.text('CM',75,25) 

        if distance < 2:
            print("tranquilo")
            ligth_on.value(0)
            alarm_on.value(0)
            time.sleep_ms(50)
            registry = []
        elif distance > 5 and distance < 400:
            print("hay alguien")
            ligth_on.value(1)
            registry.insert(0, distance)
            print(registry)
            time.sleep_ms(50)
            if len(registry) > 3:
                if registry[3] >= 5:
                    print("ALERTA DE INTRUSO")
                    ligth_on.value(1)
                    alarm_on.value(1)
                    time.sleep(5)
            
        #respuesta = urequests.get(url+"&field1="+str(distance)) # url+"&field1="+str(temp)+"&field2="+str(hum)
        #print(respuesta.text)
        #print(respuesta.status_code)
        #respuesta.close ()
        #oled.text(str(respuesta.status_code), 25, 40)
        oled.show()
        time.sleep_ms(50)

        print (f"Distancia: {distance:.3f} cm")
        
        file.write(str(f"Distancia: {distance:.3f} cm "))
        file.flush()     

        
 
else:
       print ("Imposible conectar")
       miRed.active (False)
       

