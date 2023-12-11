from datetime import datetime, timedelta

from decimal import Decimal

from core.schemas.pvp import (
    PVPDTO,
    PVPDetailsDTO,
)
from core.schemas.pvpc import (
    PVPCDetailsDTO
)
from core.schemas.user import (
    UserDTO,
    UserCacheDTO,
)
from .formatting.emojis import get_balance_emoji
from .formatting.html import (
    bold,
    cursive,
    link,
    code,
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
        return f"💵 Ваш баланс: {bold(balance)}\n" \
               f"💴 Бета-баланс: {bold(beta_balance)}"

    @staticmethod
    def games(selected_balance: int, beta_mode: bool) -> str:
        return f"{bold('🎲 Дайс / Режимы игр')}\n\n" \
               f"{get_balance_emoji(beta_mode)} Ваш баланс: {bold(selected_balance)}"

    @staticmethod
    def profile(name: str, balance: int, beta_balance: int, joined_at: datetime, games_count: int) -> str:
        return f"{bold('🎲 Дайс / Профиль')}\n\n" \
               f"Имя: {bold(name)}\n" \
               f"Баланс: {bold(balance)}\n" \
               f"Бета-баланс: {bold(beta_balance)}\n" \
               f"Дата регистрации: {bold(joined_at.strftime('%y.%m.%d %H:%M'))} (UTC)\n" \
               f"Всего игр: {bold(games_count)}"

    @staticmethod
    def lottery() -> str:
        return "🎉 Для участия в розыгрышах вступите в чат"

    @staticmethod
    def support() -> str:
        return "🤖 Если у вас возникли вопросы, обратитесь в нашу поддержку"

    @staticmethod
    def on_issue() -> str:
        return "🔧 У нас возникли технические проблемы, пожалуйста, обратитесь в поддержку"

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
    def dice_not_direct() -> str:
        return "🛑 Вход с намагниченными кубиками запрещён!"

    @staticmethod
    def force_to_subscribe() -> str:
        return f"🔔 Для взаимодействия с ботом необходимо состоять в следующих чатах:\n" \
               f" 1. {link('первый чат', 'https://google.com')}\n" \
               f" 2. {link('второй чат', 'https://google.com')}"

    @staticmethod
    def terms_and_conditions() -> str:
        return f"{bold('📋 Внимательно прочитайте правила игры')}\n\n" \
               f"1. Первое правило бойцовского клуба"

    @staticmethod
    def terms_accepted() -> str:
        return f"🎲 Хорошей игры!"

    @staticmethod
    def terms_rejected() -> str:
        return f"❌ Игра с ботом возможна {bold('только после принятия правил игры')}"

    @staticmethod
    def pvb_in_process() -> str:
        return "🎲 Вы всё ещё в игре и трясёте кость в ладонях. Сначала закончите игру, бросив кубик"

    @staticmethod
    def pvb_bots_turn() -> str:
        return bold("🤖 Бросает бот")

    @staticmethod
    def pvb_your_turn() -> str:
        return bold("🎲 Бросьте кубик!")

    @staticmethod
    def pvb(balance: int, beta_mode: bool) -> str:
        return f"{bold('🤖 Дайс / Игра с ботом')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"{get_balance_emoji(beta_mode)} Ваш баланс: {bold(balance)}"

    @staticmethod
    def pvb_history(wins_percent: float) -> str:
        return f"{bold('🤖 Дайс / Игра с ботом - история (5)')}\n\n" \
               f"🎲 Ваш процент побед: {bold(f'{wins_percent:.1f}%')}"

    @staticmethod
    def pvb_instruction() -> str:
        return f"{bold('🤖 Дайс / Игра с ботом - инструкция')}"

    @staticmethod
    def pvb_create(
            bots_turn_first: bool,
            beta_mode: bool,
            selected_balance: int,
            bet: int,
            min_bet: int,
            max_bet: int
    ) -> str:
        upper_limit = selected_balance if min_bet < selected_balance < max_bet else max_bet
        balance_emoji: str = get_balance_emoji(beta_mode)

        return f"{bold('🤖 Дайс / Игра с ботом')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"{balance_emoji} Ваш баланс: {bold(selected_balance)}\n" \
               f"{balance_emoji} Ставка: {bold(bet)}\n" \
               f"🔁 Первым {bold('бросает бот' if bots_turn_first else 'бросаете вы')}\n\n" \
               f"{cursive(f'Введите сумму ставки от {min_bet} до {upper_limit}')}"

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
    def pvp_join_rejected(game_id: int, beta_mode: bool) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"❌ Вы не можете играть сами с собой в этом режиме"

    @staticmethod
    def pvp_already_started(game_id: int, beta_mode: bool) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"❌ К игре уже присоединились, выберите другую"

    @staticmethod
    def pvp_creator_late(game_id: int, beta_mode: bool) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"⌛ Время вышло, бот бросил кость за вас"

    @staticmethod
    def pvp_expired(game_id: int, beta_mode: bool, bet: int, ttl: timedelta) -> str:
        return f"{bold(f'🎲 Игра #{game_id:03}')}{cursive(' - бета-режим') if beta_mode else ''}\n\n" \
               f"⌛ Истекло время ожидания - {ttl.seconds // 3600} часов, " \
               f"ставка закрыта, баланс восстановлен\n" \
               f"{get_balance_emoji(beta_mode)} Ставка: {bold(bet)}"

    @staticmethod
    def pvp(available_pvp_games_count: int, pages_total: int, page: int = 1) -> str:
        if available_pvp_games_count == 0:
            return f"{bold('👥 Дайс / Игра с соперником')}\n\n" \
                   f"{cursive('На данный момент нет доступных игр')}"

        return f"{bold('👥 Дайс / Игра с соперником')}\n\n" \
               f"Доступно игр: {bold(available_pvp_games_count)}\n" \
               f"Страница: {bold(f'{page} / {pages_total}')}"

    @staticmethod
    def pvp_instruction() -> str:
        return f"{bold('👥 Дайс / Игра с соперником - инструкция')}\n\n" \
               "Вы можете, либо присоединиться к существующей игре, либо создать свою\n" \
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

            return f"🎲 Игра #{pvp_details.id:03}{cursive(' - бета-режим') if pvp_details.beta_mode else ''} " \
                   f"{bold('[Ваша]')}\n\n" \
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
    def pvp_create(user_cache: UserCacheDTO, selected_balance: int, min_bet: int, max_bet: int) -> str:
        upper_limit = selected_balance if min_bet < selected_balance < max_bet else max_bet
        balance_emoji = get_balance_emoji(user_cache.beta_mode)

        return f"{bold('👥 Дайс / Игра с соперником')} {cursive(' - бета-режим') if user_cache.beta_mode else ''}\n\n" \
               f"{balance_emoji} Ваш баланс: {bold(selected_balance)}\n" \
               f"{balance_emoji} Ставка: {bold(user_cache.pvp_bet)}\n\n" \
               f"{cursive(f'Введите сумму ставки от {min_bet} до {upper_limit}')}"

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
    def pvpc_already_exists() -> str:
        return "❌ Вы уже состоите в игре"

    @staticmethod
    def pvpc_create() -> str:
        return f"{bold('🔔 Чтобы создать игру используйте шаблон')}\n\n" \
               f"{cursive('дайс ставка количество_раундов')}"

    @staticmethod
    def pvpc_rounds_out_of_limits(max_rounds: int) -> str:
        return f"🔔 Количество раундов должно быть от {bold('1')} до {bold(max_rounds)}"

    @staticmethod
    def pvpc_already_started() -> str:
        return "❌ Игра более недоступна"

    @staticmethod
    def pvpc_already_in_game() -> str:
        return "❌ Сначала завершите предыдущую игру"

    @staticmethod
    def pvpc_join_rejected() -> str:
        return "❌ Вы не можете вступить в свою же игру"

    @staticmethod
    def pvpc_cancellation_rejected() -> str:
        return "❌ Вы не можете отменить чужую игру"

    @staticmethod
    def pvpc_not_found() -> str:
        return "❌ Игра не найдена"

    @staticmethod
    def pvpc_canceled() -> str:
        return "✅ Игра отменена"

    @staticmethod
    def pvpc_join(game_id: int, bet: int, rounds: int) -> str:
        return f"{bold(f'🟡 Игра #{game_id:03}')}\n\n" \
               f"💵 Ставка: {bold(bet)}\n" \
               f"🎲 Количество кубиков: {bold(rounds)}"

    @staticmethod
    def pvpc_throwing_for_user(game_id: int, user_tg_name: str) -> str:
        return f"{bold(f'🔥 Игра #{game_id:03}')}\n\n" \
               f"🎲 Бросаем кубики за {user_tg_name}"

    @staticmethod
    def pvpc_start(pvpc_details: PVPCDetailsDTO) -> str:
        return f"{bold(f'🔥 Игра #{pvpc_details.id:03}')}\n\n" \
               f"💵 Ставка: {bold(pvpc_details.bet)}\n" \
               f"🎲 Раундов: {bold(pvpc_details.rounds)}\n\n" \
               f"{link(pvpc_details.creator_tg_name, f'tg://user?id={pvpc_details.creator_tg_id}')}\n" \
               f"----------\n" \
               f"{link(pvpc_details.opponent_tg_name, f'tg://user?id={pvpc_details.opponent_tg_id}')}\n\n" \
               f"🔥 Бросайте кости!"

    @staticmethod
    def pvpc_results(pvpc_details: PVPCDetailsDTO) -> str:
        winner_or_draw = cursive("дружба") if pvpc_details.winner_tg_name is None else bold(pvpc_details.winner_tg_name)

        return f"{bold(f'🔥 Игра #{pvpc_details.id:03}')}\n\n" \
               f"💵 Ставка: {bold(pvpc_details.bet)}\n" \
               f"🎲 Раундов: {bold(pvpc_details.rounds)}\n\n" \
               f"🏆 Победитель: {winner_or_draw}\n\n" \
               f"{link(pvpc_details.creator_tg_name, f'tg://user?id={pvpc_details.creator_tg_id}')} " \
               f"выбросил на {bold(pvpc_details.creator_scored)}\n" \
               f"----------\n" \
               f"{link(pvpc_details.opponent_tg_name, f'tg://user?id={pvpc_details.opponent_tg_id}')} " \
               f" выбросил на {bold(pvpc_details.opponent_scored)}"

    @staticmethod
    def transaction(balance: int, min_deposit: int, min_withdraw: int) -> str:
        return f"{bold('💰 Дайс / Транзакции')}\n\n" \
               f"💵 Баланс: {bold(balance)}\n\n" \
               f"{cursive(f'Минимальная сумма пополнения: {min_deposit}')}\n" \
               f"{cursive(f'Минимальная сумма вывода: {min_withdraw}')}"

    @staticmethod
    def transaction_processed(transaction_id: int, succeed: bool) -> str:
        if succeed:
            return f"✅ Транзакция #{transaction_id:03} успешно обработана"
        else:
            return f"❌ Транзакция #{transaction_id:03} отклонена"

    @staticmethod
    def transaction_deposit_min_limit(min_deposit: int) -> str:
        return f"🔔 Минимальная сумма пополнения {min_deposit} RUB"

    @staticmethod
    def transaction_withdraw_min_limit(min_withdraw: int) -> str:
        return f"🔔 Минимальная сумма вывода {min_withdraw} RUB"

    @staticmethod
    def __transaction_deposit_header() -> str:
        return bold("➡ Дайс / Пополнение баланса")

    @staticmethod
    def transaction_deposit() -> str:
        return f"{Messages.__transaction_deposit_header()}\n\n" \
               f"{cursive('Выберите удобный способ пополнения баланса')}"

    @staticmethod
    def transaction_deposit_amount(min_deposit: int, amount: int, btc_equivalent: Decimal | None = None) -> str:
        btc_caption = f"🪙 Эквивалент в BTC: {btc_equivalent}\n\n" if btc_equivalent else ""
        enter_amount_tip = cursive(f"Введите сумму от {min_deposit} RUB") if amount < min_deposit else ""

        return f"{Messages.__transaction_deposit_header()}\n\n" \
               f"💵 Сумма пополнения: {amount} RUB\n" \
               f"{btc_caption}" \
               f"{enter_amount_tip}"

    @staticmethod
    def transaction_deposit_confirm_amount(amount: int, btc_equivalent: Decimal | None = None) -> str:
        amount_caption = f"{amount} RUB"

        if btc_equivalent is not None:
            amount_caption += f" ({btc_equivalent} BTC)"

        return f"{Messages.__transaction_deposit_header()}\n\n" \
               f"Вы подтверждаете, что хотите пополнить баланс на сумму {bold(amount_caption)}?"

    @staticmethod
    def transaction_deposit_confirm(
            method: str,
            amount_relative_to_method: int,
            details_relative_to_method: str
    ) -> str:
        currency_tip = "RUB" if method == "card" else "BTC"

        return f"{Messages.__transaction_deposit_header()}\n\n" \
               f"Переведите {amount_relative_to_method} {currency_tip} на следующие реквизиты:\n" \
               f"{code(details_relative_to_method)}"

    @staticmethod
    def transaction_deposit_create(transaction_id: int) -> str:
        return f"⏳ Транзакция #{transaction_id:03} принята и будет обработана в ближайшее время.\n\n" \
               f"Статус можно проверить на вкладке {cursive('«Транзакции»')} в профиле. " \
               f"Если пополнения не произошло - обратитесь в поддержку.\n\n" \
               f"Благодарим, что выбрали нас 🤝"

    @staticmethod
    def admin(users_since_launch: int) -> str:
        return f"{bold('🎲 Дайс / Админ-панель')}\n\n" \
               f"🙋 Пользователей с момента запуска: {bold(users_since_launch)}\n\n" \
               f"{bold('Доступные команды:')} " \
               f"баланс (обычный, бета), комиссия (pvb, pvp, pvpc, card, wallet), " \
               f"ставка (минимальная, максимальная), чат (раунды)\n\n" \
               f"Чтобы увидеть синтаксис команды и текущие значения изменяемых ею параметров, " \
               f"необходимо написать только её имя без параметров, " \
               f"например, - {cursive('комиссия')}"

    @staticmethod
    def admin_mailing() -> str:
        return f"{bold('🎲 Дайс / Рассылка')}\n\n" \
               f"{cursive('>[текст рассылки]')}"

    @staticmethod
    def admin_mailing_started() -> str:
        return f"{bold('🎲 Дайс / Рассылка')}\n\n" \
               f"Рассылка запущена"

    @staticmethod
    def admin_config_adjusted() -> str:
        return "✅ Параметр изменён"

    @staticmethod
    def admin_deposit_confirm(
            transaction_id: int,
            user_tg_id: int,
            user_tg_name: str,
            created_at: datetime,
            method: str,
            amount: int,
            btc_equivalent: float | None = None,
            done: bool = False
    ) -> str:
        method_caption = "карта" if method == "card" else "биткоин"
        amount_caption = f"{amount} RUB "

        if btc_equivalent is not None:
            amount_caption += f"({btc_equivalent} BTC)"

        status_emoji = "💵" if done else "⏳"

        return f"{bold(f'{status_emoji} Транзакция #{transaction_id:03} - пополнение')}\n\n" \
               f"🙋‍ Пользователь: {link(user_tg_name, f'tg://user?id={user_tg_id}')} | {user_tg_id}\n" \
               f"📅 Создана: {bold(created_at.strftime('%y.%m.%d %H:%M'))} (UTC)\n" \
               f"💰 Способ оплаты: {bold(method_caption)}\n" \
               f"💰 Сумма: {bold(amount_caption)}"

    @staticmethod
    def admin_transaction_not_found() -> str:
        return "❌ Транзакция не найдена, либо уже обработана"
