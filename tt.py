import math


def circular_mean(hours):
    # Convert hours to radians
    # What is the 15?! (24*15=360)
    radians = [math.radians(hour) for hour in hours]

    # Calculate the sum of sin and cos values
    sin_sum = sum([math.sin(rad) for rad in radians])
    cos_sum = sum([math.cos(rad) for rad in radians])

    # Calculate the circular mean using arctan2
    mean_rad = math.atan2(sin_sum, cos_sum)

    # Convert the mean back to hours
    mean_hour = math.degrees(mean_rad)

    return mean_hour



hours = [351, 10]
mean_hour = circular_mean(hours)
print("Second Circular mean:", round(mean_hour, 2))
