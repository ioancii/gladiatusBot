from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)

#close ad by getting volatile id
def close_ad():
	#loads the page
	time.sleep(2)
	#checks to see if there are any pop ups
	try:
		id = driver.find_element_by_class_name("openX_interstitial").get_attribute("id")
		#print(id)
		x_path = '//*[@id="'+id+'"]/div[1]/a'
		#print(x_path)
		driver.find_element_by_xpath(x_path).click()
	except NoSuchElementException:
		#print("no ads")
		pass

def login():
	#enters game lobby
	driver.get("https://lobby.gladiatus.gameforge.com/en_GB/hub")

	#IMPORTANT - Gives time for the site to load all elements, CAN NOT continue without this
	time.sleep(5)

	#switches from Register form (default) to Log in form
	log_in = driver.find_element_by_xpath('//*[@id="loginRegisterTabs"]/ul/li[1]/span')
	log_in.click()

	#enters email and pass (without any keyboard input for now)
	time.sleep(2)
	user_email = driver.find_element_by_css_selector('#loginForm > div:nth-child(1) > div > input[type=email]')
	email = input("Enter email: ")
	user_email.send_keys(email)

	user_password = driver.find_element_by_css_selector('#loginForm > div:nth-child(2) > div > input[type=password]')
	pwd = input("Enter password: ")
	user_password.send_keys(pwd)

	close_ad()

	#clicks log in then joins last played server
	time.sleep(2)
	log_in_btn = driver.find_element_by_xpath('//*[@id="loginForm"]/p/button[1]')
	log_in_btn.submit()

	#Accepts cookies
	time.sleep(3)
	try:
		driver.find_element_by_xpath('/html/body/div[3]/div/div/span[2]/button[2]').click()
	except NoSuchElementException:
		driver.find_element_by_xpath('/html/body/div[4]/div/div/span[2]/button[2]').click()
	
	time.sleep(2)
	last_played = driver.find_element_by_css_selector("#joinGame > button") 
	last_played.click()

	"""site opens the server in new tab, 
	so we switch to the lobby and close it,
	then set the driver on the new-opened page"""
	#print(driver.title)
	driver.switch_to.window(driver.window_handles[0])
	time.sleep(2)
	driver.close()
	time.sleep(2)
	driver.switch_to.window(driver.window_handles[0])
	player = driver.find_element_by_css_selector("#content > table > tbody > tr > td:nth-child(1) > div.player_name_bg.pngfix > div").text
	print("Starting game as", player)
	global login 
	login = True
	return player


#auto heals the player IF there's food in inventory
def eat():
	try:
		overview = driver.find_element_by_css_selector("#mainmenu > a:nth-child(1)").get_attribute('href')
		driver.get(overview)
	except:
		overview = driver.find_element_by_css_selector("#mainmenu > a.menuitem.active").get_attribute('href')
		driver.get(overview)
	
	time.sleep(5)
	avatar = driver.find_element_by_css_selector("#avatar > div.ui-droppable")

	#deschide prima pagina din inventar ?
	try:
		driver.find_element_by_css_selector("#inventory_nav > a:nth-child(1)").click()
	except:
		driver.find_element_by_css_selector("#inventory_nav > a.awesome-tabs.current").click()
	
	#function is underway
	has_eaten = False

	#checks for food in every inventory slot
	for i in range(1,41):
		try:
			if has_eaten == False:	
				try:
					#x_path = '//*[@id="'+id+'"]/div[1]/a'
					pos = '//*[@id="inv"]/div['+str(i)+']' 
					#print(driver.find_element_by_xpath(pos).get_attribute('style'))
					food = driver.find_element_by_xpath(pos)
					try:
						#drags and drops the food over avatar & changes the function status from underway to complete
						ActionChains(driver).drag_and_drop(food, avatar).perform()
						has_eaten = True
						break
					except:
						pass
				except:
					pass
			else:
				break
		#the number of divs is determined by the number of filled inventory slots
		#40 is the maximum number, but anything below it is possible
		except IndexError:
			print("No food!!!")
			break

	#checks final status of function
	if has_eaten:
		return True
	else:
		return False

#checks the hp of the character for expedition/arena
def check_hp():
	#takes percentage from the main health bar in top left
	hp_char = driver.find_element_by_xpath('//*[@id="header_values_hp_percent"]').text #-->dd_%
	hp_list = hp_char.split("%")
	hp = int(hp_list[0])
	min_hp = 30
	#print("HP="+str(hp)+"%")
	if hp > min_hp:
		return True
	elif eat():
		return True
	else:
		return False

#auto attacks first enemy on arena provinciarum
def arena(user, flag):
	#sets variable to compare the actual cooldown bar 
	#with the ideal cooldown bar
	arena_ready = 'width: 100%;'
	player = user
	#checks if hp is high enough for fighting
	if check_hp():
		pass
	else:
		if flag:
			print("Low HP. Browser closed.")
			driver.quit()
			sys.exit()
		else:
			print("HP too low for arena, no food.")
	
	#true will always be true 
	#so the loop only ends when the hp is too low
	while True:
		#tests to see if the cooldown is over 
		#by checking the width of the cooldown bar
		if driver.find_element_by_css_selector("#cooldown_bar_fill_arena").get_attribute('style') == arena_ready:
			#goes to arena - double checks to see if it's provinciarum
			#then attacks first enemy
			go_to_arena = driver.find_element_by_css_selector("#cooldown_bar_arena > a").get_attribute('href')
			driver.get(go_to_arena)
			time.sleep(0.5)
			close_ad()
			go_to_provinciarum = driver.find_element_by_css_selector("#mainnav > li > table > tbody > tr > td:nth-child(2) > a").get_attribute('href')
			driver.get(go_to_provinciarum)
			time.sleep(0.2)
			close_ad()
			attack_provinciarum = driver.find_element_by_css_selector("#own2 > table > tbody > tr:nth-child(2) > td:nth-child(4) > div").click()
			time.sleep(0.5)
			close_ad()
			try:
				pass
			except ElementClickInterceptedException: #divine box/costume/daily bonus notification after win
				driver.find_element_by_css_selector("#linkcancelnotification").click()
			win = driver.find_element_by_css_selector("#reportHeader > table > tbody > tr > td:nth-child(2)").text
			winner = win.split(":")
			print("Winner Arena:", winner[1])
		else:
			#variable gets the cooldown timer and transforms it 
			#from string hh:mm:ss to int ssssss then waits
			cooldown = driver.find_element_by_css_selector("#cooldown_bar_text_arena").text
			cd = cooldown.split(":")
			wait = int(cd[0])*3600+int(cd[1])*60+int(cd[2])
			print("wait",wait,"seconds") 
			time.sleep(wait)
			cooldown = driver.find_element_by_xpath('//*[@id="cooldown_bar_text_arena"]').text
			
		close_ad()
		if check_hp():
			pass
		else:
			if flag:
				print("Low HP. Browser closed.")
				driver.quit()
				sys.exit()
			else:
				print("HP too low for arena, no food.")
		if flag:
			pass
		else:
			break


#was complete replica of arena, but without the check_hp as hp is not needed for turma fights
def turma(flag):
	turma_ready = 'width: 100%;'
	
	while True:
		if driver.find_element_by_css_selector("#cooldown_bar_fill_ct").get_attribute('style') == turma_ready:
			go_to_turma = driver.find_element_by_css_selector("#cooldown_bar_ct > a").get_attribute('href')
			driver.get(go_to_turma)
			time.sleep(0.5)
			close_ad()
			go_to_provinciarum = driver.find_element_by_css_selector("#mainnav > li > table > tbody > tr > td:nth-child(4) > a").get_attribute('href')
			driver.get(go_to_provinciarum)
			time.sleep(0.2)
			close_ad()
			attack_provinciarum = driver.find_element_by_css_selector("#own3 > table > tbody > tr:nth-child(2) > td:nth-child(4) > div").click()
			time.sleep(0.5)                       
			close_ad()
			try:
				pass
			except ElementClickInterceptedException: #divine box/costume/daily bonus notification after win
				driver.find_element_by_css_selector("#linkcancelnotification").click()
			win = driver.find_element_by_css_selector("#reportHeader > table > tbody > tr > td:nth-child(2)").text
			winner = win.split(":")
			print("Winner Turma:", winner[1])
		else:
			cooldown = driver.find_element_by_css_selector("#cooldown_bar_text_ct").text
			cd = cooldown.split(":")
			wait = int(cd[0])*3600+int(cd[1])*60+int(cd[2])
			print("wait",wait,"seconds") 
			time.sleep(wait)
			cooldown = driver.find_element_by_xpath('//*[@id="cooldown_bar_text_ct"]').text
			##print(cooldown)
		#driver.refresh()
		close_ad()
		if flag:
			pass
		else:
			break

#auto attacks expedition enemies
def expedition(enemy, flag):
	""""Gets number of valid expedition points + max nr of expedition points.
	Also checks the cooldown bar to see if the expedition is ready or not""" 
	exp_points = driver.find_element_by_xpath('//*[@id="expeditionpoints_value_point"]').text
	max_exp_points = driver.find_element_by_xpath('//*[@id="expeditionpoints_value_pointmax"]').text
	#print("Expedition points: "+exp_points+"/"+max_exp_points)
	cooldown = driver.find_element_by_xpath('//*[@id="cooldown_bar_text_expedition"]').text
	#print(cooldown)

	go_to_exp = driver.find_element_by_css_selector("#cooldown_bar_expedition > a").get_attribute('href')
	#print(go_to_exp)
	driver.get(go_to_exp)

	if enemy == 0:
		exp_location = driver.find_element_by_css_selector("#submenu2 > a.menuitem.active").text
		print("Location: ", exp_location)
		enemies = driver.find_elements_by_class_name("expedition_box")
		for x in enemies:
			print(x.text)
		choose = int(input("Choose an enemy: "))
	else:
		choose = enemy

	#print("expedition flag:", flag)

	while int(exp_points) > 0:
		if check_hp() is True:
			pass
		else:
			if flag:
				print("Low HP. Browser closed.")
				driver.quit()
				sys.exit()
			else:
				print("HP too low for arena, no food.")

		print("Expedition points: "+exp_points+"/"+max_exp_points)
	
		#gets the expedition link, waits and accesses it
		go_to_exp = driver.find_element_by_css_selector("#cooldown_bar_expedition > a").get_attribute('href')
		#print(go_to_exp)

		#gets width attribute from the bar's style
		#width 100% means ready, <100% not ready
		cd_good = 'width: 100%;' 
		#print(driver.find_element_by_css_selector("#cooldown_bar_fill_expedition").get_attribute('style'))

		time.sleep(1)
		driver.get(go_to_exp)
		close_ad()
		if driver.find_element_by_css_selector("#cooldown_bar_fill_expedition").get_attribute('style') == cd_good:
			if choose == 1:
				driver.find_element_by_css_selector("#expedition_list > div:nth-child(1) > div:nth-child(2) > button").click()      
	
			if choose == 2:
				driver.find_element_by_css_selector("#expedition_list > div:nth-child(2) > div:nth-child(2) > button").click()      
	
			if choose == 3:
				driver.find_element_by_css_selector("#expedition_list > div:nth-child(3) > div:nth-child(2) > button").click()      

			if choose == 4:
				driver.find_element_by_css_selector("#expedition_list > div:nth-child(4) > div:nth-child(2) > button").click()
			time.sleep(1)
			try:
				pass
			except ElementClickInterceptedException: #divine box/costume/daily bonus notification after win
				driver.find_element_by_css_selector("#linkcancelnotification").click()
			win = driver.find_element_by_css_selector("#reportHeader > table > tbody > tr > td:nth-child(2)").text
			winner = win.split(":")
			print("Expedition Winner:", winner[1])
		else:
			cooldown = driver.find_element_by_css_selector("#cooldown_bar_text_expedition").text
			cd = cooldown.split(":")
			wait = int(cd[0])*3600+int(cd[1])*60+int(cd[2])
			print("wait",wait,"seconds") 
			#driver.refresh()  
			time.sleep(wait)
			#exp_points = driver.find_element_by_xpath('//*[@id="expeditionpoints_value_point"]').text
			cooldown = driver.find_element_by_xpath('//*[@id="cooldown_bar_text_expedition"]').text
			#print(cooldown)
			driver.refresh()
		close_ad()

		if flag:
			exp_points = driver.find_element_by_xpath('//*[@id="expeditionpoints_value_point"]').text
		else:
			break

#auto dungeon attacks
def dungeon(flag):
	dng_points = driver.find_element_by_xpath('//*[@id="dungeonpoints_value_point"]').text
	max_dng_points = driver.find_element_by_xpath('//*[@id="dungeonpoints_value_pointmax"]').text

	go_to_dng = driver.find_element_by_css_selector("#cooldown_bar_dungeon > a").get_attribute('href')
	driver.get(go_to_dng)

	#src = "9387/img/combatloc.gif"
	def attack():
		attacked = False
		img_list = driver.find_elements_by_tag_name("img")
		for element in img_list:
			if "combatloc.gif" in element.get_attribute("src"):
				#print ("gif located in:", element, " ", element.get_attribute("src"))
				element.click()
				#print("click")
				attacked = True
				return attacked	

	close_ad()
	cd_good = 'width: 100%;'

	while int(dng_points) > 0:
		time.sleep(1)	
		driver.get(go_to_dng)

		if driver.find_element_by_css_selector("#cooldown_bar_fill_dungeon").get_attribute('style') == cd_good:
			
			if attack():
				pass
			else:
				#enter dungeon on advanced
				driver.find_element_by_css_selector("#content > div:nth-child(3) > div > form > table > tbody > tr > td:nth-child(2) > input").click()
				time.sleep(1)
				attack()
			time.sleep(1)
			close_ad()
			
			win = driver.find_element_by_css_selector("#reportHeader > table > tbody > tr > td:nth-child(2)").text
			winner = win.split(":")
			print("Dungeon Winner:", winner[1])

		else:
			cooldown = driver.find_element_by_css_selector("#cooldown_bar_text_dungeon").text
			cd = cooldown.split(":")
			wait = int(cd[0])*3600+int(cd[1])*60+int(cd[2])
			print("wait",wait,"seconds")
			time.sleep(wait)

		if flag:
			pass
		else:
			break
		
#auto repeat mode 
#last accessed expedition/dungeon for now
def rep(flag, user):
	repeat = flag
	player = user
	
	exp_enemy = int(input("Choose expedition enemy:"))
	
	while True: #cat timp sa ruleze? vreau sa se opreasca cumva?
		cd = []
		if check_hp():
			do_exp = True
			do_arena = True
		else:
			do_exp = False
			do_arena = False

		exp_points = int(driver.find_element_by_xpath('//*[@id="expeditionpoints_value_point"]').text)
		dng_points = int(driver.find_element_by_xpath('//*[@id="dungeonpoints_value_point"]').text)
		
		if do_exp and exp_points > 0:
			expedition(exp_enemy, repeat)
			exp_cd = driver.find_element_by_css_selector("#cooldown_bar_text_expedition").text
			try:
				exp_cd_list = exp_cd.split(":")
				cd_exp = int(exp_cd_list[0])*3600+int(exp_cd_list[1])*60+int(exp_cd_list[2])
				cd.append(cd_exp)
			except:
				cd_exp = 0
				cd.append(cd_exp)

		if dng_points > 0:
			dungeon(repeat)
			dng_cd = driver.find_element_by_css_selector("#cooldown_bar_text_dungeon").text
			try:
				dng_cd_list = dng_cd.split(":")
				cd_dng = int(dng_cd_list[0])*3600+int(dng_cd_list[1])*60+int(dng_cd_list[2])
				cd.append(cd_dng)
			except: 
				cd_dng = 0
				cd.append(cd_dng)

		if do_arena:
			arena(player, repeat)
			arena_cd = driver.find_element_by_css_selector("#cooldown_bar_text_arena").text
			try:
				arena_cd_list = arena_cd.split(":")
				cd_arena = int(arena_cd_list[0])*3600+int(arena_cd_list[1])*60+int(arena_cd_list[2])
				cd.append(cd_arena)
			except: 
				cd_arena = 0
				cd.append(cd_arena)
		
		turma(repeat)
		turma_cd = driver.find_element_by_css_selector("#cooldown_bar_text_ct").text
		try:
			turma_cd_list = turma_cd.split(":")
			cd_turma = int(turma_cd_list[0])*3600+int(turma_cd_list[1])*60+int(turma_cd_list[2])
			cd.append(cd_turma)
		except: 
			cd_turma = 0
			cd.append(cd_turma)

		cd = sorted(cd)
		print("Wait", cd[0], "seconds...")
		time.sleep(cd[0])

#allows the user to choose the playing mode
def choose_mode():
	global mode
	global repeat
	mode = int(input("Desired mode?\n0 - none;\n1 - auto expedition;\n2 - auto arena;\n3 - auto circus;\n4 - auto dungeon;\n5 - Full package;\nDecision: "))
	if mode == 1:
		repeat = True
		expedition(0, repeat)
	elif mode == 2 and level > 1:
		repeat = True
		arena(repeat)
	elif mode == 3 and level > 9:
		repeat = True
		turma(repeat)
	elif mode == 4 and level > 9:
		repeat = True
		dungeon(repeat)
	elif mode == 5:
		repeat = False
		rep(repeat, user)
	else:
		print("Good bye!")
		driver.quit()

#starts the script and saves the player name & level
def start_app():
	print("Start time:",time.strftime("%H:%M:%S", time.localtime()))
	#user log in
	global user
	user = login()

	global level
	level = int(driver.find_element_by_xpath('//*[@id="header_values_level"]').text)
	
	while login: 
		try:
			choose_mode()
		except:
			print("Something went wrong. Back to mode selection.")
			choose_mode()

if __name__ == "__main__":
	start_app()
