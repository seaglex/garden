from contextlib import ExitStack, contextmanager, AbstractContextManager


class MyResource(object):
    def __init__(self, id_):
        self.id_ = id_
        print(f"resource {self.id_} created")
    def close(self):
        print(f"resource {self.id_} destroyed")

    def do_work(self):
        print(f"resource {self.id_} working")

    @classmethod
    @contextmanager
    def create(cls, id_):
        resource = cls(id_)
        try:
            yield resource
        finally:
            resource.close()


class ManualManager(AbstractContextManager):
    def __init__(self):
        self.stack = ExitStack().__enter__()
        self.resources: list(MyResource) = []

    def __enter__(self):
        print("manager __enter__")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stack.__exit__(exc_type, exc_val, exc_tb)
        self.stack = None
        self.resources = []
        print("manager __exit__")

    def add_resource(self, resource):
        self.resources.append(self.stack.enter_context(resource))

    def do_work(self):
        for resource in self.resources:
            resource.do_work()

def run():
    with ManualManager() as manager:
        manager.add_resource(MyResource.create(1))
        manager.add_resource(MyResource.create(2))
        manager.add_resource(MyResource.create(3))
        manager.do_work()


if __name__ == '__main__':
    run()