run:
	@export FLASK_ENV=development
	@python3 -m flask run

save:
	@git add --all
	@git commit -m "$(m)"

saved:
	@git add --all
	@git commit -m "$(m)"
	@git push

server:
	@export FLASK_DEBUG=1
	@export FLASK_APP=main
	@export FLASK_ENV=development
	@flask run --host=0.0.0.0 --port 8000

deploy:
	@gunicorn3 --workers=3 app:app --daemon

stop:
	@sudo pkill -f gunicorn3

update:
	@python3 ./utils/read_MongoDB.py
	@make stop
	@make deploy