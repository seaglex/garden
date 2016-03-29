## try_buildin_impl
### try_memeory
 * test the memory consumption of build-in types
   * in x64 machine
 * value to value-interface
   * go makes a copy of the value
   * each interface consumes 912 bytes (sizeof(value) == 816)
 * function
   * pure member function (receiver as the first argument) == function
   * (pointer-based) member function use 24 bytes
     * However, sizeof(member function) == 8
 * memory consumption

|type|bytes|
| -- | -- |
|func |8 |
|member-func|24|
|interface| 16 |
|pointer | 8 |
|slice|24|
|map|8|
|chan|8|
|string|16|
|array|sizeof(value)|

 * memory consumption of value-based member-func/interface

|sizeof(value)|member-func|interface|
|--|--|--|
|1 |24 | 17|
|8 |24 | 24|
|16 |40 | 32|
|24 |40 | 48|
|32 |56 | 48|
|40 |56 | 64|
|48 |72 | 64|
|56 |72 | 80|
|64 |88 | 80|
|80 |104 | 96|
|88 |104 | 112|
|96 |120 | 116|
|400 |424 | 432|
|800 |904 | 912|


### try_structure
 * demostrate the structure of build-in types
   * in x64 machine
 * demostrate the difference between empty and nil
   * empty != nil for alll types
   * nil is more a special state
 * func
   * struct {addr}
   * nil: {0}
   * addr refers a 8 bytes struct {func-addr}
     * addr itself is a small address
     * func-addr is a small address
     * fmt.Print(func-addr) == fmt.Print(func)
   * member-function w/o instance binding is the same as normal function
 * member-func
   * struct {addr}
   * nil: {0}
   * addr refers a 16 bytes struct {func-addr, instance-addr}
     * addr itself is a large address
     * fmt.Print(func-addr) == fmt.Print(func)
     * func-addr is a small address
     * instance-addr is another large address (the address of instance)
   * func-addr of the same function, bound to an instance or not, is different
 * value-based member-func
   * struct {addr}
   * nil: {0}
   * addr refers {func-addr, variable-length instance}
     * value is appended after the func-addr
 * interface
   * struct {type-descriptor, addr}
   * (*MyInt)(nul): {type-descriptor, 0}
   * nil: {0 0}
 * pointer
   * struct {addr}
   * nil: {0}
   * It's just the addr of varaible
 * slice
   * struct {addr, length, capability}
   * []int{}: {addr, 0, 0}
   * nil: {0, 0, 0}
   * Slices may share memory
 * map
   * struct {addr}
   * map[int]int: {addr}
   * nil: {0}
 * string
   * struct {addr, length}
     * addr is a small address
   * nil not supported
   * "": {0, 0}
   * 'abc' and 'abcd' are not merged in normal optimizaiton

### try_comparison
 * comparable to nil
   * function
   * slice
   * map
 * comparable to instances of the same type
   * string
   * array
   * struct
 * comparable to both nil and instances of the same type
   * interface
     * equal: the same type, the same pointer or value
   * pointer
   * chan
 * struct with slice/map/function can't be compared with each other
### try_nil_impl
 * slice/map/chan
   * could be initialized as nil
   * read only
   * writing leads exception

## try_buildin_behaviors
 * slice
   * never make memory sharing/non-sharing assumption
 * reflect
   * Value-based is never settable
   * Captalized field of ptr-based is settable