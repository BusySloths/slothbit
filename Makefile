.PHONY: check doctor infer serve

check:
	uv run ruff check .
	uv run pytest

doctor:
	uv run slothbit doctor

infer:
	uv run slothbit infer "Explain ternary neural networks in three sentences."

serve:
	uv run slothbit serve
