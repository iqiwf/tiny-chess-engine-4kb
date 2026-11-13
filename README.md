tiny-chess-01 entry: a 4 KB Python chess engine.

main.py is an lzma+base85 packed payload of a 0x88 alpha-beta engine:
negamax with quiescence, null-move pruning, late-move reductions,
killer/history ordering, PST evaluation. It talks to the env over HTTP.
