result = [
    (1, "A"),
    (1, None),
    (1, 3),
    (1, 1)
]

metrics_id = [row[1] for row in result if row[1] is not None]

print(metrics_id)