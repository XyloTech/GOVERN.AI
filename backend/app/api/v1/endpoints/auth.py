"""
Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.firebase_auth import get_current_user_from_token
from app.models.user import User, UserRole

router = APIRouter()


class UserSyncRequest(BaseModel):
    firebase_uid: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from Firebase token"""
    print(f"[Auth] Authorization header: {authorization[:50] if authorization else 'None'}...")
    
    if not authorization or not authorization.startswith("Bearer "):
        print("[Auth] Missing or invalid authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.split("Bearer ")[1].strip()
    if not token:
        print("[Auth] Empty token after Bearer prefix")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty authentication token"
        )
    
    try:
        firebase_user = get_current_user_from_token(token)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[Auth] Error getting user from token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
    
    # Find or create user in database
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    
    if not user:
        # Create new user
        user = User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user["email"],
            full_name=firebase_user.get("name", firebase_user["email"].split("@")[0]),
            photo_url=firebase_user.get("picture"),
            role=UserRole.EXECUTIVE,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update user info if changed
        if firebase_user.get("email") and user.email != firebase_user["email"]:
            user.email = firebase_user["email"]
        if firebase_user.get("name") and user.full_name != firebase_user["name"]:
            user.full_name = firebase_user["name"]
        if firebase_user.get("picture") and user.photo_url != firebase_user["picture"]:
            user.photo_url = firebase_user["picture"]
        db.commit()
        db.refresh(user)
    
    return user


@router.post("/sync")
async def sync_user(
    user_data: UserSyncRequest,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Sync Firebase user with backend database"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token"
        )
    
    token = authorization.split("Bearer ")[1]
    firebase_user = get_current_user_from_token(token)
    
    # Verify the UID matches
    if firebase_user["uid"] != user_data.firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="UID mismatch"
        )
    
    # Find or create user
    user = db.query(User).filter(User.firebase_uid == user_data.firebase_uid).first()
    
    if not user:
        user = User(
            firebase_uid=user_data.firebase_uid,
            email=user_data.email,
            full_name=user_data.display_name or user_data.email.split("@")[0],
            photo_url=user_data.photo_url,
            role=UserRole.EXECUTIVE,
            is_active=True
        )
        db.add(user)
    else:
        # Update if needed
        if user_data.email and user.email != user_data.email:
            user.email = user_data.email
        if user_data.display_name and user.full_name != user_data.display_name:
            user.full_name = user_data.display_name
        if user_data.photo_url and user.photo_url != user_data.photo_url:
            user.photo_url = user_data.photo_url
    
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "photo_url": user.photo_url,
        "role": user.role.value
    }


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "photo_url": current_user.photo_url,
        "role": current_user.role.value,
        "is_active": current_user.is_active
    }

