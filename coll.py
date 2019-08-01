#!/opt/datadog-agent/embedded/bin/python
import requests
import socket
import psutil   # v2.2.1


# YOU SHOULD KNOW: IT IS HARD TO TELL EVERY PROCESS FROM EACH OTHER

# Duplicated process detected: /usr/sbin/httpd -DFOREGROUND| pid: 1060410
# Duplicated process detected: /usr/sbin/httpd -DFOREGROUND| pid: 1060411
# Duplicated process detected: /usr/sbin/httpd -DFOREGROUND| pid: 1060412
# Duplicated process detected: /usr/sbin/httpd -DFOREGROUND| pid: 1060413
# Duplicated process detected: /usr/sbin/httpd -DFOREGROUND| pid: 1060414
# Duplicated process detected: -bash| pid: 1894438
# Duplicated process detected: -bash| pid: 1895344
# Duplicated process detected: -bash| pid: 1895380

api = "http://20.26.37.208:8080/api/coll"
hostname = socket.gethostname()

user_usage = {}
process_status = {}


for p in psutil.process_iter():
    user = p.username()
    usage_cpu = p.cpu_percent()
    usage_mem = p.memory_info_ex().rss
    num_threads = p.num_threads()
    num_fds = p.num_fds()
    pcmd = " ".join(p.cmdline())
    pid = p.pid


    if user in user_usage:
        user_usage[user]['usage_cpu'] += usage_cpu
        user_usage[user]['usage_mem'] += usage_mem
        user_usage[user]['num_threads'] += num_threads
        user_usage[user]['num_fds'] += num_fds
    else:
        user_usage[user] = {}
        user_usage[user]['usage_cpu'] = usage_cpu
        user_usage[user]['usage_mem'] = usage_mem
        user_usage[user]['num_threads'] = num_threads
        user_usage[user]['num_fds'] = num_fds

    if pcmd:
        if pcmd in process_status:
            print("Duplicated process detected: {}| pid: {}".format(pcmd, pid))
        else:
            process_status[pcmd] = {}
            process_status[pcmd]["pid"] = pid
            process_status[pcmd]["cpu"] = usage_cpu
            process_status[pcmd]["mem"] = usage_mem
            process_status[pcmd]['num_conns'] = len(p.connections())
            # process_status[pcmd]["connections"] = []
            # for connection in p.connections():
            #     if not connection.raddr:
            #         process_status[pcmd]["connections"].append(
            #             [connection.laddr.ip, connection.laddr.port, '', '', connection.status])
            #     else:
            #         process_status[pcmd]["connections"].append(
            #             [connection.laddr.ip, connection.laddr.port, connection.raddr.ip, connection.raddr.port, connection.status])


r = requests.post(api, json={
        "hostname": hostname,
        "user_usage": user_usage,
        "process_status": process_status
    })

print(r.text)