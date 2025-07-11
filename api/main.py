from api.app import create_app
from api.config import config

environment = config['development']
app = create_app(environment)
if __name__ == "__main__":
    app.run()

# https://www.warp.dev/ terminal de linux en mac