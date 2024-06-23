import asyncio
import logging
import sqlite3
import sys
import aiogram.utils.keyboard

from sqlite3 import Cursor
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandStart, Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

token = '7385233291:AAF8kMfvu-CCopRIIiqstjZXN6Nwlguw4tw'
dp = Dispatcher()
con = sqlite3.connect('excursi0', isolation_level=None)
cur = con.cursor()
form_router = Router()
dp.include_router(form_router)

def fetch_date(cur: Cursor):
    return cur.execute('SELECT DISTINCT date FROM time').fetchall()

def fetch_time(cur: Cursor, day: str, place: str):
    return cur.execute('SELECT DISTINCT time FROM time WHERE reserved = 0 AND strftime("%d", date) = :day '
                       'AND place = :place',
                       {'day': day, "place": place}).fetchall()

def right_time(cur: Cursor, time_r: str, date: str, place: str):
    right_time = cur.execute('SELECT time FROM time WHERE time = :time AND place = :place AND date = :date',
                       {'time': time_r, 'date': date, 'place': place}).fetchall()
    return len(right_time) == 0

def place_hasnt_res(cur: Cursor, place: str):
    res = cur.execute('SELECT reserved FROM time WHERE reserved = 0 AND place = :place',
                       {"place": place}).fetchall()
    return len(res) == 0
#
# def check(id: int, cur: Cursor):
#     return cur.execute('SELECT id FROM recording WHERE id = :id', {"id": id}).fetchone()

def db_table(id: int, client_name: str, excursion_place: str, excursion_date: str, excursion_time: str, quantity: int):
    cur.execute('INSERT INTO recording(id, client_name, excursion_place, excursion_date, excursion_time, quantity) VALUES (?, ?, ?, ?, ?, ?)',
                   (id, client_name, excursion_place, excursion_date, excursion_time, quantity))
    con.commit

def db_table0(place: str, date: str, time: str, reserved: bool):
    cur.execute('INSERT INTO time(place, date, time, reserved) VALUES (?, ?, ?, ?)',
                   (place, date, time, reserved))
    con.commit

def quantity_check(place):
    if place == 'Государственный музей-заповедник Гатчина':
        quantity = 2000
        return quantity

    elif place == 'Приоратский дворец':
        quantity = 2000
        return quantity

    elif place == 'Музей истории авиационного двигателестроения и ремонта':
        quantity = 1000
        return quantity

    elif place == 'Гатчинский музей-усадьба П.Е.Щербова':
        quantity = 3000
        return quantity

def quantity_check_str(place):
    if place == 'Государственный музей-заповедник Гатчина':
        quantity = '2000'
        return quantity

    elif place == 'Приоратский дворец':
        quantity = '2000'
        return quantity

    elif place == 'Музей истории авиационного двигателестроения и ремонта':
        quantity = '1000'
        return quantity

    elif place == 'Гатчинский музей-усадьба П.Е.Щербова':
        quantity = '3000'
        return quantity


class Dialog(StatesGroup):
    museum_name = State()
    signup_mus_name = State()
    signup_date = State()
    signup_name_client = State()
    signup_confirm = State()
    signup_confirm_db = State()

@form_router.message(Command('cancel'))
async def command_cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    kb = [[aiogram.utils.keyboard.KeyboardButton(text= '/menu')],
           [aiogram.utils.keyboard.KeyboardButton(text= '/commands')]]
    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    await message.answer('Отмненено.', reply_markup= keyboard)

@dp.message(Command('commands'))
async def command_cancel_handler(message: Message) -> None:
    await message.answer('/menu открывает основную информацию для записи.\n'
                         '/cancel отменяет все действия.\n'
                         '/excursions_info отображает информацию об экскурсиях\n'
                         '/signup позволяет записаться на экскурсию онлайн',
                         reply_markup= aiogram.types.reply_keyboard_remove.ReplyKeyboardRemove())

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [[aiogram.utils.keyboard.KeyboardButton(text= '/menu')]
    ]
    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    await message.answer('Доброе время суток! Вас приветствует чат-бот экскурсионного бюро.'
                         ' Здесь вы можете просмотреть информацию об экскурсиях и записаться на экскурсию онлайн. Обратите внимание:'
                         ' цена для одной группы фиксированная вне зависимости от количества участников, максимальное количество'
                         ' участников – 10 человек.'
                         ' Полная информация о доступных командах: /commands', reply_markup= keyboard)

@form_router.message(Command('menu'))
async def command_menu_handler(message: Message) -> None:
    kb = [[aiogram.utils.keyboard.KeyboardButton(text= '/excursions_info')],
          [aiogram.utils.keyboard.KeyboardButton(text= '/signup')]
    ]
    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    await message.answer('Пожалуйста, выберите подходящий вариант:\n'
                         '/excursions_info – посмотреть информацию о проводимых экскурсиях\n'
                         '/signup – записаться на экскурсию онлайн'
                         '\nИли посмотрите полный список доступных команд: /commands', reply_markup= keyboard)



@form_router.message(Command('excursions_info'))
async def command_recording_handler(message: Message, state: FSMContext):
    kb = [[aiogram.utils.keyboard.KeyboardButton(text= 'Государственный музей-заповедник Гатчина')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Приоратский дворец')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Музей истории авиационного двигателестроения и ремонта')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Гатчинский музей-усадьба П.Е.Щербова')]
          ]
    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    await message.answer('Выберите место проведения экскурсии', reply_markup= keyboard)
    await state.set_state(Dialog.museum_name)

@form_router.message(Dialog.museum_name)
async def museum_name(message: Message, state: FSMContext) -> None:
    await state.update_data(museum_name= message.text)

    kb = [[aiogram.utils.keyboard.KeyboardButton(text= '/excursions_info')],
          [aiogram.utils.keyboard.KeyboardButton(text='/signup')]
          ]
    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    match message.text:
        case 'Государственный музей-заповедник Гатчина':
            await message.answer('Время проведения экскурсий по будним дням: 9:00, 12:00, 15:00, 18:00, 21:00.\n'
                                 'По выходным: 10:00, 14:00, 18:00, 22:00.\n'
                                 'Цена билета на десять человек: 2000р.', reply_markup= keyboard)
        case 'Приоратский дворец':
            await message.answer('Время проведения экскурсий по будним дням: 10:00, 14:00, 18:00, 22:00.\n'
                                 'По выходным: 10:00, 14:00, 18:00, 22:00\n'
                                 'Цена билета на десять человек: 2000р.', reply_markup= keyboard)
        case 'Музей истории авиационного двигателестроения и ремонта':
            await message.answer('Время проведения экскурсий по будним дням: 10:00, 14:00, 18:00, 22:00.\n'
                                 'По выходным: 11:00, 15:00, 19:00\n'
                                 'Цена билета на десять человек: 1000р.', reply_markup= keyboard)
        case 'Гатчинский музей-усадьба П.Е.Щербова':
            await message.answer('Время проведения экскурсий по будним дням: 11:00, 15:00, 19:00.\n'
                                 'По выходным: 14:00, 19:00.\n'
                                 'Цена билета на десять человек: 3000р.', reply_markup= keyboard)
        case _:
            await message.answer('Неверная команда. Введите /commands, чтобы посмотреть список доступных команд.')

    x = await state.get_data()
    print(x)
    await state.set_state(None)


@form_router.message(Command('signup'))
async def command_recording_handler(message: Message, state: FSMContext):
    kb = [[aiogram.utils.keyboard.KeyboardButton(text= 'Государственный музей-заповедник Гатчина')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Приоратский дворец')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Музей истории авиационного двигателестроения и ремонта')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Гатчинский музей-усадьба П.Е.Щербова')]
          ]
    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    await message.answer('Выберите место проведения экскурсии:', reply_markup= keyboard)
    await state.set_state(Dialog.signup_mus_name)



@form_router.message(Dialog.signup_mus_name)
async def command_signup_date(message: Message, state: FSMContext) -> None:
    await state.update_data(signup_mus_name= message.text)
    info = await state.get_data()
    if place_hasnt_res(cur, info['signup_mus_name']):
        kb = [[aiogram.utils.keyboard.KeyboardButton(text='/signup')],
            [aiogram.utils.keyboard.KeyboardButton(text='/excursions_info')]]
        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer('К сожалению, на выбранное место больше нет свободных записей. '
                             'Вы можете выбрать другое место проведения экскурсии или прийти к нам в другое время.')
    else:
        kb = [[aiogram.utils.keyboard.KeyboardButton(text= s[0])] for s in fetch_date(cur)]
        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
        await message.answer('Выберите дату проведения экскурсии:', reply_markup= keyboard)
        await state.set_state(Dialog.signup_date)

@form_router.message(Dialog.signup_date)
async def command_signup_time(message: Message, state: FSMContext) -> None:
    await state.update_data(signup_date= message.text)
    info = await state.get_data()
    await state.set_state(None)
    day = info["signup_date"][-2:]
    place = info["signup_mus_name"]
    if all(len(s) == 0 for s in fetch_time(cur, day, place)):
        await message.answer('Извините, на эту дату больше нет свободных мест. Выберите другой вариант')
        kb = [[aiogram.utils.keyboard.KeyboardButton(text= s[0])] for s in fetch_time(cur, day, place)]
        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
        await state.set_state(Dialog.signup_date)
    else:
        kb = [[aiogram.utils.keyboard.KeyboardButton(text= s[0])] for s in fetch_time(cur, day, place)]
        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
        await message.answer('Выберите время проведения экскурсии:', reply_markup= keyboard)
        await state.set_state(Dialog.signup_name_client)

@form_router.message(Dialog.signup_name_client)
async def command_signup_name(message: Message, state: FSMContext) -> None:
    await state.update_data(signup_time=message.text)
    info = await state.get_data()
    if right_time(cur, info['signup_time'], info['signup_date'], info['signup_mus_name']):
        day = info["signup_date"][-2:]
        place = info["signup_mus_name"]
        kb = [[aiogram.utils.keyboard.KeyboardButton(text= s[0])] for s in fetch_time(cur, day, place)]
        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
        await message.answer('Пожалуйста, выберите время из предложенных вариантов или отмените запись: /cancel',

                             reply_markup=keyboard)
        await state.set_state(Dialog.signup_name_client)

    else:
        await state.set_state(None)
        await message.answer('Как к вам обращаться?', reply_markup= aiogram.types.reply_keyboard_remove.ReplyKeyboardRemove())
        await state.set_state(Dialog.signup_confirm)


@form_router.message(Dialog.signup_confirm)
async def command_signup_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(signup_name= message.text)
    info = await state.get_data()
    await state.set_state(None)
    kb = [[aiogram.utils.keyboard.KeyboardButton(text= 'Да')],
          [aiogram.utils.keyboard.KeyboardButton(text= 'Нет')]]

    keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard= kb, resize_keyboard= True)
    await message.answer('Ваши данные:\n' + info['signup_name'] + "\n" +
                         info['signup_mus_name'] + '\n' + info['signup_date'] + '\n' + info['signup_time'] + '\n' + str(quantity_check(info['signup_mus_name'])) + '\nВсё верно?', reply_markup= keyboard)
    await state.set_state(Dialog.signup_confirm_db)



@form_router.message(Dialog.signup_confirm_db)
async def command_signup_db(message: Message, state: FSMContext) -> None:
    await state.update_data(signup_confirm= message.text)
    info = await state.get_data()
    print(info)
    if info['signup_confirm'] == 'Да':
        id = message.from_user.id
        db_table(id = id, client_name= info['signup_name'], excursion_place= info['signup_mus_name'],
                       excursion_date= info['signup_date'], excursion_time= info['signup_time'], quantity= quantity_check_str(info['signup_mus_name']))
        cur.execute('UPDATE time SET reserved = 1 WHERE place = :place AND date = :date AND time = :time',
                          {'place': info['signup_mus_name'], 'date': info['signup_date'], 'time': info['signup_time']} )
        kb = [[aiogram.utils.keyboard.KeyboardButton(text='/menu')]]

        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer('Ваша заявка принята', reply_markup= keyboard)
    elif info['signup_confirm'] == 'Нет':
        kb = [[aiogram.utils.keyboard.KeyboardButton(text='/signup')],
              [aiogram.utils.keyboard.KeyboardButton(text='/menu')]
              ]
        keyboard = aiogram.types.reply_keyboard_markup.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
        await message.answer('Вы можете пройти регистрацию заново: /signup или еще раз просмотреть меню: /menu', reply_markup= keyboard)

    await state.clear()

@form_router.message()
async def undetected_command_handler(message: Message):
    await message.answer('Неверная команда. Введите /commands, чтобы посмотреть список доступных команд.')



async def main() -> None:
    bot = Bot(token= token, default= DefaultBotProperties(parse_mode= ParseMode.HTML))

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level= logging.INFO, stream= sys.stdout)
    asyncio.run(main())
