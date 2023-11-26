class BalanceIsNotEnoughError(ValueError):
    pass


class BetOutOfLimitsError(ValueError):
    pass


class PVPAlreadyStartedError(ValueError):
    pass


class PVPNotFoundForUserError(ValueError):
    pass


class PVPCreatorLate(ValueError):
    pass
