def merge_sort(arr, key, reverse=False):
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, reverse)
    right = merge_sort(arr[mid:], key, reverse)

    return _merge(left, right, key, reverse)


def _merge(left, right, key, reverse):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if reverse:
            if key(left[i]) >= key(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if key(left[i]) <= key(right[j]):
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


def top_n_routes(routes: list[dict], n: int = 20) -> list[dict]:
    sorted_routes = merge_sort(routes, key=lambda x: x["trip_count"], reverse=True)
    return sorted_routes[:n]


def detect_outliers_iqr(values: list[float]) -> tuple[float, float, list[int]]:
    n = len(values)
    if n < 4:
        return 0, 0, []

    sorted_vals = merge_sort(values, key=lambda x: x)

    def median(arr):
        m = len(arr)
        if m % 2 == 0:
            return (arr[m // 2 - 1] + arr[m // 2]) / 2
        return arr[m // 2]

    mid = n // 2
    if n % 2 == 0:
        lower_half = sorted_vals[:mid]
        upper_half = sorted_vals[mid:]
    else:
        lower_half = sorted_vals[:mid]
        upper_half = sorted_vals[mid + 1:]

    q1 = median(lower_half) if lower_half else 0
    q3 = median(upper_half) if upper_half else 0

    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_indices = []
    for i, val in enumerate(values):
        if val < lower_bound or val > upper_bound:
            outlier_indices.append(i)

    return lower_bound, upper_bound, outlier_indices
