import pymysql
import json
import datetime
from django.views.decorators.csrf import csrf_exempt

db = {
    "host": "",
    "port": 3306,
    "user": "",
    "password": "",
    "db": "business_monitor"
}

# api/web
@csrf_exempt
def apiweb(request):
    update_time = datetime.datetime.now()
    with pymysql.connect(**db) as cursor:
        items = json.loads(request.body)
        for item in items:
            local_ip = item['local_ip']
            remote_ip = item['remote_ip']
            update_status = item['update_status']
            response_time = item['response_time']
            if not cursor.execute("SELECT * FROM node_conn_status WHERE local_ip=%s AND remote_ip=%s",  (local_ip, remote_ip)):
                cursor.execute("INSERT INTO node_conn_status(local_ip, remote_ip, update_status, response_time, update_time) \
                    VALUES (%s, %s, %s, %s, %s)", 
                    (local_ip, remote_ip, update_status, response_time, update_time)
                    )
            else:
                cursor.execute("UPDATE node_conn_status SET update_status=%s, response_time=%s, update_time=%s", 
                    (update_status, response_time, update_time)
                    )
    return JsonResponse("ok", safe=False)


# api/coll
@csrf_exempt
def apicoll(request):

    data = json.loads(request.body)
    hostname = data.get("hostname")
    user_usage = data.get("user_usage")
    process_status = data.get("process_status")

    datetime_now = datetime.datetime.now()

    with pymysql.connect(**db) as cursor:

        for pcmd in process_status:

            pid = process_status[pcmd]["pid"]
            cpu = process_status[pcmd]["cpu"]
            mem = process_status[pcmd]["mem"]
            num_conns = process_status[pcmd]['num_conns']

            if  cursor.execute(
                    "SELECT * FROM process_status_current WHERE hostname = %s AND pcmd = %s", (hostname, pcmd)
                ):

                cursor.execute(
                    "UPDATE process_status_current SET pid=%s, cpu=%s, mem=%s, num_conns=%s, create_time=%s, update_time=%s WHERE hostname=%s AND pcmd=%s",
                    (pid, cpu, mem, num_conns, datetime_now, datetime_now, hostname, pcmd)
                )
            else:
                cursor.execute(
                    "INSERT INTO process_status_current(pid, cpu, mem, num_conns, update_time, create_time, hostname, pcmd) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (pid, cpu, mem, num_conns, datetime_now, datetime_now, hostname, pcmd)
                )

        for user in user_usage:

            usage_cpu =  user_usage[user]['usage_cpu']
            usage_mem = user_usage[user]['usage_mem']
            num_threads =  user_usage[user]['num_threads']
            num_fds = user_usage[user]['num_fds']

            if cursor.execute(
                    "SELECT * FROM user_usage_current WHERE hostname=%s AND user=%s",
                    (hostname, user)
                ):

                cursor.execute(
                    "UPDATE user_usage_current SET usage_cpu=%s, usage_mem=%s, num_threads=%s, num_fds=%s, create_time=%s, update_time=%s WHERE hostname=%s AND user=%s",
                    (usage_cpu, usage_mem, num_threads, num_fds, datetime_now, datetime_now, hostname, user)
                )
            else:
                cursor.execute("INSERT INTO user_usage_current (usage_cpu, usage_mem, num_threads, num_fds, create_time, update_time, hostname, user) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (usage_cpu, usage_mem, num_threads, num_fds, datetime_now, datetime_now, hostname, user)   
                )
    return JsonResponse("ok", safe=False)







