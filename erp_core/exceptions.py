# erp_core/exceptions.py
class ERPException(Exception): pass
class DatabaseError(ERPException): pass
class ValidationError(ERPException): pass
class PermissionDeniedError(ERPException): pass
class TransactionError(ERPException): pass
class DuplicateTransactionError(TransactionError): pass
class AccountingError(ERPException): pass
class CreditLimitError(ERPException): pass
class CreditLimitExceededError(CreditLimitError): pass
class RPCError(ERPException): pass
