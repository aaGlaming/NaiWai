from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    hashed = hash_password("MilkFrog123!")
    assert hashed != "MilkFrog123!"
    assert verify_password("MilkFrog123!", hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_round_trip():
    token = create_access_token(42)
    assert decode_access_token(token) == 42
    assert decode_access_token(token + "broken") is None
