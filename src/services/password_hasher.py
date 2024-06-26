from passlib.context import CryptContext


class PasswordHasher:
  pwd_context: CryptContext
  schemes = ["bcrypt"]
  
  def __init__(self) -> None:
    self.pwd_context = CryptContext(schemes=self.schemes)
    
  def hash_password(self, password: str) -> str:
    """Method to hash a given password

    Args:
        password (str): The string to be hashed

    Returns:
        str: The hashed password
    """
    return self.pwd_context.hash(password)
  
  def compare_passwords(self, provided_password: str, actual_password: str) -> bool:
    """Method to compare provided_password to the hashed actual_password

    Args:
        provided_password (str): The password to validate
        actual_password (str): The hashed password to validate against

    Returns:
        bool: True if the passwords match, False if not.
    """
    return self.pwd_context.verify(provided_password, actual_password)