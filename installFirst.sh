# After running this script in bash:
# to run servers:
#     Backend
#       export FLASK_ENV=development
#       pipenv run ./manage.py runserver

#     Front end in separate terminal
#       you must be skylinesC/ember
#       ember serve --proxy http://localhost:5000/
#       or
#       DEBUG=\* ember serve --proxy http://localhost:5000/

# To view website
#   http://localhost:4200/

git clone https://github.com/hess8/skylinesC
cd skylinesC
pipenv install --dev
pipenv shell

#  Now run installNext.sh	
