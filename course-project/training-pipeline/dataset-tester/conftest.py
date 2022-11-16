def pytest_addoption(parser):
    parser.addoption("--dataset-path", action="store", default="default name")


def pytest_generate_tests(metafunc):
    option_value = metafunc.config.option.dataset_path
    if 'dataset_path' in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("dataset_path", [option_value])
