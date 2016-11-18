import sys
import xaut
import time
import threading
import thread

mouse = xaut.mouse()
sensitivity = 5
keyboard = xaut.keyboard()
par = False #ignoro las pulsaciones pares.
pipe = open('/dev/input/js0','r')
action = []

class mousemanipulator(threading.Thread):
	def run(self):
		self.reset()
		global mouse
		while True:
			time.sleep(.02) # Just so we don't hog CPU waiting around
			if self.coords != (0, 0):
				mouse.move(mouse.x()+self.coords[0],mouse.y()+self.coords[1])

	def updatex(self, coord): self.coords = (coord, self.coords[1])
	def updatey(self, coord): self.coords = (self.coords[0], coord)
	def reset(self): self.coords = (0, 0)
	def stop(self):
		self._Thread__stop()

#Hacer luego una funcion para cargar el keymap desde un fichero y asi poder seleccionar entre varios keymaps cuando pulse select. :)
keymap = {'00':'^{ISO_Left_Tab}', '01':'^t', '02':65, '03': '!{ISO_Left_Tab}', '04':'MSBTN1', # <- Buttons
	  '05':'MSBTN2','06':'MSSCRLUP','07':'MSSCRLDOWN',  
	  '08':None,'09':None, '0A':None, '0B':None,
	  'DPADUP':111, 'DPADDOWN':116, 'DPADLEFT':113, 'DPADRIGHT':114 # <- Dpad
	  }

def pressactivate(key): # Press down keys/buttons

	global mouse
	global action
	global keyboard
	global par

	if type(key) is int: keyboard.down(key)
	elif key == 'MSBTN1': mouse.btn_down(1)#Clic izq
	elif key == 'MSBTN2': mouse.btn_down(3)#Clic dch
	elif key == 'MSSCRLDOWN': mouse.btn_down(5)
	elif key == 'MSSCRLUP': mouse.btn_down(4)
	elif (type(key) is str) and (not par): 
		keyboard.type(key)
		par = True
	elif (type(key) is str) and par: 
		par = False
	else: pass

def keyupactivate(key): # Release buttons

	global mouse
	global action
	global keyboard
	global par

	if type(key) is int: keyboard.up(key)
	elif key == 'MSBTN1': mouse.btn_up(1)
	elif key == 'MSBTN2': mouse.btn_up(2)
	elif key == 'MSSCRLDOWN': mouse.btn_up(5)
	elif key == 'MSSCRLUP': mouse.btn_up(4)
	elif (type(key) is str) and (not par): 
		keyboard.type(key)
		par = True
	elif (type(key) is str) and par: 
		par = False
	else: pass

mousecontrol = mousemanipulator()
mousecontrol.start()
mousecontrol.reset()

salir = False

while (not salir):
	for character in pipe.read(1):
		action += ['%02X' % ord(character)]
		if len(action) == 8:

			num = int(action[5], 16) # Translate back to integer form
			percent254 = str(((float(num)-128.0)/126.0)-100)[4:6] # Calculate the percentage of push
			percent128 = str((float(num)/127.0))[2:4]

			if num >= 128: # Convert % of push back into an integer
				if percent254 == '.0': percent254 = 100
				else: percent254 = int(percent254)
			else:
				if percent128 == '0': percent128 = 100
				else: percent128 = int(percent128)
				
			#print(num)
						
			if action[6] == '01': # Button
				#print(action[7])
				key = keymap[action[7]] # Find the equivalent keyboard key to each button
				
				if action[7] != '09':
					if action[4] == '01': pressactivate(key)
					else: keyupactivate(key)
				elif not par:
					par = True #Para evitar que al volver a abrir el programa se lance el salir.
				else:
					salir = True
					#Cerrar o matar thread del raton.
					#mousecontrol.interrupt_main()
					#thread.interrupt_main() <----- ni esto funciona. :(
					mousecontrol.stop()
			
			elif action[7] == '00': # D-pad left/right
				#print "D-pad left/right"
				if action[4] == 'FF': pressactivate(keymap['DPADRIGHT'])
				elif action[4] == '01': pressactivate(keymap['DPADLEFT'])
				else: 
					keyupactivate(keymap['DPADRIGHT'])
					keyupactivate(keymap['DPADLEFT'])
			elif action[7] == '01': # D-pad up/down
				#print "D-pad up/down"
				if action[4] == 'FF': pressactivate(keymap['DPADDOWN'])
				elif action[4] == '01': pressactivate(keymap['DPADUP'])
				else: 
					keyupactivate(keymap['DPADDOWN'])
					keyupactivate(keymap['DPADUP'])
			
			elif action[7] == '02': # Right Joystick up/ down 
				#print "Right Joystick up/down"
				if num >= 128:
					#print "up"
					if percent254 < 20: mousecontrol.updatey(sensitivity*-1)
					elif percent254 < 40: mousecontrol.updatey((sensitivity*-1)*2)
					elif percent254 < 60: mousecontrol.updatey((sensitivity*-1)*3)
					elif percent254 < 80: mousecontrol.updatey((sensitivity*-1)*4)
					elif percent254 < 90: mousecontrol.updatey((sensitivity*-1)*5)
					else: mousecontrol.updatey((sensitivity*-1)*6)
				elif num <= 127 and num != 0:
					#print "down"
					if percent128 < 20: mousecontrol.updatey(sensitivity)
					elif percent128 < 40: mousecontrol.updatey(sensitivity*2)
					elif percent128 < 60: mousecontrol.updatey(sensitivity*3)
					elif percent128 < 80: mousecontrol.updatey(sensitivity*4)
					elif percent128 < 90: mousecontrol.updatey(sensitivity*5)
					else: mousecontrol.updatey(sensitivity*6)
				else:
					#print "hooolaaaa?" #rebote o inicio?
					mousecontrol.updatey(0)
					
			elif action[7] == '03': # Right Joystick left/right
				#print "Right Joystick left/right"
				if num >= 128:
					#print "left"
					if percent254 < 20: mousecontrol.updatex(sensitivity*-1)
					elif percent254 < 40: mousecontrol.updatex((sensitivity*-1)*2)
					elif percent254 < 60: mousecontrol.updatex((sensitivity*-1)*3)
					elif percent254 < 80: mousecontrol.updatex((sensitivity*-1)*4)
					elif percent254 < 90: mousecontrol.updatex((sensitivity*-1)*5)
					else: mousecontrol.updatex((sensitivity*-1)*6)
				elif num <= 127 and num != 0:
					#print "right"
					if percent128 < 20: mousecontrol.updatex(sensitivity)
					elif percent128 < 40: mousecontrol.updatex(sensitivity*2)
					elif percent128 < 60: mousecontrol.updatex(sensitivity*3)
					elif percent128 < 80: mousecontrol.updatex(sensitivity*4)
					elif percent128 < 90: mousecontrol.updatex(sensitivity*5)
					else: mousecontrol.updatex(sensitivity*6)
				else:
					#print "hooolaaa?" #rebote o inicio?
					mousecontrol.updatex(0)

			action = []

			
