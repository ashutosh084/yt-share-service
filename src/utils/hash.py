import bcrypt

def get_password_hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def compare_hash(source, target):
  return bcrypt.checkpw(source, target)
