import network, time, urequests
from machine import Pin, I2C
from utime import sleep
import sh1106
from hcsr04 import HCSR04

device_on = Pin(16, Pin.OUT)   # led verde dispositivo encendido
ligth_on = Pin(17, Pin.OUT)   # led amarillo simula prender bombillo en el lugar
alarm_on = Pin(19, Pin.OUT)   # led rojo simula abertura de puerta, infrarrojo enciende alarma sonora
leds = [device_on, ligth_on, alarm_on]

# configuracion de pantalla OLED+1
wide = 128
high = 64
screen = I2C(0, scl=Pin(22), sda=Pin(21))
oled = sh1106.SH1106_I2C(wide, high, screen)

# configuracion de sensor ultrasonico (distancia)
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
      
    url = "https://maker.ifttt.com/trigger/message/with/key/dhYdAW6WbpI8qZTWLgqgZbqkwYr-FfqMCRIHC8k3jmW?"

    
    # muestra en la pantalla OLED comportamiento del sensor trabajando
    while True:
        device_on.value(1)
        oled.fill(0)
        distance = sensor.distance_cm()
        time.sleep(1)
        oled.text("DISTANCIA", 25, 1)
        oled.text(str(int(distance)), 50, 10)
        oled.text('CM',75,10) 

        if distance < 2:
            print("Todo tranquilo")
            oled.text("Status", 10, 20)
            oled.text("Todo tranquilo", 10, 30)
            ligth_on.value(0)
            alarm_on.value(0)
            #time.sleep_ms(50)
            registry = []
        elif distance > 2 and distance < 150:
            print("Hay alguien cerca")
            oled.text("Status", 10, 20)
            oled.text("Alguien cerca", 10, 30)
            ligth_on.value(1)
            registry.insert(0, distance)
            print(registry)
            #time.sleep_ms(10)
            if len(registry) > 5:
                if registry[5] >= 3 and registry[3] <= 150:
                    print("ALERTA DE INTRUSO")
                    oled.text("INTRUSO", 10, 40)
                    ligth_on.value(1)
                    alarm_on.value(1)
                    #time.sleep(1)
                    
                    respuesta = urequests.get(url+"&value1="+str(distance)) # url+"&field1="+str(temp)+"&field2="+str(hum)
                    print(respuesta.text)
                    print(respuesta.status_code)
                    respuesta.close ()
                    oled.text(str(respuesta.status_code), 25, 50) 
           
        oled.show() 
        time.sleep_ms(50)

        print (f"Distancia: {distance:.3f} cm")
        
        file.write(str(f"Distancia: {distance:.3f} cm "))
        file.flush()     
 
else:
       print ("Imposible conectar")
       miRed.active (False)
       
if __name__==("__main__"):
    main()
