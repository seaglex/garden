class Base(object):
    def instance_func(self):
        print(self, "original base instance_func")

    def instance_func2(self):
        print(self, "original base instance_func2")

    def instance_func3(self):
        print(self, "original base instance_func3")

    @staticmethod
    def static_func():
        print("original base static_func")


def new_instance_func(self):
    print(self, "new instance_func")


@staticmethod
def new_static_func():
    print("new static_func")


def new_instance_func3(self, *args):
    print("wrapping func3")
    return Base.instance_func3(self)


# original
obj1 = Base()
print("obj1")
obj1.instance_func()
obj1.static_func()

# update
print("updating methods...")
Base.instance_func = new_instance_func
Base.static_func = new_static_func

print("obj1")
obj1.instance_func()
obj1.static_func()

# self-update
print("self-updating methods...")
Base.instance_func = Base.instance_func2
print("obj1")
obj1.instance_func()
obj1.static_func()

# self-update2
print("self-updating wrapped methods...")
Base.instance_func = new_instance_func3
print("obj1")
obj1.instance_func()
obj1.static_func()
