def pytest_addoption(parser):
    # dataset_path: Path, save_to: Path, epochs: int
    parser.addoption("--dataset-path", action="store", default="default name")
    parser.addoption("--save-to", action="store", default="default name")
    parser.addoption("--epochs", action="store", default="default name")

option = None
def pytest_configure(config):
    global option
    option = config.option
    print(">>> option", option.dataset_path)
    print(">>> option", option.save_to)
    print(">>> option", option.epochs)
