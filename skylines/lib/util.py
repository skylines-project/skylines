from itsdangerous import Signer, BadSignature


def str_to_bool(str):
    return str.lower() in ['1', 'true', 't', 'yes', 'y']


def pressure_alt_to_qnh_alt(altitude, qnh):
    if qnh is None:
        qnh = 1013.25

    k1 = 0.190263
    inv_k1 = 1.0 / 0.190263
    k2 = 8.417286e-5
    inv_k2 = 1.0 / 8.417286e-5

    static_pressure = ((1013.25 ** k1) - k2 * altitude) ** inv_k1

    return (qnh ** k1 - static_pressure ** k1) * inv_k2


def sign_message(msg, secret):
    signer = Signer(secret)
    if not isinstance(msg, str):
        msg = str(msg)
    return signer.sign(msg)


def unsign_message(token, secret):
    try:
        signer = Signer(secret)
        return signer.unsign(token)
    except BadSignature:
        return token