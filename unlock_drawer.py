import subprocess
import database

def execute_gpio_control(pin, duration):
    # Command to run the GPIO control script
    command = ['python', 'gpio_controller.py', str(pin), str(duration)]

    # Run the command in a separate process
    subprocess.Popen(command)

def unlock_drawer(user_id, drawer):
    print("Unlocking drawer")

    # if drawer == -1:
    #     execute_gpio_control(17, 60)
