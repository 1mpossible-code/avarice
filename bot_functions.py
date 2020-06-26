import datetime
import json
import re
import inscriptions
from classes.cart import Cart
from classes.catalog import Catalog
from classes.order import Order
from database import *
import logging


log = logging.getLogger(__name__)

# Creating new Catalog
catalog = Catalog(None)
catalog_group = dict()
# Creating new making_order
making_order_group = dict()


def handler(bot, types, message, call):
    creating_unique_catalog(message, call)
    if message and message.text:
        checking_messages(bot, message, types)
    elif call and call.message:
        checking_new_callback_data(bot, call, types)


def creating_unique_catalog(message, call):
    global catalog
    if message is not None or call is not None:
        if message:
            catalog = Catalog(message.chat.id)
        elif call.message.chat.id:
            catalog = Catalog(call.message.chat.id)
    if message is not None or call is not None:
        try:
            if catalog_group[catalog.chat_id] is None:
                print(catalog_group)
        except KeyError:
            catalog_group[catalog.chat_id] = catalog
        if message and catalog_group[catalog.chat_id] is not None:
            catalog = catalog_group[message.chat.id]
        elif call and catalog_group[catalog.chat_id] is not None:
            catalog = catalog_group[call.message.chat.id]


def sending_start_message(bot, message, types):
    markup = creating_start_markup_buttons(types)
    with open("images/greeting/AnimatedSticker.tgs", "rb") as sticker:
        bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id, 'Привет, {0.first_name}, рады '.format(message.from_user) +
                     'видеть тебя в нашем боте!\nЭто магазин <b>' +
                     '{0.first_name}</b>.\nВыбирай товары в каталоге,'.format(bot.get_me()) +
                     ' а затем оформляй заказ в ' +
                     'корзине :)', parse_mode='html', reply_markup=markup)


def start_func(message):
    if not if_user_exists(message.chat.id):
        new_user(message.chat.id, message.from_user.first_name, message.from_user.username, None)


def sending_help_message(bot, message):
    log.info(f"{message.from_user.username} sent a /help command")
    bot.send_message(message.chat.id, inscriptions.help_text, parse_mode='html')


def creating_start_markup_buttons(types):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton(inscriptions.catalog)
    item2 = types.KeyboardButton(inscriptions.cart)
    item3 = types.KeyboardButton(inscriptions.search)
    item4 = types.KeyboardButton(inscriptions.orders)
    item5 = types.KeyboardButton(inscriptions.faq)
    item6 = types.KeyboardButton(inscriptions.contacts)
    markup.add(item1, item2, item3, item4, item5, item6)
    return markup


def checking_messages(bot, message, types):
    # Making order
    if get_making_order_by_id(message.chat.id):
        global making_order_group
        try:
            steps = making_order_group[message.chat.id][0]
            params = making_order_group[message.chat.id][1]
            checking_order_creating_steps(bot, message, steps, params)
        except KeyError:
            making_order_group[message.chat.id] = [
                {
                    "city": False,
                    "number_of_departament": False,
                    "full_name": False,
                    "number": False,
                    "payment_system": False
                },
                {
                    "city": None,
                    "number_of_departament": None,
                    "full_name": None,
                    "number": None,
                    "payment_system": None
                }
            ]
            steps = making_order_group[message.chat.id][0]
            params = making_order_group[message.chat.id][1]
            checking_order_creating_steps(bot, message, steps, params)
    else:
        # Main buttons
        if message.text == inscriptions.catalog:
            catalog_function(bot, message, types)
        elif message.text == inscriptions.cart:
            cart_function(bot, message, types)
        elif message.text == inscriptions.search:
            bot.send_message(message.chat.id, inscriptions.search_text, parse_mode='html')
        elif message.text == inscriptions.orders:
            orders_function(bot, types, message)
        elif message.text == inscriptions.faq:
            faq_function(bot, message)
        elif message.text == inscriptions.contacts:
            contacts_function(bot, message)
        else:
            bot.send_message(message.chat.id, inscriptions.unrecognized_message, parse_mode='html')


def checking_order_creating_steps(bot, message, steps, params):
    if not steps["city"]:
        params["city"] = message.text
        steps["city"] = True
    elif not steps["number_of_departament"]:
        bot.send_message(message.chat.id, inscriptions.number_of_departament)
        steps["number_of_departament"] = True
    elif not steps["full_name"]:
        bot.send_message(message.chat.id, inscriptions.full_name)
        params["number_of_departament"] = message.text
        steps["full_name"] = True
    elif not steps["number"]:
        bot.send_message(message.chat.id, inscriptions.number)
        params["full_name"] = message.text
        steps["number"] = True
    elif not steps["payment_system"]:
        bot.send_message(message.chat.id, inscriptions.payment_system, parse_mode='html')
        params["number"] = message.text
        steps["payment_system"] = True
    else:
        params["payment_system"] = message.text
        bot.send_message(message.chat.id, inscriptions.done, parse_mode='html')
        user = get_user_by_id(message.chat.id)
        date = datetime.datetime.now()
        date_id = re.search(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", str(date))
        date_id = date_id.group()
        cart = Cart(message.chat.id)
        new_order(message.chat.id, json.dumps({
            "Chat ID": message.chat.id,
            "Phone": params["number"],
            "Name": user[1],
            "Username": user[2],
        }), cart.return_cart_json(), date_id, 0, json.dumps(params))
        set_making_order_status_to_user(message.chat.id, 0)


def send_to_operators():
    log.debug("Sending to operator")


def catalog_function(bot, message, types):
    catalog_first_prod(bot, message, types)


def catalog_first_prod(bot, message, types):
    try:
        with open(catalog.products[catalog.current_prod][4], 'rb') as photo:
            markup = catalog_markup_create(message.chat.id, catalog.products,
                                           catalog.current_prod, catalog.prod_amount, types)
            bot.send_photo(message.chat.id, photo,
                           "<b>{0[1]}</b>\n{0[2]}".format(catalog.products[catalog.current_prod]),
                           reply_markup=markup, parse_mode='html')
    except IndexError as e:
        print(e)
        log.error("No products in catalog")
        bot.send_message(message.chat.id, inscriptions.no_prods_in_catalog)


def catalog_update(bot, call, types):
    markup = catalog_markup_create(call.message.chat.id, catalog.products,
                                   catalog.current_prod, catalog.prod_amount, types)
    bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id,
                             caption="<b>{0[1]}</b>\n{0[2]}".format(catalog.products[catalog.current_prod]),
                             reply_markup=markup, parse_mode="html")


def catalog_markup_create(call, products, current_prod_catalog, last_prod, types):
    products_in_cart = how_many_in_cart(call, products, current_prod_catalog)
    markup = types.InlineKeyboardMarkup(row_width=1)
    item = types.InlineKeyboardButton(products_in_cart + inscriptions.currency + " " +
                                      str(products[current_prod_catalog][3]) + " " +
                                      inscriptions.add_to_cart + " " +
                                      products[current_prod_catalog][1], callback_data="to_cart")
    markup.add(item)
    markup.row_width = 3
    item1 = types.InlineKeyboardButton("←", callback_data="prev")
    item2 = types.InlineKeyboardButton(f"{current_prod_catalog + 1} / {last_prod + 1}", callback_data="nothing")
    item3 = types.InlineKeyboardButton("→", callback_data="next")
    markup.add(item1, item2, item3)
    return markup


def how_many_in_cart(chat_id, products, current_prod_catalog):
    cart = Cart(chat_id)
    products_in_cart = cart.items
    try:
        cur_prod_amount = products_in_cart[str(products[current_prod_catalog][0])][7]["amount"]
        cur_prod_amount_string = f"({cur_prod_amount}) "
        log.error(cur_prod_amount_string)
        return cur_prod_amount_string
    except TypeError:
        return ""
    except KeyError:
        return ""


def checking_new_callback_data(bot, call, types):
    if call.message:
        callback_data_catalog(bot, call, types)
        callback_data_cart(bot, call)
        callback_data_order(bot, call)


def callback_data_catalog(bot, call, types):
    if call.data == "to_cart":
        callback_to_cart(call)
        catalog_update(bot, call, types)
    elif call.data == "next":
        callback_next_prod()
        catalog_update(bot, call, types)
    elif call.data == "prev":
        callback_prev_prod()
        catalog_update(bot, call, types)


def callback_to_cart(call):
    cart = Cart(call.message.chat.id)
    cart.add_item(catalog.products[catalog.current_prod])
    cart.set_cart_to_user()


def callback_next_prod():
    if catalog.current_prod == catalog.prod_amount:
        catalog.current_prod = 0
    else:
        catalog.current_prod += 1


def callback_prev_prod():
    if catalog.current_prod == 0:
        catalog.current_prod = catalog.prod_amount
    else:
        catalog.current_prod -= 1


def cart_function(bot, message, types):
    items_array = make_items_array(message)
    if items_array is not None:
        items_text = items_array[0]
        result_sum = items_array[1]
        markup = cart_markup_create(types)
        bot.send_message(message.chat.id, "<b>Корзина</b>\n\n---\n{0}".format(items_text) +
                                          "---\n\n<b>Итого: </b>{0}".format(result_sum) +
                         inscriptions.currency, reply_markup=markup, parse_mode='html')
    elif items_array is None:
        bot.send_message(message.chat.id, inscriptions.cart_is_empty, parse_mode='html')


def make_items_array(message):
    cart = Cart(message.chat.id)
    items = cart.items
    items_arr = list()
    items_text = str()
    items_sum = 0
    try:
        for item in items:
            amount = items[item][7]['amount']
            price = items[item][3]
            local_sum = amount * price
            items_text += f"<b>{items[item][1]}</b>\n{amount} " \
                          f"{inscriptions.amount} x {price}{inscriptions.currency} = {local_sum}\n"
            items_sum += local_sum
        if items_text == "":
            return None
        else:
            items_arr.append(items_text)
            items_arr.append(items_sum)
            return items_arr
    except TypeError:
        return None


def cart_markup_create(types):
    markup = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton(inscriptions.clear_cart, callback_data="clear_cart")
    item2 = types.InlineKeyboardButton(inscriptions.make_order, callback_data="make_order")
    markup.add(item1, item2)
    return markup


def callback_data_cart(bot, call):
    if call.data == "clear_cart":
        callback_clear_cart(call)
        cart_update(bot, call)
    elif call.data == "make_order":
        callback_make_order(bot, call)
        cart_update(bot, call)


def cart_update(bot, call):
    cart = Cart(call.message.chat.id)
    if cart.items == {}:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, inscriptions.cart_is_empty, parse_mode='html')


def callback_clear_cart(call):
    cart = Cart(call.message.chat.id)
    cart.items = None
    cart.set_cart_to_user()


def callback_make_order(bot, call):
    start_making_order(bot, call)


def start_making_order(bot, call):
    # Город доставки, номер отделения, полное имя пользователя, номер телефона, оплата
    bot.send_message(call.message.chat.id, inscriptions.city_of_dislocation)
    set_making_order_status_to_user(call.message.chat.id, 1)


def callback_data_order(bot, call):
    orders = Order(call.message.chat.id)
    # If order in user`s order list
    for order in orders.orders:
        if call.data == order[0]:
            bot.send_message(call.message.chat.id, order.return_items_note_str())


def orders_function(bot, types, message):
    order = Order(message.chat.id)
    if not order.is_orders():
        bot.send_message(message.chat.id, inscriptions.no_orders_text)
    elif order.is_orders():
        markup = create_orders_markup(types, message)
        bot.send_message(message.chat.id, inscriptions.some_orders_here, reply_markup=markup)


def create_orders_markup(types, message):
    orders = Order(message.chat.id)
    markup = types.InlineKeyboardMarkup(row_width=2)
    for order in orders.orders:
        item = types.InlineKeyboardButton(order[0], callback_data=order[0])
        markup.add(item)
    return markup


def faq_function(bot, message):
    bot.send_message(message.chat.id, inscriptions.faq_text, parse_mode='html')


def contacts_function(bot, message):
    bot.send_message(message.chat.id, inscriptions.contacts_text, parse_mode='html')
