from math import ceil


def paginate(
    query,
    page: int = 1,
    limit: int = 10,
):
    """
    Generic pagination utility.
    """

    if page < 1:
        page = 1

    if limit < 1:
        limit = 10

    total = query.count()

    items = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": ceil(total / limit) if total else 1,
        "items": items,
    }