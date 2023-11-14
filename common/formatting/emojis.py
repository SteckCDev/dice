def get_status_emoji(status: bool) -> str:
    return "🟢" if status else "🔴"


def get_balance_emoji(beta_mode: bool) -> str:
    return "💴" if beta_mode else "💵"
