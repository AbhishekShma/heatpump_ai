from decimal import Decimal

def row_to_dict(row):
    return {
        k: (float(v) if isinstance(v, Decimal) else v)
        for k, v in row.items()
    }

    # result = [row_to_dict(row) for row in rows]
    # return result