# This file contain routes regarding transactions
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from database.session import get_db
from database.models import Account as DBAccount, Category as DBCategory,Transaction as DBTransaction

# Updated imports to use new model structure
from Models.accounts import AccountResponse, AccountCreateRequest, AccountUpdateRequest
from auth.permissions import require_auth, get_current_user
from Models.transactions import TransactionCreateRequest,TransactionType,TransactionResponse,TransactionUpdateRequest


router = APIRouter(
    prefix='/transaction',
    tags=['Transaction'],
    dependencies=[Depends(require_auth)]
)

# Helper functions for balance management
def reverse_transaction_balance(transaction: DBTransaction, db: Session):
    """Reverse the balance changes of a transaction"""
    # Get the accounts
    from_account = db.query(DBAccount).filter(DBAccount.id == transaction.account_id).first()
    to_account = None
    if transaction.to_account:
        to_account = db.query(DBAccount).filter(DBAccount.id == transaction.to_account).first()
    
    # Reverse the balance changes
    if transaction.transaction_type == TransactionType.INCOME:
        from_account.balance -= transaction.amount
    elif transaction.transaction_type == TransactionType.EXPENSE:
        from_account.balance += transaction.amount
    elif transaction.transaction_type == TransactionType.TRANSFER:
        from_account.balance += transaction.amount  # Add back to source
        if to_account:
            to_account.balance -= transaction.amount  # Remove from destination

def apply_transaction_balance(transaction_data, from_account, to_account=None):
    """Apply balance changes for a transaction"""
    if transaction_data.transaction_type == TransactionType.INCOME:
        from_account.balance += transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.EXPENSE:
        from_account.balance -= transaction_data.amount
    elif transaction_data.transaction_type == TransactionType.TRANSFER:
        from_account.balance -= transaction_data.amount
        if to_account:
            to_account.balance += transaction_data.amount

@router.post('/create')
async def create_transaction(req_transaction: TransactionCreateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Create a new Transaction
    """
    # Step 1: Check if accounts exist
    from_account = db.query(DBAccount).filter(
        DBAccount.id == req_transaction.account_id,
        DBAccount.user_id == current_user.id
    ).first()
    
    if not from_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="From account not found"
        )
    
    # Step 2: Handle to_account (only for transfers)
    to_account = None
    if req_transaction.to_account_id:
        to_account = db.query(DBAccount).filter(
            DBAccount.id == req_transaction.to_account_id,
            DBAccount.user_id == current_user.id
        ).first()
    
    # Step 3: Check category exists
    category = db.query(DBCategory).filter(
        DBCategory.id == req_transaction.category_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found"
        )
    
    # Step 4: Validate transaction type requirements
    if req_transaction.transaction_type == TransactionType.TRANSFER:
        if not to_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="To account not found for transfer"
            )
    
    # Step 5: Check balance for outgoing transactions
    if req_transaction.transaction_type in (TransactionType.TRANSFER, TransactionType.EXPENSE):
        if from_account.balance < req_transaction.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance in from account"
            )
    
    # Step 6: Update account balances
    if req_transaction.transaction_type == TransactionType.INCOME:
        from_account.balance += req_transaction.amount
    elif req_transaction.transaction_type == TransactionType.EXPENSE:
        from_account.balance -= req_transaction.amount
    elif req_transaction.transaction_type == TransactionType.TRANSFER:
        from_account.balance -= req_transaction.amount
        to_account.balance += req_transaction.amount
    
    # Step 7: Create transaction record
    new_transaction = DBTransaction(
        transaction_name=req_transaction.transaction_name,
        account_id=req_transaction.account_id,
        to_account=getattr(req_transaction,'to_account_id',None),
        category_id=req_transaction.category_id,
        amount=req_transaction.amount,
        transaction_type=req_transaction.transaction_type,
        description=getattr(req_transaction,'description', None),
        user_id=current_user.id
    )
    
    db.add(new_transaction)
    db.commit()
    
    # Step 8: Refresh objects (only if they exist)
    db.refresh(from_account)
    if to_account:
        db.refresh(to_account)
    db.refresh(new_transaction)
    
    return TransactionResponse.model_validate(new_transaction)

@router.get('/get_all', response_model=List[TransactionResponse])
async def get_all_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    account_id: Optional[int] = Query(None, description="Filter by account ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    transaction_type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    start_date: Optional[datetime] = Query(None, description="Filter from date"),
    end_date: Optional[datetime] = Query(None, description="Filter to date"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all transactions for the current user with filtering and pagination"""
    
    # Base query - only user's transactions
    query = db.query(DBTransaction).filter(DBTransaction.user_id == current_user.id)
    
    # Apply filters
    if account_id:
        # Verify account belongs to user
        account_check = db.query(DBAccount).filter(
            DBAccount.id == account_id,
            DBAccount.user_id == current_user.id
        ).first()
        if not account_check:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        query = query.filter(DBTransaction.account_id == account_id)
    
    if category_id:
        query = query.filter(DBTransaction.category_id == category_id)
    
    if transaction_type:
        query = query.filter(DBTransaction.transaction_type == transaction_type)
    
    if start_date:
        query = query.filter(DBTransaction.date >= start_date)
    
    if end_date:
        query = query.filter(DBTransaction.date <= end_date)
    
    # Apply pagination and ordering (newest first)
    transactions = query.order_by(DBTransaction.date.desc()).offset(skip).limit(limit).all()
    
    return [TransactionResponse.model_validate(transaction) for transaction in transactions]



@router.get('/get/{transaction_id}', response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """
    Get a single transaction by ID
    """
    transaction = db.query(DBTransaction).filter(
        DBTransaction.id == transaction_id,
        DBTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.model_validate(transaction)

@router.put('/{transaction_id}', response_model=TransactionResponse)
async def update_transaction(
    transaction_id: int,
    request: TransactionUpdateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a transaction with proper balance management"""
    
    # Get existing transaction
    existing_transaction = db.query(DBTransaction).filter(
        DBTransaction.id == transaction_id,
        DBTransaction.user_id == current_user.id
    ).first()
    
    if not existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Store original values for balance reversal
    original_account_id = existing_transaction.account_id
    original_amount = existing_transaction.amount
    original_type = existing_transaction.transaction_type
    
    # Get the account for the existing transaction
    original_account = db.query(DBAccount).filter(
        DBAccount.id == original_account_id,
        DBAccount.user_id == current_user.id
    ).first()
    
    if not original_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original account not found"
        )
    
    # Reverse the original transaction's balance effect
    reverse_transaction_balance(original_account, original_amount, original_type)
    
    # Update transaction fields
    update_data = request.model_dump(exclude_unset=True)
    
    # Validate new account if changed
    new_account_id = update_data.get('account_id', original_account_id)
    if new_account_id != original_account_id:
        new_account = db.query(DBAccount).filter(
            DBAccount.id == new_account_id,
            DBAccount.user_id == current_user.id
        ).first()
        
        if not new_account:
            # Restore original balance since we're failing
            apply_transaction_balance(original_account, original_amount, original_type)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="New account not found"
            )
    else:
        new_account = original_account
    
    # Validate new category if provided
    if 'category_id' in update_data and update_data['category_id']:
        category = db.query(DBCategory).filter(
            DBCategory.id == update_data['category_id']
        ).first()
        
        if not category:
            # Restore original balance since we're failing
            apply_transaction_balance(original_account, original_amount, original_type)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Apply updates to the transaction
    for field, value in update_data.items():
        setattr(existing_transaction, field, value)
    
    # Apply new transaction's balance effect
    new_amount = existing_transaction.amount
    new_type = existing_transaction.transaction_type
    apply_transaction_balance(new_account, new_amount, new_type)
    
    try:
        db.commit()
        db.refresh(existing_transaction)
        return TransactionResponse.model_validate(existing_transaction)
    
    except Exception as e:
        db.rollback()
        # Restore original balance state
        reverse_transaction_balance(new_account, new_amount, new_type)
        apply_transaction_balance(original_account, original_amount, original_type)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update transaction: {str(e)}"
        )

@router.delete('/{transaction_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a transaction with proper balance management"""
    
    # Get the transaction to delete
    transaction = db.query(DBTransaction).filter(
        DBTransaction.id == transaction_id,
        DBTransaction.user_id == current_user.id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    # Get the account to reverse balance changes
    account = db.query(DBAccount).filter(
        DBAccount.id == transaction.account_id,
        DBAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Reverse the transaction's balance effect
    reverse_transaction_balance(account, transaction.amount, transaction.transaction_type)
    
    try:
        # Delete the transaction
        db.delete(transaction)
        db.commit()
        
    except Exception as e:
        db.rollback()
        # Restore balance if deletion failed
        apply_transaction_balance(account, transaction.amount, transaction.transaction_type)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete transaction: {str(e)}"
        )

