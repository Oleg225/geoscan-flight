from pioneer_sdk import Pioneer
import time

drone = Pioneer(ip='127.0.0.1', mavlink_port=8000)

HEIGHT = 1.5

waypoints = [
    (-1.73, 5.17, HEIGHT),
    (-1.70, 0.76, HEIGHT),
    ( 1.55, 0.66, HEIGHT),
    ( 1.66,-4.46, HEIGHT),
    ( 4.62,-4.49, HEIGHT),  
]

print("Армирование...")
drone.arm()
time.sleep(1)

print("Взлёт...")
drone.takeoff()
time.sleep(5)

for i, (x, y, z) in enumerate(waypoints):
    print(f"Летим в точку {i+1}: x={x}, y={y}")
    drone.go_to_local_point(x=x, y=y, z=z, yaw=0)
    while not drone.point_reached():
        time.sleep(0.1)
    print(f"Точка {i+1} достигнута!")
    time.sleep(1)

print("Посадка...")
drone.land()
time.sleep(5)
print("Готово!")
