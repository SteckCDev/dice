import math
from datetime import datetime

from common.formatting.emojis import get_balance_emoji
from common.formatting.html import (
    bold,
    cursive,
    link,
)
from core.schemas.pvp import (
    PVPDTO,
    PVPDetailsDTO,
)
from core.schemas.user import (
    UserDTO,
    UserCacheDTO,
)


class Messages:
    @staticmethod
    def start() -> str:
        return f"{bold('Рады приветствовать в Дайс 👋')}\n\n" \
               f"{cursive('🎲 Кубик крутится - кэш мутится')}\n\n" \
               f"- {bold('/balance')} - текущий баланс\n" \
               f"- {bold('/profile')} - основное меню\n" \
               f"- {bold('/pvb')} - игра с ботом\n" \
               f"- {bold('/pvp')} - игра с соперником\n" \
               f"- {bold('/pvpc')} - игра с соперником в чате\n" \
               f"- {bold('/lottery')} - розыгрыши\n" \
               f"- {bold('/support')} - поддержка"

    @staticmethod
    def balance(balance: int, beta_balance: int) -> str:
        return f"💵 Ваш баланс: {bold(balance)} RUB\n" \
               f"💴 Бета-баланс: {bold(beta_balance)} RUB"

    @staticmethod
    def game_mode_disabled() -> str:
        return f"🔧 На данный момент этот режим находится на {bold('плановых технических работах')}, " \
               f"возвращайтесь позже"

    @staticmethod
    def balance_is_not_enough() -> str:
        return "❌ Недостаточно баланса"

    @staticmethod
    def bet_out_of_limits(min_bet: int, max_bet: int) -> str:
        return f"🔔 Сумма ставки должна быть в диапазоне между {min_bet} и {max_bet}"

    @staticmethod
    def pvb_in_process() -> str:
        return "🎲 Вы всё ещё в игре и трясёте кость в ладонях. Сначала закончите игру, бросив кубик"

    @staticmethod
    def pvb_non_direct() -> str:
        return "🛑 Вход с намагниченными кубиками запрещён!"

    @staticmethod
    def pvb_bots_turn() -> str:
        return bold("🤖 Бросает бот")

    @staticmethod
    def pvb_your_turn() -> str:
        return bold("🎲 Бросьте кубик!")

    @staticmethod
    def pvp_already_started(game_id: int, beta_mode: bool) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"❌ К игре уже присоединились, выберите другую"

    @staticmethod
    def pvp_creator_late(game_id: int, beta_mode: bool) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"⌛ Время вышло, бот бросил кость за вас"

    @staticmethod
    def force_to_subscribe() -> str:
        return f"🔔 Для взаимодействия с ботом необходимо состоять в следующих чатах:\n" \
               f" 1. {link('первый чат', 'https://google.com')}\n" \
               f" 2. {link('второй чат', 'https://google.com')}"

    @staticmethod
    def games(selected_balance: int, beta_mode: bool) -> str:
        return f"{bold('🎲 Выберите режим игры')}\n\n" \
               f"{get_balance_emoji(beta_mode)} Ваш баланс: {bold(selected_balance)} RUB"

    @staticmethod
    def profile(name: str, balance: int, beta_balance: int, joined_at: datetime, games_count: int) -> str:
        return f"Имя: {bold(name)}\n" \
               f"Баланс: {bold(balance)}\n" \
               f"Бета-баланс: {bold(beta_balance)}\n" \
               f"Дата регистрации: {bold(joined_at)} (UTC)\n" \
               f"Всего игр: {bold(games_count)}"

    @staticmethod
    def lottery() -> str:
        return "🎉 Для участия в розыгрышах вступите в чат"

    @staticmethod
    def support() -> str:
        return "🤖 Если у вас возникли вопросы, обратитесь в нашу поддержку"

    @staticmethod
    def terms_and_conditions() -> str:
        return f"{bold('📋 Внимательно прочитайте правила игры')}\n\n" \
               f"1. Первое правило бойцовского клуба"

    @staticmethod
    def pvb(balance: int, beta_mode: bool) -> str:
        return f"{bold('🤖 Игра с ботом')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"{get_balance_emoji(beta_mode)} Ваш баланс: {bold(balance)}"

    @staticmethod
    def pvb_instruction() -> str:
        return f"{bold('🤖 Игра с ботом - инструкция')}"

    @staticmethod
    def pvb_create(bots_turn_first: bool, beta_mode: bool, selected_balance: int, bet: int) -> str:
        balance_emoji = get_balance_emoji(beta_mode)

        return f"{bold('🤖 Игра с ботом')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"{balance_emoji} Ваш баланс: {bold(selected_balance)}\n" \
               f"{balance_emoji} Ставка: {bold(bet)}\n" \
               f"🔁 Первым {bold('бросает бот' if bots_turn_first else 'бросаете вы')}"

    @staticmethod
    def pvb_result(beta_mode: bool, selected_balance: int, player_won: bool | None, game_id: int) -> str:
        if player_won is None:
            result = "✌ Ничья! Сделайте ставку ещё раз"
        elif player_won:
            result = "🔥 Вы выиграли!"
        else:
            result = "💀 Вы проиграли!"

        return f"🎲 Игра #{game_id:03}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"{result}\n" \
               f"{get_balance_emoji(beta_mode)} Ваш баланс: {bold(selected_balance)}"

    @staticmethod
    def pvb_history(wins_percent: int) -> str:
        return f"🎲 Ваш процент побед: {bold(f'{wins_percent:.1f}%')}"

    @staticmethod
    def pvp(available_pvp_games: int, page: int = 1) -> str:
        if available_pvp_games == 0:
            return bold("🎲 На данный момент нет доступных игр")

        pages_total = math.ceil(available_pvp_games / 5)

        return f"{bold(f'🎲 Доступно {available_pvp_games} игр')}\n\n" \
               f"📋 Страница: {bold(f'{page} / {pages_total}')}"

    @staticmethod
    def pvp_instruction() -> str:
        return "🎲 Вы можете, либо присоединиться к существующей игре, либо создать свою\n" \
               "- Если в существующую игру вступает игрок и бросает кубик, " \
               "у создателя игры есть минута чтобы бросить кубик в ответ, иначе это сделает бот\n" \
               "- Если игру не приняли в течение 72 часов, она автоматически закрывается " \
               "и ставка зачисляется обратно на баланс создателя"

    @staticmethod
    def pvp_details(user: UserDTO, pvp_details: PVPDetailsDTO) -> str:
        if user.tg_id == pvp_details.creator_tg_id:
            cancel_caption = ""

            if pvp_details.cancellation_unlocks_in:
                cancel_caption = f"Игру можно будет отменить через " \
                                 f"{pvp_details.cancellation_unlocks_in.seconds // 60} минут"

            return f"🎲 Игра #{pvp_details.id:03}{cursive(' - бета-режим') if pvp_details.beta_mode else ''} {bold('[Ваша]')}\n\n" \
                   f"{get_balance_emoji(pvp_details.beta_mode)} Ставка: {bold(pvp_details.bet)}\n\n" \
                   f"{cancel_caption}"

        balance_for_mode = user.beta_balance if pvp_details.beta_mode else user.balance

        if balance_for_mode >= pvp_details.bet:
            join_caption = bold("Чтобы вступить в игру бросьте кость")
        else:
            join_caption = bold("У вас недостаточно баланса чтобы присоединиться к игре")

        return f"🎲 Игра #{pvp_details.id:03}" \
               f"{cursive(' - бета-режим') if pvp_details.beta_mode else ''} {bold(' [Ваша]')}\n\n" \
               f"🤙 Соперник: {bold(pvp_details.creator_name)}\n\n" \
               f"{get_balance_emoji(pvp_details.beta_mode)}: {bold(balance_for_mode)}\n" \
               f"{get_balance_emoji(pvp_details.beta_mode)} Сумма ставки: {bold(pvp_details.bet)}\n\n" \
               f"{join_caption}"

    @staticmethod
    def pvp_cancel(game_id: int) -> str:
        return bold(f'✅ Игра #{game_id:03} успешно отменена, баланс восстановлен')

    @staticmethod
    def pvp_create(user_cache: UserCacheDTO, min_bet: int, max_bet: int) -> str:
        return f"{bold('👥 Игра с соперником')} {cursive(' - бета-режим') if user_cache.beta_mode else ''}\n\n" \
               f"{get_balance_emoji(user_cache.beta_mode)} Ставка: {bold(user_cache.pvp_bet)}\n\n" \
               f"{cursive(f'Введите сумму ставки от {min_bet} RUB до {max_bet} RUB')}"

    @staticmethod
    def pvp_confirm(game_id: int, user_cache: UserCacheDTO) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03} создана!')} " \
               f"{cursive(' - бета-режим') if user_cache.beta_mode else ''}\n\n" \
               f"{get_balance_emoji(user_cache.beta_mode)} Ставка: {bold(user_cache.pvp_bet)}"

    @staticmethod
    def pvp_join(game_id: int, beta_mode: bool) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"Ждём бросок игрока минуту, иначе бот бросит кость за него"

    @staticmethod
    def pvp_started(game_id: int, beta_mode: bool, bet: int, opponent_tg_name: str) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"🤙 Соперник: {bold(opponent_tg_name)}\n" \
               f"{get_balance_emoji(beta_mode)} Ставка: {bold(bet)}\n\n" \
               f"Бросьте кость или это сделает бот!"

    @staticmethod
    def pvp_finished(pvp: PVPDTO, user: UserDTO, opponent: UserDTO) -> str:
        opponent_dice = pvp.creator_dice if opponent.tg_id == pvp.creator_tg_id else pvp.opponent_dice

        if pvp.winner_tg_id is None:
            result: str = "✌ Ничья!"
        else:
            result: str = "🔥 Вы выиграли!" if pvp.winner_tg_id == user.tg_id else "💀 Вы проиграли!"

        return f"{bold(f'🎲 Игра #{pvp.id:03}')}{cursive(' - бета-режим') if pvp.beta_mode else ''}\n\n" \
               f"🤙 {opponent.tg_name} выбросил {bold(opponent_dice)}\n" \
               f"{result}\n" \
               f"{get_balance_emoji(pvp.beta_mode)} Ваш баланс: " \
               f"{bold(user.beta_balance if pvp.beta_mode else user.balance)}"

    @staticmethod
    def pvpc() -> str:
        return "⚔ Для игры с соперником в чате, вступите в наш чат"

    @staticmethod
    def terms_accepted() -> str:
        return f"🎲 Хорошей игры!"

    @staticmethod
    def terms_rejected() -> str:
        return f"❌ Игра с ботом возможна {bold('только после принятия правил игры')}"

    @staticmethod
    def admin(users_since_launch: int) -> str:
        return f"{bold('🎲 Дайс / Админ-панель')}\n\n" \
               f"🙋 Пользователей с момента запуска: {bold(users_since_launch)}\n\n" \
               f"{bold('Доступные команды:')} " \
               f"реквизиты, баланс, чат, комиссия (бот, p2p, чат, банк, биткоин), ставка (минимум, максимум), " \
               f"транзакция (минимум, биткоин), оповещение (сумма, период), сумма, период\n\n" \
               f"Чтобы увидеть синтаксис команды необходимо написать только её имя без параметров, " \
               f"например, - \"комиссия\""
