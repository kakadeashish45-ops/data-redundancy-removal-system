import tempfile, os
import app

def test_normalize():
    assert app.normalize(" Rahul Patil ") == "rahulpatil"

def test_fingerprint_same_for_formatting():
    a = app.fingerprint("Rahul Patil", "R@Example.com", "987-654-3210", "Pune")
    b = app.fingerprint("rahulpatil", "r@example.com", "9876543210", "Pune")
    assert a == b
