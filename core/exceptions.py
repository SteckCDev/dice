class BalanceIsNotEnoughError(ValueError):
    pass


class BetOutOfLimitsError(ValueError):
    pass


class PVPAlreadyStartedError(ValueError):
    pass


class PVPNotFoundForUserError(ValueError):
    pass


class PVPCreatorLateError(ValueError):
    pass


class PVPJoinRejectedError(ValueError):
    pass


class PVPCNotFoundForUserError(ValueError):
    pass


class PVPCJoinRejectedError(ValueError):
    pass


class PVPCAlreadyInGameError(ValueError):
    pass


class PVPCAlreadyStartedError(ValueError):
    pass


class PVPCCancellationRejectedError(ValueError):
    pass
