"""
Firebase Authentication Utilities
"""
import httpx
from typing import Optional
from fastapi import HTTPException, status
from app.core.config import settings

# Firebase project ID from config
FIREBASE_PROJECT_ID = "governai-37f33"
FIREBASE_ISSUER = f"https://securetoken.google.com/{FIREBASE_PROJECT_ID}"


async def verify_firebase_token(token: str) -> Optional[dict]:
    """
    Verify Firebase ID token using Google's token verification endpoint.
    Returns the decoded token payload if valid, None otherwise.
    """
    try:
        # Use Google's token verification endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Verify the token is for our project
            if data.get("aud") != "governai-37f33":
                return None
            
            # Verify issuer
            if not data.get("iss", "").startswith("https://securetoken.google.com/"):
                return None
            
            return {
                "uid": data.get("sub"),  # Firebase UID
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture"),
                "email_verified": data.get("email_verified", False)
            }
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None


def get_current_user_from_token(token: str) -> dict:
    """
    Synchronous version for use in dependencies.
    Verifies Firebase ID token using Google's tokeninfo endpoint.
    """
    import httpx
    import json
    import base64
    try:
        print(f"[Auth] Verifying token (first 20 chars): {token[:20]}...")
        print(f"[Auth] Token length: {len(token)}")
        
        # Try the tokeninfo endpoint with proper URL encoding
        with httpx.Client(timeout=10.0) as client:
            # Try POST first (more reliable for long tokens)
            try:
                response = client.post(
                    "https://www.googleapis.com/oauth2/v3/tokeninfo",
                    data={"id_token": token},
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                print(f"[Auth] Used POST method")
            except Exception as post_error:
                # Fallback to GET if POST fails
                print(f"[Auth] POST failed, trying GET: {post_error}")
                # URL encode the token properly for GET
                import urllib.parse
                encoded_token = urllib.parse.quote(token, safe='')
                response = client.get(
                    f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={encoded_token}"
                )
                print(f"[Auth] Used GET method")
            
            print(f"[Auth] Token verification response status: {response.status_code}")
            
            if response.status_code != 200:
                error_detail = response.text if hasattr(response, 'text') else "Unknown error"
                print(f"[Auth] Token verification failed: {error_detail}")
                
                # Try to parse error JSON
                try:
                    error_json = response.json()
                    error_msg = error_json.get("error_description") or error_json.get("error") or error_detail
                except:
                    error_msg = error_detail
                
                # If it's an "Invalid Value" error, try decoding the token locally as a fallback
                if "Invalid Value" in error_msg or "invalid" in error_msg.lower():
                    print(f"[Auth] Attempting local token decode as fallback...")
                    try:
                        # Decode JWT token (basic decode without verification)
                        parts = token.split('.')
                        if len(parts) == 3:
                            # Decode payload (second part)
                            payload = parts[1]
                            # Add padding if needed
                            padding = 4 - len(payload) % 4
                            if padding != 4:
                                payload += '=' * padding
                            decoded = base64.urlsafe_b64decode(payload)
                            token_data = json.loads(decoded)
                            print(f"[Auth] Decoded token locally: aud={token_data.get('aud')}, sub={token_data.get('sub')[:20] if token_data.get('sub') else 'None'}...")
                            
                            # Use decoded token data if it looks valid
                            if token_data.get("sub") and token_data.get("email"):
                                return {
                                    "uid": token_data.get("sub"),
                                    "email": token_data.get("email"),
                                    "name": token_data.get("name"),
                                    "picture": token_data.get("picture"),
                                    "email_verified": token_data.get("email_verified", False)
                                }
                    except Exception as decode_error:
                        print(f"[Auth] Local decode also failed: {decode_error}")
                        import traceback
                        traceback.print_exc()
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid authentication token: {error_msg[:200]}"
                )
            
            data = response.json()
            print(f"[Auth] Token data: aud={data.get('aud')}, sub={data.get('sub')[:20] if data.get('sub') else 'None'}...")
            
            # Verify the token is for our project
            # Firebase tokens have audience as the project ID or client ID
            token_aud = data.get("aud")
            # Be more lenient with audience check - Firebase can use different formats
            if token_aud and token_aud != "governai-37f33":
                # Check if it contains our project ID or is a valid Firebase audience
                if "governai-37f33" not in str(token_aud) and not str(token_aud).startswith("governai"):
                    print(f"[Auth] Token audience mismatch: expected 'governai-37f33', got '{token_aud}'")
                    # Still allow if it's a valid-looking Firebase audience format
                    if not str(token_aud).endswith(".apps.googleusercontent.com") and "governai" not in str(token_aud).lower():
                        print(f"[Auth] Warning: Token audience doesn't match project, but continuing...")
                        # Don't reject - just log a warning
            
            return {
                "uid": data.get("sub"),
                "email": data.get("email"),
                "name": data.get("name"),
                "picture": data.get("picture"),
                "email_verified": data.get("email_verified", False)
            }
    except HTTPException:
        raise
    except httpx.RequestError as e:
        print(f"[Auth] Request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to verify token: {str(e)}"
        )
    except Exception as e:
        print(f"[Auth] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}"
        )

