from airflow.sdk import dag, task
from datetime import datetime
import time

@dag(schedule=None, start_date=datetime(2023, 1, 1), catchup=False, tags=['goodtag'])
def yawa_dag():
    
    @task
    def first_task():
        #sleep for 30 seconds
        time.sleep(3)

        lol = 12324 * 23142
        if lol > 1000000:
            print("lol is greater than 1000000")
        else:
            print("lol is less than or equal to 1000000")
        result = "im your first hello"
        return result

    @task
    def second_task(input_value):
        time.sleep(3)
        result = f"im your second hello, received: {input_value}"
        return result
    
    @task
    def third_task(input_value):
        time.sleep(3)
        result = f"im your third hello, received: {input_value}"
        return result
    
    first_hello = first_task()
    second_hello = second_task(first_hello)
    third_hello = third_task(second_hello)

yawa_dag()