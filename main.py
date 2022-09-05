import json
import time
import log as logger
import requests
from jsonpath import jsonpath

import send_message


wishes_list = [
    {"US_mercer_extra_small": {
        "https_dict": {"https": "https://www.michaelkors.com/server/productinventory?productList=US_35T1GM9C0I"},
        "wishes": ["490069615", "490048706", "490048704"],
        "real_net": "https://www.michaelkors.com/mercer-extra-small-logo-and-leather-crossbody-bag/_/R-US_35T1GM9C0I?color=9150"}},
    {"US_mercer_medium": {
        "https_dict": {"https": "https://www.michaelkors.com/server/productinventory?productList=US_35S1GM9M2B"},
        "wishes": ["490027196", "490027187", "490027188"],
        "real_net": "https://www.michaelkors.com/mercer-medium-logo-and-leather-accordion-crossbody-bag/_/R-US_35S1GM9M2B"}},
    # {"CA_mercer_extra_small": {
    #     "https_dict": {"https": "https://www.michaelkors.com/server/productinventory?productList=US_35T1GM9C0I"},
    #     "wishes": ["490069615", "490048706", "490048704"],
    #     "real_net": "https://www.michaelkors.com/server/productinventory?productList=US_35T1GM9C0I"}},
    # {"CA_mercer_medium": {
    #     "https_dict": {"https": "https://www.michaelkors.com/server/productinventory?productList=US_35T1GM9C0I"},
    #     "wishes": ["490069615", "490048706", "490048704"],
    #     "real_net": "https://www.michaelkors.com/server/productinventory?productList=US_35T1GM9C0I"}},
]


def get_json_list(http_str, bag_type):
    headers = {
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1.5) ",
    }
    # 设置一个会话session对象s
    s = requests.session()
    resp = s.get(http_str, headers=headers)
    logger.info(bag_type + ":Json begin loading...")
    str_dic = json.loads(resp.text)
    return str_dic


def get_product_status(product_dict):
    logger.info("get_product_status")
    return product_dict["product"]


def get_sku_status(sku_dict):
    logger.info("get_sku_status")
    return sku_dict["SKUs"]


def get_sku_index(sku_list, index):
    logger.info("get_sku_index")
    return sku_list[index]


def get_inventory_from_sku(sku_dict):
    logger.info("get_inventory_from_sku")
    return sku_dict["inventory"][0]


def get_inventory_status_label(inventory_dict):
    logger.info("get_inventory_status_label")
    return inventory_dict["inventoryStatusLabel"]


def get_sku_identifier(str_dict, bag_index):
    logger.info("get_sku_identifier start...")
    sku_dict = get_product_status(str_dict)
    sku_list = get_sku_status(sku_dict)
    sku_identifier = get_sku_index(sku_list, bag_index)
    logger.info("get_sku_identifier success.")
    return sku_identifier


def get_inventory_status(sku_identifier):
    logger.info("get_inventory_status start...")
    inventory = get_inventory_from_sku(sku_identifier)
    inventory_status_label = get_inventory_status_label(inventory)
    logger.info("get_inventory_status success.")
    return inventory_status_label


def get_wishes_status(http_dict):
    logger.info("get_wishes_status start...")
    status_list = {}
    for key, value in http_dict.items():
        logger.info("value:" + value)
        json_list = get_json_list(value, key)
        num_of_identifier = len(json_list['product']['SKUs'])
        logger.info("num_of_identifier:" + str(num_of_identifier))
        for i in range(num_of_identifier):
            logger.info("num_of_identifier:" + str(num_of_identifier) + ",now is:" + str(i))
            sku_identifier = get_sku_identifier(json_list, i)
            logger.info("sku_identifier:" + sku_identifier["identifier"])
            inventory_status = get_inventory_status(sku_identifier)
            logger.info("inventory_status:" + str(inventory_status))
            status_list[sku_identifier['identifier']] = inventory_status
    logger.info("get_wishes_status success.")
    return status_list


def check_wish_bag_status_change(https_dict, wish_list, msg, real_net):
    logger.info("check_wish_bag_status_change start...")
    bag_state_dict = get_wishes_status(https_dict)
    logger.info("bag_state_dict:" + str(bag_state_dict))
    message_info = ""
    for key, value in bag_state_dict.items():
        if wish_list.__contains__(key):
            if value != "Out of Stock":
                message_info = message_info + msg + "\n"
                message_info = message_info + key + ":" + value + "\n"
                message_info = message_info + "purchase link:" + real_net + "\n"
                logger.info("message_info:" + message_info)
    logger.info("return message_info")
    return message_info


def send_email(bag_wishes_list):
    index = len(bag_wishes_list)
    send_message_info = ""
    for i in range(index):
        for k, v in wishes_list[i].items():
            net_dict = v["https_dict"]
            logger.info("Start load exp_bag:" + k)
            logger.info(net_dict)
            bag_wishes_list = v["wishes"]
            logger.info(",".join(bag_wishes_list))
            real_net = v["real_net"]
            logger.info("real_net:" + real_net)
            result = check_wish_bag_status_change(net_dict, bag_wishes_list, k, real_net)
            if result != "":
                send_message_info += result
                send_message_info += "\n"
    print("--------------send_message_info--------------")
    print(send_message_info)
    print("--------------send_message_info--------------")
    if send_message_info != "":
        logger.info("The bag you want is in stock, start send email...")
        send_message.send_qq_email(send_message_info)
        logger.info("send email success.")
    else:
        logger.warning("The bag you want is still out of stock")


while True:
    time_now = time.strftime("%H", time.localtime())  # 刷新
    if time_now == "23":  # 此处设置每天定时的时间
        send_email(wishes_list)
        subject = time.strftime("%Y-%m-%d %H:%M:%S",
                                time.localtime()) + ":Regularly check the inventory of the desired bags"
        logger.info(subject)
        time.sleep(60)  # 因为以秒定时，所以暂停60秒，使之不会在60秒内执行多次
