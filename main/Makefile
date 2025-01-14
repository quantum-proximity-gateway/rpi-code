PYTHON_CMD=$(shell pwd)/venv/bin/python3

RECOGNISE_SCRIPT=recognise.py
REGISTER_SCRIPT=register_user.py
TRAIN_SCRIPT=train_model.py

recognise:
	sudo $(PYTHON_CMD) $(RECOGNISE_SCRIPT)

register:
	@sudo $(PYTHON_CMD) $(REGISTER_SCRIPT) $(filter-out $@,$(MAKECMDGOALS))

train:
	sudo $(PYTHON_CMD) $(TRAIN_SCRIPT)

%:
	@:
