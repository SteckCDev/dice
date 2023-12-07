from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from core.schemas.pvb import PVBDTO
from core.schemas.pvp import PVPDTO, PVPDetailsDTO
from core.schemas.user import UserDTO
from settings import settings
from .formatting.emojis import get_status_emoji, get_balance_emoji
from .menu import Menu


class Markups:
    @staticmethod
    def back_to(path: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("<< Назад", callback_data=path)
        )

    @staticmethod
    def navigation() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(
            KeyboardButton(Menu.GAMES),
            KeyboardButton(Menu.PROFILE),
            KeyboardButton(Menu.LOTTERY),
            KeyboardButton(Menu.SUPPORT)
        )

    @staticmethod
    def games() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("🤖 Игра с ботом", callback_data="pvb"),
            InlineKeyboardButton("👥 Игра с соперником", callback_data="pvp:1"),
            InlineKeyboardButton("⚔ С соперником в чате", callback_data="pvpc")
        )

    @staticmethod
    def profile(beta_mode: bool) -> InlineKeyboardMarkup:
        beta_caption = "Выключить бета-режим" if beta_mode else "Включить бета-режим"

        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("💳 Транзакции", callback_data="transactions"),
            InlineKeyboardButton("📋 Топ-5 лучших", callback_data="top5"),
            InlineKeyboardButton(f"{get_balance_emoji(beta_mode)} {beta_caption}", callback_data=f"switch-beta")
        )

    @staticmethod
    def lottery() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("Участвовать!", url=settings.lottery_url)
        )

    @staticmethod
    def support() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("Поддержка", url=settings.support_url)
        )

    @staticmethod
    def terms_and_conditions() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🛑 Отказаться", callback_data="terms-reject"),
            InlineKeyboardButton("✅ Подтвердить", callback_data="terms-accept")
        )

    @staticmethod
    def pvb() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("Инструкция", callback_data="pvb-instruction"),
            InlineKeyboardButton("📋 Мои игры", callback_data="pvb-history"),
            InlineKeyboardButton("<< Назад", callback_data="games"),
            InlineKeyboardButton("🎲 Создать", callback_data="pvb-create")
        )

    @staticmethod
    def pvb_create(bots_turn_first: bool) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("Обновить", callback_data="pvb-create"),
            InlineKeyboardButton(f"🔁 Первый {'бот' if bots_turn_first else 'я'}", callback_data="pvb-switch-turn"),
            InlineKeyboardButton("<< Назад", callback_data="pvb"),
            InlineKeyboardButton("🎲 Начать", callback_data=f"pvb-start")
        )

    @staticmethod
    def pvb_history(games_pvb: list[PVBDTO] | None) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        if games_pvb is None:
            markup.add(
                InlineKeyboardButton(
                    "🔔 Вы ещё ни разу не сыграли", callback_data="None"
                ),
                InlineKeyboardButton("<< Назад", callback_data="pvb")
            )
            return markup

        for pvb in games_pvb:
            if pvb.player_won is None:
                sign = "🤝"
            elif pvb.player_won:
                sign = "💰"
            else:
                sign = "💀"

            markup.add(
                InlineKeyboardButton(
                    f"{sign} Игра #{pvb.id:03} | {get_balance_emoji(pvb.beta_mode)} {pvb.bet}",
                    callback_data="None"
                )
            )

        markup.add(
            InlineKeyboardButton("<< Назад", callback_data="pvb")
        )

        return markup

    @staticmethod
    def pvp(user_id: int, games_pvp: list[PVPDTO] | None, pages_total: int, page: int = 0) -> InlineKeyboardMarkup:
        if games_pvp is None:
            return InlineKeyboardMarkup(row_width=2).add(
                InlineKeyboardButton("Рейтинг", callback_data="pvp-rating"),
                InlineKeyboardButton("Мои игры", callback_data="pvp-history"),
                InlineKeyboardButton("Инструкция", callback_data="pvp-instruction"),
                InlineKeyboardButton("Обновить", callback_data=f"pvp:1"),
                InlineKeyboardButton("<< Назад", callback_data="games"),
                InlineKeyboardButton("🎲 Создать", callback_data="pvp-create"),
            )

        if page > pages_total:
            page = 1

        pagination_options_mode: int = 0

        if pages_total == 1:
            page_fill_start = 0
            page_fill_end = len(games_pvp)

        else:
            if page == 1:
                page_fill_start = 0
                page_fill_end = 5
                pagination_options_mode = 1

            elif page == pages_total:
                page_fill_start = (pages_total - 1) * 5
                page_fill_end = len(games_pvp)
                pagination_options_mode = 2

            else:
                page_fill_start = (page - 1) * 5
                page_fill_end = page * 5
                pagination_options_mode = 3

        markup: InlineKeyboardMarkup = InlineKeyboardMarkup(row_width=2)

        markup.add(
            InlineKeyboardButton("Рейтинг", callback_data=f"pvp-rating"),
            InlineKeyboardButton("Мои игры", callback_data=f"pvp-history")
        )

        for i in range(page_fill_start, page_fill_end):
            markup.add(
                InlineKeyboardButton(
                    f"{get_balance_emoji(games_pvp[i].beta_mode)} "
                    f"Игра #{games_pvp[i].id:03} | {games_pvp[i].bet} RUB "
                    f"{'[Ваша]' if games_pvp[i].creator_tg_id == user_id else ''}",
                    callback_data=f"pvp-details:{games_pvp[i].id}:{page}"
                )
            )

        if pagination_options_mode == 1:
            markup.add(
                InlineKeyboardButton("Вперёд >>", callback_data=f"pvp:{page + 1}")
            )
        elif pagination_options_mode == 2:
            markup.add(
                InlineKeyboardButton("<< Назад", callback_data=f"pvp:{page - 1}")
            )
        elif pagination_options_mode == 3:
            markup.add(
                InlineKeyboardButton("<< Назад", callback_data=f"pvp:{page - 1}"),
                InlineKeyboardButton("Вперёд >>", callback_data=f"pvp:{page + 1}")
            )

        markup.add(
            InlineKeyboardButton("Инструкция", callback_data=f"pvp-instruction"),
            InlineKeyboardButton("Обновить", callback_data=f"pvp:1")
        )
        markup.add(
            InlineKeyboardButton("<< Назад", callback_data="games"),
            InlineKeyboardButton("🎲 Создать", callback_data="pvp-create")
        )

        return markup

    @staticmethod
    def pvp_details(user: UserDTO, pvp_details: PVPDetailsDTO, page: int) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup(row_width=1)

        if user.tg_id == pvp_details.creator_tg_id and pvp_details.cancellation_unlocks_in is None:
            markup.add(
                InlineKeyboardButton("🛑 Отменить игру", callback_data=f"pvp-cancel:{pvp_details.id}")
            )

        markup.add(
            InlineKeyboardButton("<< Назад", callback_data=f"pvp:{page}")
        )

        return markup

    @staticmethod
    def pvp_create() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("<< Назад", callback_data="pvp"),
            InlineKeyboardButton("Обновить", callback_data="pvp-create"),
            InlineKeyboardButton("🎲 Создать игру", callback_data="pvp-confirm")
        )

    @staticmethod
    def pvpc() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup().add(
            InlineKeyboardButton("Вступить!", url=settings.pvpc_url)
        )

    @staticmethod
    def pvpc_join(game_id: int) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("🎲 Присоединиться", callback_data=f"pvpc-join:{game_id}"),
            InlineKeyboardButton("💀 Отменить", callback_data=f"pvpc-cancel:{game_id}")
        )

    @staticmethod
    def admin(
            pvb_active: bool, pvp_active: bool, pvpc_active: bool, pvpf_active: bool, transactions_active: bool
    ) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("📋 Общая статистика", callback_data="admin-total"),
            InlineKeyboardButton("⏳ Транзакции", callback_data="admin-transactions"),
            InlineKeyboardButton("🎲 Созданные игры", callback_data="admin-log-filtered"),
            InlineKeyboardButton("📢 Рассылка", callback_data="admin-mailing"),
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

    @staticmethod
    def admin_mailing() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(row_width=1).add(
            InlineKeyboardButton("📢 Начать рассылку", callback_data="admin-mailing-start"),
            InlineKeyboardButton("📋 Предпросмотр", callback_data="admin-mailing-preview"),
            InlineKeyboardButton("<< Назад", callback_data="admin")
        )
