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