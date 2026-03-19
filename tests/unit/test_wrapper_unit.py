from types import SimpleNamespace

from DEBtoolPyIF.estimation.wrapper import MATLABWrapper


def _build_wrapper():
    wrapper = MATLABWrapper.__new__(MATLABWrapper)
    wrapper.eng = None
    return wrapper


def test_start_matlab_engine_auto_connects_to_shared_session(monkeypatch):
    calls = []
    shared_engine = object()

    engine_stub = SimpleNamespace(
        find_matlab=lambda: ["shared-session"],
        connect_matlab=lambda session_name: calls.append(("connect", session_name)) or shared_engine,
        start_matlab=lambda: calls.append(("start", None)) or object(),
    )

    monkeypatch.setattr("DEBtoolPyIF.estimation.wrapper.matlab.engine", engine_stub)

    wrapper = _build_wrapper()
    wrapper.start_matlab_engine(MATLABWrapper.AUTO_SESSION)

    assert wrapper.eng is shared_engine
    assert calls == [("connect", "shared-session")]


def test_start_matlab_engine_auto_starts_when_no_shared_session_exists(monkeypatch):
    calls = []
    started_engine = object()

    engine_stub = SimpleNamespace(
        find_matlab=lambda: [],
        connect_matlab=lambda session_name: calls.append(("connect", session_name)) or object(),
        start_matlab=lambda: calls.append(("start", None)) or started_engine,
    )

    monkeypatch.setattr("DEBtoolPyIF.estimation.wrapper.matlab.engine", engine_stub)

    wrapper = _build_wrapper()
    wrapper.start_matlab_engine(MATLABWrapper.AUTO_SESSION)

    assert wrapper.eng is started_engine
    assert calls == [("start", None)]
