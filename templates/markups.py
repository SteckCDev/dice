from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from common.formatting import get_status_emoji, get_balance_emoji
from settings import settings
from templates.menu import Menu


class Markups:
    navigation = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
        KeyboardButton(Menu.GAMES),
        KeyboardButton(Menu.PROFILE),
        KeyboardButton(Menu.LOTTERY),
        KeyboardButton(Menu.SUPPORT)
    )

    games = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🤖 Игра с ботом", callback_data="pvb"),
        InlineKeyboardButton("👥 Игра с соперником", callback_data="pvp:1"),
        InlineKeyboardButton("⚔ С соперником в чате", callback_data="pvpc")
    )

    lottery = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Участвовать!", url=settings.lottery_url)
    )

    support = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Поддержка", url=settings.support_url)
    )

    hide = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🛑 Закрыть", callback_data="hide")
    )

    pvb = InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("🎲 Создать", callback_data="pvb-create"),
        InlineKeyboardButton("📋 Мои игры", callback_data="pvb-history"),
        InlineKeyboardButton("<< Назад", callback_data="games"),
        InlineKeyboardButton("Инструкция", callback_data="pvb-instruction")
    )

    pvpc = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Вступить!", url=settings.pvpc_url)
    )

    join_chat_return = InlineKeyboardMarkup().add(
        InlineKeyboardButton("<< Назад", callback_data="dice-games"),
        InlineKeyboardButton("Вступить!", url=settings.pvpc_url),
    )

    try_too = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Попробовать тоже!", url=f"{settings.bot_url}?start=pvb]")
    )

    terms_and_conditions = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🛑 Отказаться", callback_data="terms-reject"),
        InlineKeyboardButton("✅ Подтвердить", callback_data="terms-accept")
    )

    dice_p2p_create = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🛑 Отменить", callback_data="dice-p2p:1"),
        InlineKeyboardButton("✅ Создать игру", callback_data="dice-p2p-create-confirm")
    )

    @staticmethod
    def back_to(path: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("<< Назад", callback_data=path)
        )

    @staticmethod
    def profile(beta_mode: bool) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("💵 Капуста", callback_data="transactions"),
            InlineKeyboardButton("💳 Транзакции", callback_data="transactions-mine"),
            InlineKeyboardButton("📋 Топ-5 лучших", callback_data="top5"),
            InlineKeyboardButton(f"{get_balance_emoji(beta_mode)} Бета-режим", callback_data=f"switch-beta"),
            InlineKeyboardButton("🛑 Закрыть", callback_data="hide")
        )

    @staticmethod
    def transactions() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("⬅ Вывести", callback_data="withdrawal"),
            InlineKeyboardButton("➡ Пополнить", callback_data="deposit"),
            InlineKeyboardButton("<< Назад", callback_data="profile")
        )

    @staticmethod
    def transactions_mine(transactions: list) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for transaction_id, status, method, transaction_type, amount, requested_at in transactions:
            if status == TransactionStatuses.CREATED:
                if transaction_type == "withdrawal":
                    callback_data = f"transaction-details:{transaction_id}"
                else:
                    callback_data = "none"

                sign = "⏳"
            elif status == WithdrawalStatuses.WAITING_FOR_PAYMENT:
                callback_data = "none"
                sign = "🟢"
            elif status == TransactionStatuses.COMPLETED:
                callback_data = "none"
                sign = "✅"
            elif status == TransactionStatuses.CANCELED_BY_ADMIN:
                callback_data = "none"
                sign = "❌"
            else:
                callback_data = "none"
                sign = "✋"

            method_caption = "биткоин-кошелёк" if method == "btc" else "карта"
            type_caption = "Списание" if transaction_type == "withdrawal" else "Пополнение"

            markup.add(
                InlineKeyboardButton(
                    f"{sign} {type_caption} {amount} ({method_caption})",
                    callback_data=callback_data
                )
            )

        markup.add(InlineKeyboardButton("<< Назад", callback_data="profile"))

        return markup

    @staticmethod
    def transaction_details(transaction_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("🛑 Отменить вывод", callback_data=f"transaction-cancel:{transaction_id}"),
            InlineKeyboardButton("<< Назад", callback_data="transactions-mine")
        )

    @staticmethod
    def top5(players: list, players_names: list) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for i, player in enumerate(players):
            player_id, winnings = player
            player_name = players_names[i - 1]

            markup.add(
                InlineKeyboardButton(
                    f"🥇 {winnings} RUB - {player_name}", callback_data=f"player:{player_id}:{winnings}:{i}"
                )
            )

        markup.add(InlineKeyboardButton("<< Назад", callback_data="profile"))

        return markup

    @staticmethod
    def demo(is_demo_mode) -> InlineKeyboardMarkup:
        caption = "💴 Демо-режим" if is_demo_mode else "💵 Обычный режим"

        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("<< Назад", callback_data="profile"),
            InlineKeyboardButton(caption, callback_data=f"demo:{int(not is_demo_mode)}")
        )

    @staticmethod
    def pvb_create(bots_turn_first: bool) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🛑 Отменить", callback_data="pvb"),
            InlineKeyboardButton(f"🔁 Первый {'бот' if bots_turn_first else 'я'}", callback_data="pvb-switch-turn"),
            InlineKeyboardButton("🎲 Начать", callback_data=f"pvb-start")
        )

    @staticmethod
    def dice_bot_mine(games: list) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        if len(games) == 0:
            markup.add(InlineKeyboardButton("🔔 Вы ещё ни разу не сыграли", callback_data="None"))
        else:
            for game_id, bet, result, demo_mode in games:
                if result == 1:
                    sign = "✅"
                elif result == 0:
                    sign = "💀"
                else:
                    sign = "✌️"

                if demo_mode == 1:
                    demo_emoji = "💴"
                else:
                    demo_emoji = "💵"

                markup.add(
                    InlineKeyboardButton(
                        f"{sign} Игра #{game_id:03} | {demo_emoji} {bet}", callback_data="None"
                    )
                )

        markup.add(InlineKeyboardButton("<< Назад", callback_data="dice-bot"))

        return markup

    @staticmethod
    def dice_p2p(
            user_id, games_available: list, page: int, pages_total: int, games_total: int
    ) -> InlineKeyboardMarkup:

        navigation = 0

        markup = InlineKeyboardMarkup()

        markup.add(
            InlineKeyboardButton("Создать", callback_data="dice-p2p-create"),
            InlineKeyboardButton("Обновить", callback_data="dice-p2p:1")
        )

        if page > pages_total:
            page = 1

        if pages_total == 0:
            markup.add(
                InlineKeyboardButton("Мои игры", callback_data=f"dice-p2p-mine:{page}"),
                InlineKeyboardButton("Рейтинг", callback_data=f"dice-p2p-rating:{page}")
            )
            markup.add(
                InlineKeyboardButton("<< Игры", callback_data="dice-games"),
                InlineKeyboardButton("Инструкция", callback_data=f"dice-p2p-instruction:{page}")
            )

            return markup

        elif pages_total == 1:
            page_fill_start = 0
            page_fill_end = games_total

        else:
            if page == 1:
                page_fill_start = 0
                page_fill_end = 5
                navigation = 1

            elif page == pages_total:
                page_fill_start = (pages_total - 1) * 5
                page_fill_end = games_total
                navigation = 2

            else:
                page_fill_start = (page - 1) * 5
                page_fill_end = page * 5
                navigation = 3

        for i in range(page_fill_start, page_fill_end):
            game_id, bet, demo_mode, creator_id = games_available[i]

            if demo_mode == 0:
                emoji = "💵"
            else:
                emoji = "💴"

            if creator_id == user_id:
                caption = "[Ваша]"
            else:
                caption = ""

            markup.add(
                InlineKeyboardButton(
                    f"{emoji}Игра #{game_id:03} | {bet} RUB {caption}",
                    callback_data=f"dice-p2p-details:{game_id}:{page}"
                )
            )

        if navigation == 1:
            markup.add(
                InlineKeyboardButton("Вперёд >>", callback_data=f"dice-p2p:{page + 1}")
            )
        elif navigation == 2:
            markup.add(
                InlineKeyboardButton("<< Назад", callback_data=f"dice-p2p:{page - 1}")
            )
        elif navigation == 3:
            markup.add(
                InlineKeyboardButton("<< Назад", callback_data=f"dice-p2p:{page - 1}"),
                InlineKeyboardButton("Вперёд >>", callback_data=f"dice-p2p:{page + 1}")
            )

        markup.add(
            InlineKeyboardButton("Мои игры", callback_data=f"dice-p2p-mine:{page}"),
            InlineKeyboardButton("Рейтинг", callback_data=f"dice-p2p-rating:{page}")
        )
        markup.add(
            InlineKeyboardButton("<< Игры", callback_data="dice-games"),
            InlineKeyboardButton("Инструкция", callback_data=f"dice-p2p-instruction:{page}")
        )

        return markup

    @staticmethod
    def dice_p2p_details(
            game_id: int, came_from: int, is_owner: bool, cancel_available: bool
    ) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        if is_owner and cancel_available:
            markup.add(
                InlineKeyboardButton("🛑 Отменить игру", callback_data=f"dice-p2p-cancel:{game_id}")
            )

        markup.add(
            InlineKeyboardButton("<< Назад", callback_data=f"dice-p2p:{came_from}")
        )

        return markup

    @staticmethod
    def join_fight(game_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("Давай", url=f"{settings.bot_url}?start=join{game_id}")
        )

    @staticmethod
    def join_in_chat(user_id, user_name, game_id, game_bet, game_rounds) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                "🎲 Присоединиться",
                callback_data=f"in-chat-join:{user_name.replace(':', '')}:{user_id}:{game_id}:{game_bet}:{game_rounds}"
            ),
            InlineKeyboardButton("🛑 Отменить", callback_data=f"in-chat-cancel:{user_id}")
        )

    @staticmethod
    def withdrawal(btc_fee: int, card_fee: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton(f"🪙 BTC {btc_fee}%", callback_data="withdrawal-amount:btc"),
            InlineKeyboardButton(f"💳 Card {card_fee}%", callback_data="withdrawal-amount:card"),
            InlineKeyboardButton("<< Назад", callback_data="transactions")
        )

    @staticmethod
    def deposit() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🪙 BTC", callback_data="deposit-amount:btc"),
            InlineKeyboardButton("💳 Card", callback_data="deposit-amount:card"),
            InlineKeyboardButton("<< Назад", callback_data="transactions")
        )

    @staticmethod
    def any_transaction_amount(
            is_amount_enough: bool, transaction_type: str, method: str, amount: int, btc_equivalent: float
    ) -> InlineKeyboardMarkup:
        if method == "card" or btc_equivalent != -1:
            if transaction_type == "withdrawal":
                back_callback_data = "withdrawal"
                forward_callback_data = "withdrawal-details"
            else:
                back_callback_data = "deposit"
                forward_callback_data = "deposit-amount-confirm"

            if is_amount_enough:
                return InlineKeyboardMarkup(row_width=2).add(
                    InlineKeyboardButton("<< Назад", callback_data=back_callback_data),
                    InlineKeyboardButton("Далее >>", callback_data=f"{forward_callback_data}:{method}:{amount}")
                )
            else:
                return InlineKeyboardMarkup(row_width=2).add(
                    InlineKeyboardButton("<< Назад", callback_data=back_callback_data)
                )
        else:
            return Markups.back_to("profile")

    @staticmethod
    def deposit_amount_confirm(method: str, btc_equivalent: float, amount: int) -> InlineKeyboardMarkup:
        if method == "card" or btc_equivalent != -1:
            return InlineKeyboardMarkup().add(
                InlineKeyboardButton("🛑 Отказаться", callback_data=f"deposit-amount:{method}"),
                InlineKeyboardButton("✅ Подтвердить", callback_data=f"deposit-confirm:{method}:{amount}")
            )
        else:
            return Markups.back_to("profile")

    @staticmethod
    def withdrawal_bank(are_blanks_filled: bool, method: str, amount: int) -> InlineKeyboardMarkup:
        if are_blanks_filled:
            return InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton("<< Назад", callback_data=f"withdrawal-details:{method}:{amount}"),
                InlineKeyboardButton("Далее >>", callback_data=f"withdrawal-confirm:{method}:{amount}")
            )
        else:
            return InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton("<< Назад", callback_data=f"withdrawal-details:{method}:{amount}")
            )

    @staticmethod
    def deposit_confirm(method: str, btc_equivalent: float, amount: int) -> InlineKeyboardMarkup:
        if method == "card" or btc_equivalent != -1:
            return InlineKeyboardMarkup().add(
                InlineKeyboardButton("<< Назад", callback_data=f"deposit-amount:{method}"),
                InlineKeyboardButton(
                    "✅ Подтвердить перевод", callback_data=f"confirmation:deposit:{method}:{amount}:0"
                )
            )
        else:
            return Markups.back_to(f"deposit-amount:{method}")

    @staticmethod
    def admin_any_transaction_confirm(
            transaction_type: str, transaction_id: int, amount: int, is_back_button_required=False
    ) -> InlineKeyboardMarkup:
        caption = "списать" if transaction_type == "withdrawal" else "зачислить"

        markup = InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton(
                f"✅ Подтвердить и {caption} {amount}", callback_data=f"admin-approbation:approve:{transaction_id}"
            ),
            InlineKeyboardButton(f"🛑 Отклонить", callback_data=f"admin-approbation:reject:{transaction_id}")
        )

        if is_back_button_required:
            markup.add(InlineKeyboardButton("<< Назад", callback_data="admin-transactions"))

        return markup

    @staticmethod
    def admin_approbation(transaction_type: str, transaction_id: int):
        if transaction_type == "withdrawal":
            return InlineKeyboardMarkup(row_width=1).add(
                InlineKeyboardButton(f"✅ Оплатить", callback_data=f"admin-withdrawal-paid:{transaction_id}")
            )
        else:
            return None

    @staticmethod
    def admin(
            pvb_active: bool, pvp_active: bool, pvpc_active: bool, pvpf_active: bool, transactions_active: bool
    ) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("📋 Общая статистика", callback_data="admin-total"),
            InlineKeyboardButton("⏳ Транзакции", callback_data="admin-transactions"),
            InlineKeyboardButton("🎲 Созданные игры", callback_data="admin-log-filtered"),
            InlineKeyboardButton("📢 Рассылка", callback_data="admin-call"),
            InlineKeyboardButton(
                f"{get_status_emoji(pvb_active)} PVB",
                callback_data=f"admin-switch-pvb"
            ),
            InlineKeyboardButton(
                f"{get_status_emoji(pvp_active)} PVP",
                callback_data=f"admin-switch-pvp"
            ),
            InlineKeyboardButton(
                f"{get_status_emoji(pvpc_active)} PVPC",
                callback_data=f"admin-switch-pvpc"
            ),
            InlineKeyboardButton(
                f"{get_status_emoji(pvpf_active)} Автоматические игры PVP",
                callback_data=f"admin-switch-pvpf"
            ),
            InlineKeyboardButton(
                f"{get_status_emoji(transactions_active)} Транзакции",
                callback_data=f"admin-switch-transactions"
            ),
        )
