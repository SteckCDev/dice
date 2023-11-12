from core.formatting.emojis import get_balance_emoji
from core.formatting.html import (
    nl,
    bold,
    cursive
)
from schemas import UserProfile


class Messages:
    trigger_words = {
        "слово": "сообщение",
        "второе слово": "второе сообщение"
    }

    start = f"{bold('Рады приветствовать в Дайс 👋')}{nl(2)}" \
            f"🎲 Кубик крутится - кэш мутится{nl(2)}" \
            f"- {bold('/balance')} - текущий баланс{nl(1)}" \
            f"- {bold('/profile')} - основное меню{nl(1)}" \
            f"- {bold('/pvb')} - игра с ботом{nl(1)}" \
            f"- {bold('/pvp')} - игра с соперником{nl(1)}" \
            f"- {bold('/pvpc')} - игра с соперником в чате{nl(1)}" \
            f"- {bold('/lottery')} - розыгрыши{nl(1)}" \
            f"- {bold('/support')} - поддержка"

    lottery = "🎉 Для участия в розыгрышах вступите в чат"
    support = "🤖 Если у вас возникли вопросы, обратитесь в нашу поддержку"
    pvpc = "⚔ Для игры с соперником в чате, вступите в наш чат"

    my_transactions = f"{bold('💰 Ваши последние 5 транзакций')}"

    top_five = f"{bold('🏆 Топ-5 игроков')}"

    force_to_subscribe = "🔔 Для взаимодействия с ботом необходимо состоять в следующих чатах:\n" \
                     " 1. чат\n" \
                     " 2. чат"

    terms_and_conditions = f"{bold('📋 Внимательно прочитайте правила игры')}\n\n" \
                           f"1. Первое правило бойцовского клуба"

    demo_mode_instruction = ""

    game_mode_disabled = f"🔧 На данный момент этот режим находится на {bold('плановых технических работах')}, " \
                         f"возвращайтесь позже"

    deposit_sleeping = f"🔧 На данный момент создание транзакций штатно приостановлено " \
                       f"по причине {bold('плановых ежедневных технических работ')}, возвращайтесь позже"

    withdrawal_sleeping = f"{bold('Обратите внимание!')}\n" \
                          f"По причине проходящих на данный момент плановых технических работ, обработка этого вида " \
                          f"транзакции произойдёт не ранее, чем через 6 часов"

    pvb_in_process = "🎲 Вы всё ещё в игре и трясёте кость в ладонях. Сначала закончите игру, бросив кубик"

    dice_bot_throw = f"{bold('🎲 Бросьте кубик!')}"

    pvb_instruction = f"{bold('🤖 Игра с ботом - инструкция')}"

    dice_p2p_instruction = "🎲 Вы можете, либо присоединиться к существующей игре, либо создать свою\n" \
                           "- Если в существующую игру вступает игрок и бросает кубик, " \
                           "у создателя игры есть минута чтобы бросить кубик в ответ, иначе это сделает бот\n" \
                           "- Если игру не приняли в течение 72 часов, она автоматически закрывается " \
                           "и ставка зачисляется обратно на баланс создателя"

    technical_issues = f"{bold('🔧 Технические неполадки')}\n\n" \
                       f"Пожалуйста, обратитесь в поддержку"

    @staticmethod
    def games(balance: int) -> str:
        return f"<b>🎲 Выберите режим игры</b>\n\n" \
               f"💵 Ваш баланс: <b>{balance}</b> RUB"

    @staticmethod
    def balance(balance: int, beta_balance: int) -> str:
        return f"💵 Ваш баланс: {bold(balance)} RUB{nl()}" \
               f"💴 Бета-баланс: {bold(beta_balance)} RUB"

    @staticmethod
    def profile(profile_scheme: UserProfile) -> str:
        return f"Имя: {bold(profile_scheme.tg_name)}\n" \
               f"Баланс: {bold(profile_scheme.balance)}\n" \
               f"Бета-баланс: {bold(profile_scheme.beta_balance)}\n" \
               f"Дата регистрации: {bold(profile_scheme.joined_at)} (UTC)\n" \
               f"Всего игр: {bold(profile_scheme.games_count)}"

    @staticmethod
    def transactions(balance: int, min_transaction: int, btc_min_withdrawal: int) -> str:
        return f"<b>💰 Пополнение и вывод</b>\n\n" \
               f"💵 Баланс: <b>{balance}</b>\n\n" \
               f"Сумма любой операции не должна быть ниже <b>{min_transaction} RUB</b>\n" \
               f"Сумма вывода на биткоин-кошелёк не должна быть ниже <b>{btc_min_withdrawal}</b>"

    @staticmethod
    def transaction_details(
            method: str, transaction_id: int, requested_at: str, details: str, bank: str,
            amount: int, btc_equivalent: float, fee: int
    ) -> str:
        if method == "btc":
            method_caption = "на BTC-кошелёк"
            invoice_caption = f"{(btc_equivalent / 100) * (100 - fee):.7f} BTC"
            details_caption = f"🪙 Эквивалент: <b>{btc_equivalent}</b>\n" \
                              f"🪙 Кошелёк: <b>{details}</b>"
        else:
            method_caption = "на банковскую карту"
            invoice_caption = f"{(amount / 100) * (100 - fee):.0f} RUB"
            details_caption = f"💳 Банк: <b>{bank}</b>\n" \
                              f"💳 Реквизиты: <b>{details}</b>"

        return f"<b>💵 Транзакция #{transaction_id:03} - вывод</b>\n\n" \
               f"📅 Дата и время: <b>{requested_at}</b>\n" \
               f"💰 Способ получения: <b>{method_caption}</b>\n" \
               f"💰 Сумма: <b>{amount} RUB</b>\n" \
               f"💰 Комиссия: <b>{fee}%</b>\n" \
               f"💰 Сумма к получению: <b>{invoice_caption}</b>\n" \
               f"{details_caption}"

    @staticmethod
    def player(name: str, games_total: int, position: int, winnings: int) -> str:
        return f"🥇 <b>Рейтинговый игрок</b>\n\n" \
               f"🙋‍ Имя: <b>{name}</b>\n" \
               f"🎲 Всего игр: <b>{games_total}</b>\n" \
               f"🏆 Место в рейтинге: <b>{position}</b>\n" \
               f"💵 Общая сумма выигрыша: <b>{winnings}</b>"

    @staticmethod
    def demo(user_balance: int, user_beta_balance: int, is_demo_mode: bool) -> str:
        caption = "💴 Вы в <b>демо</b>-режиме" if is_demo_mode else "💵 Вы в <b>обычном</b> режиме"

        return f"🎲 Демо-режим с бета-балансом\n\n" \
               f"💵 Настоящий баланс: <b>{user_balance}</b>\n" \
               f"💴 Бета-баланс: <b>{user_beta_balance}</b>\n\n" \
               f"{caption}\n\n" \
               f"{Messages.demo_mode_instruction}"

    @staticmethod
    def pvb(balance: int, is_demo_mode: bool) -> str:
        if is_demo_mode:
            balance_caption = f"💴 Бета-баланс"
            demo_caption = "<i>- демо-режим</i>"
        else:
            balance_caption = f"💵 Ваш баланс"
            demo_caption = ""

        return f"<b>🤖 Игра с ботом {demo_caption}</b>\n\n" \
               f"{balance_caption}: <b>{balance}</b>"

    @staticmethod
    def pvb_create(bots_turn_first: bool, beta_mode: bool, selected_balance: int, bet: int) -> str:
        balance_emoji = get_balance_emoji(beta_mode)

        return f"{bold('🤖 Игра с ботом')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"{balance_emoji} Ваш баланс: {bold(selected_balance)}\n" \
               f"{balance_emoji} Ставка: <b>{bet}</b>\n" \
               f"🔁 Первым {bold('бросает бот' if bots_turn_first else 'бросаете вы')}"

    @staticmethod
    def dice_bot_result(is_demo_mode: bool, selected_balance: int, result: int, game_id: int) -> str:
        if is_demo_mode:
            demo_caption = " - <i>демо-режим</i>"
            balance_caption = "💴 Бета-баланс"
        else:
            demo_caption = ""
            balance_caption = "💵 Ваш баланс"

        if result == 1:
            result_caption = "🔥 Вы выиграли!"
        elif result == 0:
            result_caption = "💀 Вы проиграли!"
        else:
            result_caption = "✌ Ничья! Сделайте ставку ещё раз"

        return f"Игра #{game_id:03}{demo_caption}\n\n" \
               f"{result_caption}\n" \
               f"{balance_caption}: {selected_balance}"

    @staticmethod
    def dice_bot_mine(wins_percent: int) -> str:
        return f"Ваш процент побед: <b>{wins_percent:.0f}%</b>"

    @staticmethod
    def dice_p2p(page: int, pages_total: int, games_total: int) -> str:
        if pages_total == 0:
            return "<b>🎲 На данный момент нет доступных игр</b>"
        else:
            return f"<b>🎲 Доступно {games_total}</b> игр\n\n" \
                   f"📋 Страница: <b>{page} / {pages_total}</b>"

    @staticmethod
    def dice_p2p_details(
            game_id: int, selected_balance: int, bet: int, creator_name: str,
            is_demo_mode: bool, is_owner: bool, is_balance_enough: bool, minutes_before_cancel: int
    ) -> str:
        if is_demo_mode:
            demo_caption = " - <i>демо-режим</i>"
            balance_emoji = "💴"
            balance_caption = f"💴 Бета-баланс"
        else:
            demo_caption = ""
            balance_emoji = "💵"
            balance_caption = f"💵 Ваш баланс"

        if is_owner:
            cancel_caption = ""

            if minutes_before_cancel != 0:
                cancel_caption = f"<i>Игру можно будет отменить через {minutes_before_cancel} минут</i>"

            return f"<b>🎲 Игра #{game_id:03}{demo_caption} - <b>Ваша</b></b>\n\n" \
                   f"{balance_emoji} Сумма ставки: <b>{bet}</b>\n\n" \
                   f"{cancel_caption}"
        else:
            if is_balance_enough:
                caption = "<b>Чтобы вступить в игру бросьте кость</b>"
            else:
                caption = "<b>У вас недостаточно баланса чтобы присоединиться к игре</b>"

            return f"<b>🎲 Игра #{game_id:03}{demo_caption}</b>\n\n" \
                   f"🤙 Соперник: <b>{creator_name}\n</b>\n" \
                   f"{balance_caption}: <b>{selected_balance}</b>\n" \
                   f"{balance_emoji} Сумма ставки: <b>{bet}</b>\n\n" \
                   f"{caption}"

    @staticmethod
    def dice_p2p_cancel(game_id: int) -> str:
        return f"<b>✅ Игра #{game_id:03} успешно отменена, баланс восстановлен</b>"

    @staticmethod
    def withdrawal(balance: int, is_transactions_sleeping: bool) -> str:
        caption = Messages.withdrawal_sleeping if is_transactions_sleeping else ""

        return f"<b>Вывод средств</b>\n\n" \
               f"💵 Баланс: <b>{balance}</b>\n\n" \
               f"Выберите удобный способ вывода средств\n\n" \
               f"{caption}"

    @staticmethod
    def withdrawal_amount(
            is_amount_enough: bool, method: str, balance: int, withdrawal: int, btc_equivalent: float,
            card_fee: int, btc_fee: int, highest_lower_limit: int
    ) -> str:
        if is_amount_enough:
            caption = ""
        else:
            caption = f"<i>Чтобы продолжить укажите сумму вывода не менее {highest_lower_limit} RUB</i>"

        if method == "card":
            return f"<b>Вывод средств</b>\n\n" \
                   f"💵 Баланс: <b>{balance}</b>\n" \
                   f"💵 Сумма вывода: <b>{withdrawal}</b>\n" \
                   f"💳 Комиссия: <b>{card_fee}%</b>\n\n" \
                   f"{caption}"
        else:
            if btc_equivalent == -1:
                return Messages.technical_issues
            else:
                return f"<b>Вывод средств</b>\n\n" \
                       f"💵 Баланс: <b>{balance}</b>\n" \
                       f"💵 Сумма вывода: <b>{withdrawal}</b>\n" \
                       f"🪙 Эквивалент в BTC: <b>{btc_equivalent}</b>\n" \
                       f"🪙 Комиссия: <b>{btc_fee}%</b>\n\n" \
                       f"{caption}"

    @staticmethod
    def withdrawal_bank(bank: str, details: str) -> str:
        if bank == "" and details != "":
            bank = "не указан"
            caption = "<i>Чтобы продолжить укажите банк</i>"
        elif details == "" and bank != "":
            details = "не указаны"
            caption = "<i>Чтобы продолжить укажите реквизиты</i>"
        elif bank == "" and details == "":
            bank = "не указан"
            details = "не указаны"
            caption = "<i>Чтобы продолжить укажите банк и реквизиты, введя их поочереди, двумя сообщениями</i>"
        else:
            caption = "Если хотите изменить данные - просто напишите их по очереди"

        return f"<b>Вывод средств</b>\n\n" \
               f"🏦 Банк: <b>{bank}</b>\n" \
               f"💳 Реквизиты: <b>{details}</b>\n\n" \
               f"{caption}"

    @staticmethod
    def deposit(balance: int) -> str:
        return f"<b>Пополнение баланса</b>\n\n" \
               f"💵 Баланс: <b>{balance}</b>\n\n" \
               f"Выберите удобный способ пополнения баланса"

    @staticmethod
    def deposit_amount(is_amount_enough: bool, method: str, balance: int, deposit: int, btc_equivalent: float) -> str:
        caption = "" if is_amount_enough else "<i>Чтобы продолжить укажите сумму пополнения</i>"

        if method == "card":
            return f"<b>Пополнение баланса</b>\n\n" \
                   f"💵 Баланс: <b>{balance}</b>\n" \
                   f"💵 Сумма пополнения: <b>{deposit}</b>\n\n" \
                   f"{caption}"
        else:
            if btc_equivalent == -1:
                return Messages.technical_issues
            else:
                return f"<b>Пополнение баланса</b>\n\n" \
                       f"💵 Баланс: <b>{balance}</b>\n" \
                       f"💵 Сумма пополнения: <b>{deposit}</b>\n" \
                       f"🪙 Эквивалент в BTC: <b>{btc_equivalent}</b>\n\n" \
                       f"{caption}"

    @staticmethod
    def deposit_amount_confirm(method: str, btc_equivalent: float, amount: int) -> str:
        if method == "card":
            return f"<b>Пополнение баланса</b>\n\n" \
                   f"Вы подтверждаете, что хотите пополнить баланс на сумму <b>{amount} RUB</b>?"
        else:
            if btc_equivalent == -1:
                return Messages.technical_issues
            else:
                return f"<b>Пополнение баланса</b>\n\n" \
                       f"Вы подтверждаете, что хотите пополнить баланс на сумму " \
                       f"<b>{amount} RUB ({btc_equivalent} BTC)</b>?"

    @staticmethod
    def deposit_confirm(method: str, btc_equivalent: float, amount: int, details: str, wallet: str) -> str:
        if method == "card":
            return f"Отлично! Переведите <code>{amount}</code> RUB на следующие реквизиты:\n" \
                   f"<code>{details}</code>"
        else:
            if btc_equivalent == -1:
                return Messages.technical_issues
            else:
                return f"Отлично! Переведите <code>{btc_equivalent}</code> BTC на следующие реквизиты:\n" \
                       f"<code>{wallet}</code>"

    @staticmethod
    def confirmation(transaction_type: str, transaction_id: int) -> str:
        if transaction_type == "withdrawal":
            caption = "Если пополнения не произошло - обратитесь в поддержку\n\n" \
                      "Удачной игры 🎲"
        else:
            caption = "Благодарим, что выбрали нас 🤝"

        return f"<b>⏳ Транзакция #{transaction_id:03} " \
               f"принята и будет обработана в ближайшее время</b>\n\n" \
               f"Статус можно проверить на вкладке <b>«Транзакции»</b> в профиле.\n" \
               f"{caption}"

    @staticmethod
    def admin_withdrawal_confirm(
            method: str, transaction_id: int, requested_at: str, user_id: int, name: str,
            wallet: str, details: str, bank: str, amount: int, btc_equivalent: float, fee: int
    ) -> str:
        if method == "btc":
            method_caption = "на BTC-кошелёк"
            invoice_caption = f"{(btc_equivalent / 100) * (100 - fee):.7f} BTC"
            details_caption = f"🪙 Эквивалент: <b>{btc_equivalent}</b>\n" \
                              f"🪙 Кошелёк: <b>{wallet}</b>"
        else:
            method_caption = "на банковскую карту"
            invoice_caption = f"{(amount / 100) * (100 - fee):.0f} RUB"
            details_caption = f"💳 Банк: <b>{bank}</b>\n" \
                              f"💳 Реквизиты: <b>{details}</b>"

        return f"<b>💵 Транзакция #{transaction_id:03} - вывод</b>\n\n" \
               f"🙋‍ Пользователь: <a href='tg://user?id={user_id}'>{name}</a> | {user_id}\n" \
               f"📅 Дата и время: <b>{requested_at}</b>\n" \
               f"💰 Способ получения: <b>{method_caption}</b>\n" \
               f"💰 Сумма: <b>{amount} RUB</b>\n" \
               f"💰 Комиссия: <b>{fee}%</b>\n" \
               f"💰 Сумма к переводу: <b>{invoice_caption}</b>\n" \
               f"{details_caption}"

    @staticmethod
    def admin_deposit_confirm(
            method: str, transaction_id: int, requested_at: str, user_id: int, name: str,
            amount: int, btc_equivalent: float
    ) -> str:
        if method == "btc":
            method_caption = "через BTC-кошелёк"
            details_caption = f"🪙 Эквивалент: <b>{btc_equivalent}</b>\n"
        else:
            method_caption = "банковской картой"
            details_caption = ""

        return f"<b>💵 Транзакция #{transaction_id:03} - пополнение</b>\n\n" \
               f"🙋‍ Пользователь: <a href='tg://user?id={user_id}'>{name}</a> | {user_id}\n" \
               f"📅 Дата и время: <b>{requested_at}</b>\n" \
               f"💰 Способ оплаты: <b>{method_caption}</b>\n" \
               f"💰 Сумма: <b>{amount} RUB</b>\n" \
               f"{details_caption}"

    @staticmethod
    def terms_accepted() -> str:
        return f"🎲 Хорошей игры!"

    @staticmethod
    def terms_rejected() -> str:
        return f"❌ Игра с ботом возможна {bold('только после принятия правил игры')}"

    @staticmethod
    def admin(users_since_launch: int) -> str:
        return f"{bold('🎲 Дайс / Админ-панель')}{nl(2)}" \
               f"🙋 Пользователей с момента запуска: <b>{bold(users_since_launch)}</b>{nl(2)}" \
               f"{bold('Доступные команды:')} " \
               f"реквизиты, баланс, чат, комиссия (бот, p2p, чат, банк, биткоин), ставка (минимум, максимум), " \
               f"транзакция (минимум, биткоин), оповещение (сумма, период), сумма, период {nl(2)}" \
               f"Чтобы увидеть синтаксис команды необходимо написать только её имя без параметров, " \
               f"например, - \"комиссия\""
