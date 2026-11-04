def get_auth_error_message(error: Exception, action: str) -> str:
    raw_message = str(error).lower()
    if action == "signup":
        if "already registered" in raw_message or "already exists" in raw_message:
            return "This email is already registered. Please log in instead."
        if "invalid email" in raw_message:
            return "Please enter a valid email address."
        if "password" in raw_message and ("weak" in raw_message or "short" in raw_message):
            return "Your password is too weak. Please use at least 6 characters."
        return "We could not create your account. Please check your details and try again."

    if "invalid login credentials" in raw_message or "invalid credentials" in raw_message:
        return "Incorrect email or password. Please try again."
    if "email not confirmed" in raw_message:
        return "Please verify your email before logging in."
    return "We could not log you in. Please check your email and password."