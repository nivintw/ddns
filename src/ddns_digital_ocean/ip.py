import json
import logging
import time
import urllib.request
from datetime import datetime

import requests
from rich import print

from . import constants
from .api_key_helpers import get_api
from .database import connect_database

conn = connect_database(constants.database_path)


def get_ip():
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(ip4_server) FROM ipservers")
    count = cursor.fetchone()[0]
    if count != 0:
        cursor.execute("SELECT ip4_server from ipservers")
        server = cursor.fetchone()
        server = server[0]
        try:
            current_ip = urllib.request.urlopen(server).read().decode("utf-8")  # noqa: S310
            return current_ip
        except Exception as e:
            error = str(e)
            logging.error(time.strftime("%Y-%m-%d %H:%M") + " - Error : " + str(e))
            return error
    else:
        return None


def updateip(force):
    apikey = get_api()
    current_ip = get_ip()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM subdomains")
    count = cursor.fetchone()[0]
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    updated = None
    if count == 0:
        print(
            "[red]Error: [/red]There are no dynamic domains active."
            " Start by adding a new domain with [i]ddns -s test.example.com[/i]"
        )
    else:
        cursor.execute("SELECT id,active FROM subdomains")
        rows = cursor.fetchall()
        for i in rows:
            cursor.execute(
                "SELECT name "
                "FROM domains "
                "WHERE id like (SELECT main_id from subdomains WHERE id = ?)",
                (i[0],),
            )
            domain_info = cursor.fetchone()
            domain_name = str(domain_info[0])
            domain_status = i[1]
            subdomain_id = str(i[0])
            # Chek if an update is required
            if domain_status == 1:
                req = urllib.request.Request(
                    "https://api.digitalocean.com/v2/domains/"
                    + domain_name
                    + "/records/"
                    + subdomain_id
                )
                req.add_header("Content-Type", "application/json")
                req.add_header("Authorization", "Bearer " + apikey)
                current = urllib.request.urlopen(req)  # noqa: S310
                remote = current.read().decode("utf-8")
                remoteData = json.loads(remote)
                remoteIP4 = remoteData["domain_record"]["data"]
                if remoteIP4 != current_ip or force is True and domain_status == 1:
                    updated = True
                    data = {"type": "A", "data": current_ip}
                    headers = {
                        "Authorization": "Bearer " + apikey,
                        "Content-Type": "application/json",
                    }
                    response = requests.patch(
                        "https://api.digitalocean.com/v2/domains/"
                        + domain_name
                        + "/records/"
                        + subdomain_id,
                        data=json.dumps(data),
                        headers=headers,
                        timeout=60,
                    )
                    if str(response) != "<Response [200]>":
                        logging.error(
                            time.strftime("%Y-%m-%d %H:%M")
                            + " - Error updating ("
                            + str(domain_name)
                            + ") : "
                            + str(response.content)
                        )
                    else:
                        cursor.execute(
                            "UPDATE subdomains SET current_ip4=? WHERE id = ?",
                            (
                                current_ip,
                                subdomain_id,
                            ),
                        )
                        cursor.execute(
                            "UPDATE subdomains SET last_updated=? WHERE id = ?",
                            (
                                now,
                                subdomain_id,
                            ),
                        )
                        cursor.execute(
                            "UPDATE subdomains SET last_checked=? WHERE id = ?",
                            (
                                now,
                                subdomain_id,
                            ),
                        )
                        conn.commit()
                else:
                    cursor.execute(
                        "UPDATE subdomains SET last_checked=? WHERE id = ?",
                        (
                            now,
                            subdomain_id,
                        ),
                    )
                    conn.commit()

    if updated is None:
        logging.info(time.strftime("%Y-%m-%d %H:%M") + " - Info : No updated necessary")
    else:
        logging.info(
            time.strftime("%Y-%m-%d %H:%M")
            + " - Info : Updates done. Use ddns -l domain.com to check domain"
        )
