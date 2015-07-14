ENV_NAME := env

all: env

clean: env-clean

env: $(ENV_NAME)/bin/activate

env-clean:
	rm -rf $(ENV_NAME)

$(ENV_NAME)/bin/activate: requirements.txt
	test -d $(ENV_NAME) || virtualenv --python=python2 $(ENV_NAME)
	$(ENV_NAME)/bin/pip install --upgrade pip
	$(ENV_NAME)/bin/pip install -Ur requirements.txt
	touch $(ENV_NAME)/bin/activate


