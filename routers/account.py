# This file contain routes regarding accounts
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from database.session import get_db
from database.models import Account as DBAccount
from Models.AccountResponse import AccountResponse
from Models.AccountRequest import AccountRequest
from Models.AccountUpdateRequest import AccountUpdateRequest
from auth.permissions import require_auth,get_current_user


router = APIRouter(
    prefix='/account',
    tags=['Account'],
    dependencies=[Depends(require_auth)]
)

@router.post('/create')
async def create_account(req_account : AccountRequest,db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    # create account
    # step 1 check account already exist.
    # step 2 create account
    # step 3 return account response

    account = db.query(DBAccount).filter(DBAccount.account_name == req_account.account_name).first()
    


    if account:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account Already Existed"
        )
    new_account = DBAccount(
        account_name = req_account.account_name,
        description = req_account.description,
        balance = req_account.balance,
        account_type = req_account.account_type,
        user_id = current_user.id,
        currency = req_account.currency,
       
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return AccountResponse.model_validate(new_account)

@router.get('/get_all', response_model=List[AccountResponse])
async def get_all_accounts(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    accounts = db.query(DBAccount).filter(DBAccount.user_id == current_user.id).all()
    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No accounts found"
        )
    return [AccountResponse.model_validate(account) for account in accounts]

@router.get('/get/{account_id}', response_model=AccountResponse)
async def get_account(account_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    account = db.query(DBAccount).filter(DBAccount.id == account_id, DBAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return AccountResponse.model_validate(account)
@router.put('/update/{account_id}', response_model=AccountResponse)
async def update_account(account_id: int, req_account: AccountRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    account = db.query(DBAccount).filter(DBAccount.id == account_id, DBAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update fields
    account.account_name = req_account.account_name
    account.description = req_account.description
    account.balance = req_account.balance
    account.account_type = req_account.account_type
    account.currency = req_account.currency
    
    db.commit()
    db.refresh(account)
    
    return AccountResponse.model_validate(account)

@router.delete('/delete/{account_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    account = db.query(DBAccount).filter(DBAccount.id == account_id, DBAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    db.delete(account)
    db.commit()
    
    return {"detail": "Account deleted successfully"}

@router.patch('/update/{account_id}', response_model=AccountResponse)  # ✅ PATCH for partial updates
async def update_account(
    account_id: int, 
    req_account: AccountUpdateRequest,
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    account = db.query(DBAccount).filter(DBAccount.id == account_id, DBAccount.user_id == current_user.id).first()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # ✅ Smart way: only update provided fields
    update_data = req_account.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return AccountResponse.model_validate(account)