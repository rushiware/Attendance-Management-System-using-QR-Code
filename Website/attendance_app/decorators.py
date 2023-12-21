from firebase_admin import auth
from django.shortcuts import redirect

def firebase_authenticated(view_func):
    """
    Decorator to check if the user is authenticated via Firebase.
    """
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is authenticated via Firebase
        uid_token = request.session.get('uid')

        if uid_token:
            try:
                # Verify the Firebase token using the request's session
                decoded_token = auth.verify_id_token(uid_token)
                # You can also extract user information from decoded_token if needed

                # If the token is valid, proceed to the original view
                return view_func(request, *args, **kwargs)

            except auth.InvalidIdTokenError:
                # Redirect to login page or handle unauthorized access
                return redirect('/signin/')  # Adjust the URL as needed
        else:
            # Redirect to login page or handle unauthorized access
            return redirect('/signin/')  # Adjust the URL as needed

    return _wrapped_view