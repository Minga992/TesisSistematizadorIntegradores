import statistics


def flatten(t):
    return [item for sublist in t for item in sublist]


def onlyNotNone(values):
    return list(filter(lambda x: x is not None, values))


def statsOfValues(values, units, ignoreNone=False):
    notNoneValues = values if not ignoreNone else onlyNotNone(values)

    try:
        mean = statistics.mean(notNoneValues)
        stdev = statistics.stdev(notNoneValues) if len(notNoneValues) > 1 else 0.0
    # Lo explicito porque lo vi, si aparecen valores muy grandes (por ej. en el maxError de alguna variable)
    # Revienta por los aires. No hay manera de zafarlo, son números más allá de la capacidad de representación
    # de los floats que usa statistics. No debería aparecer en experimentos razonables, creo.
    except OverflowError:
        raise
    return {"mean": mean, "stdev": stdev, "values": values, "units": units}


def statsOfKeyInArray(key, array, units):
    values = [x[key] for x in array]
    return statsOfValues(values=values, units=units)
