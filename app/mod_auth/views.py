from . import auth


@auth.route('/login', methods=["POST", "GET"])
def login():
    """
    Login route for user's to login to their accounts
    :return: Login view
    """
    pass

@auth.route('/register', methods=["POST", "GET"])
def register():
    pass
