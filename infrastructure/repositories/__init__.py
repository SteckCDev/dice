from .admin import RedisAdminRepository as __RedisAdminRepository
from .config import RedisConfigRepository as __RedisConfigRepository
from .currency import BlockchainInfoCurrencyRepository as __BlockchainInfoCurrencyRepository
from .pvb import PostgresRedisPVBRepository as __PostgresRedisPVBRepository
from .pvp import PostgresRedisPVPRepository as __PostgresRedisPVPRepository
from .pvpc import PostgresRedisPVPCRepository as __PostgresRedisPVPCRepository
from .transaction import PostgresRedisTransactionRepository as __PostgresRedisTransactionRepository
from .user import PostgresRedisUserRepository as __PostgresRedisUserRepository


ImplementedAdminRepository = __RedisAdminRepository
ImplementedConfigRepository = __RedisConfigRepository
ImplementedCurrencyRepository = __BlockchainInfoCurrencyRepository
ImplementedPVBRepository = __PostgresRedisPVBRepository
ImplementedPVPRepository = __PostgresRedisPVPRepository
ImplementedPVPCRepository = __PostgresRedisPVPCRepository
ImplementedTransactionRepository = __PostgresRedisTransactionRepository
ImplementedUserRepository = __PostgresRedisUserRepository
