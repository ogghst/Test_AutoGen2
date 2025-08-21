from typing import Annotated, Literal, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class UserProfile:
    """A user profile for a social media platform."""
    
    # Basic user information
    username: Annotated[
        str, 
        "The unique username for the user. Must be 3-20 characters, alphanumeric plus underscores only. Example: 'john_doe123'"
    ]
    
    email: Annotated[
        str,
        "User's email address. Must be a valid email format. Used for notifications and login. Example: 'user@example.com'"
    ]
    
    full_name: Annotated[
        str,
        "User's display name. Can contain spaces and special characters. Example: 'John Doe Jr.'"
    ]
    
    # Age with constraints
    age: Annotated[
        int,
        "User's age in years. Must be between 13 and 120. Used for content filtering and age-appropriate recommendations."
    ]
    
    # Enum-like field with specific options
    account_type: Annotated[
        Literal["free", "premium", "enterprise"],
        "Type of user account. 'free' has basic features, 'premium' includes advanced features, 'enterprise' is for business users with admin capabilities."
    ]
    
    # Optional fields with defaults
    bio: Annotated[
        Optional[str],
        "User's biography/description. Optional field, max 500 characters. Can include emojis and hashtags. Set to None if not provided."
    ] = None
    
    profile_picture_url: Annotated[
        Optional[str],
        "URL to user's profile picture. Should be HTTPS URL pointing to an image file (jpg, png, gif). None means using default avatar."
    ] = None
    
    # Location information
    location: Annotated[
        Optional[str],
        "User's location (city, country). Used for local recommendations and timezone detection. Example: 'San Francisco, CA' or 'London, UK'"
    ] = None
    
    # Preferences as a list
    interests: Annotated[
        list[str],
        "List of user's interests/hobbies. Used for content recommendation algorithm. Examples: ['photography', 'travel', 'cooking', 'technology']"
    ] = field(default_factory=list)
    
    # Boolean flags with clear meanings
    is_verified: Annotated[
        bool,
        "Whether the user account is verified (blue checkmark). True for verified accounts, False otherwise. Only admins can set this."
    ] = False
    
    email_notifications: Annotated[
        bool,
        "User preference for receiving email notifications. True = send emails, False = no email notifications."
    ] = True
    
    is_private: Annotated[
        bool,
        "Privacy setting. True = private account (followers need approval), False = public account (anyone can follow)."
    ] = False
    
    # Timestamps
    created_at: Annotated[
        datetime,
        "Timestamp when the user account was created. Automatically set when user registers. Format: ISO datetime."
    ] = field(default_factory=datetime.now)
    
    last_login: Annotated[
        Optional[datetime],
        "Timestamp of user's last login. None if user has never logged in. Updated automatically on each login."
    ] = None
    
    # Numeric fields with business meaning
    follower_count: Annotated[
        int,
        "Number of users following this account. Automatically calculated, do not set manually. Used for influence scoring."
    ] = 0
    
    following_count: Annotated[
        int,
        "Number of accounts this user is following. Automatically calculated. Used to detect spam behavior if too high."
    ] = 0
    
    # Settings as nested structure
    privacy_settings: Annotated[
        dict[str, bool],
        "Dictionary of privacy preferences. Keys: 'show_email', 'show_age', 'allow_messages_from_strangers', 'show_online_status'. All values are boolean."
    ] = field(default_factory=lambda: {
        "show_email": False,
        "show_age": True,
        "allow_messages_from_strangers": False,
        "show_online_status": True
    })

    def __post_init__(self):
        """Validate the data after initialization."""
        # Validate username
        if not (3 <= len(self.username) <= 20):
            raise ValueError("Username must be 3-20 characters long")
        
        # Validate age
        if not (13 <= self.age <= 120):
            raise ValueError("Age must be between 13 and 120")
        
        # Validate bio length
        if self.bio and len(self.bio) > 500:
            raise ValueError("Bio cannot exceed 500 characters")

# Example usage and utility functions
def create_user_from_llm_input(llm_response: dict) -> UserProfile:
    """
    Create a UserProfile from LLM-generated data.
    The LLM should provide a dictionary matching the field names.
    """
    try:
        # Handle datetime strings if LLM provides them as strings
        if 'created_at' in llm_response and isinstance(llm_response['created_at'], str):
            llm_response['created_at'] = datetime.fromisoformat(llm_response['created_at'])
        
        if 'last_login' in llm_response and isinstance(llm_response['last_login'], str):
            llm_response['last_login'] = datetime.fromisoformat(llm_response['last_login'])
        
        return UserProfile(**llm_response)
    except Exception as e:
        raise ValueError(f"Failed to create UserProfile: {e}")

def get_field_descriptions(cls=UserProfile) -> dict[str, str]:
    """Extract all the annotation descriptions for LLM reference."""
    descriptions = {}
    for field_name, field_type in cls.__annotations__.items():
        if hasattr(field_type, '__metadata__'):
            descriptions[field_name] = field_type.__metadata__[0]
    return descriptions

# Example: Generate a prompt for an LLM
def generate_llm_prompt_for_user_creation() -> str:
    """Generate a detailed prompt for an LLM to create a UserProfile."""
    descriptions = get_field_descriptions()
    
    prompt = """Create a realistic user profile with the following fields:

"""
    
    for field_name, description in descriptions.items():
        prompt += f"- {field_name}: {description}\n"
    
    prompt += """
Please provide the data as a JSON object with these exact field names.
Example format:
{
    "username": "example_user",
    "email": "user@email.com",
    ...
}
"""
    return prompt

# Example usage
if __name__ == "__main__":
    # Example 1: Create a user manually
    user = UserProfile(
        username="jane_doe",
        email="jane@example.com",
        full_name="Jane Doe",
        age=28,
        account_type="premium",
        bio="Travel enthusiast and photographer 📸",
        interests=["photography", "travel", "hiking"]
    )
    
    print("Created user:", user.username)
    
    # Example 2: Show what an LLM would see
    print("\nField descriptions for LLM:")
    descriptions = get_field_descriptions()
    for field, desc in descriptions.items():
        print(f"{field}: {desc}")
    
    # Example 3: Generate LLM prompt
    print("\nLLM Prompt:")
    print(generate_llm_prompt_for_user_creation())