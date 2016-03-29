package main

import (
	"fmt"
	"runtime"
	"unsafe"
)

type IFoo interface {
	Name() string
}
type Foo struct {
	s [98]float64
	x int64
	y int64
}

func (self *Foo) Name() string {
	return fmt.Sprintf("Foo_%d", self.x)
}

type ValueFoo struct {
	// change the size of ValueFoo to observe the optimization of value-based member-func / interface
	s [98]float64
	x int64
	y int64
}

func (self ValueFoo) Name() string {
	self.x += 1
	return fmt.Sprintf("Foo_%d", self.x)
}
func Add(x int, y int) int {
	return x + y
}

func expandInterface(src IFoo, num int) []IFoo {
	slice := make([]IFoo, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandValueInterfaceWithValue(src ValueFoo, num int) []IFoo {
	slice := make([]IFoo, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandPtrInterfaceWithPtr(src *Foo, num int) []IFoo {
	slice := make([]IFoo, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandPtr(src *Foo, num int) []*Foo {
	slice := make([]*Foo, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}
func expandFunc(src func(x int, y int) int, num int) [](func(x, y int) int) {
	slice := make([](func(x, y int) int), num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandSlice(src []int, num int) [][]int {
	slice := make([][]int, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandMap(src map[int]string, num int) []map[int]string {
	slice := make([]map[int]string, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandChan(src chan int, num int) []chan int {
	slice := make([]chan int, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func expandString(src string, num int) []string {
	slice := make([]string, num, num)
	for n := 0; n < num; n++ {
		slice[n] = src
	}
	return slice
}

func testMemory(name string, testor func(int) interface{}, sz int) {
	runtime.GC()
	var mem runtime.MemStats
	runtime.ReadMemStats(&mem)
	var beg uint64 = mem.Alloc

	testor(sz)

	runtime.ReadMemStats(&mem)
	var end uint64 = mem.Alloc
	fmt.Println(name, "avg-bytes", float64(end-beg)/float64(sz))
}

// result / M
// mem 1.1 9.1 89.3
// delta 0 8 80.2
// conclusion: a func consume 8 bytes in 64bits box
func testFunc(sz int) interface{} {
	src := Add
	ls := expandFunc(src, sz)
	return ls
}

func testMemberFunc(sz int) interface{} {
	var ls []func()string = make([]func()string, sz)
	var foo = &Foo{}
	for n:=0; n<sz; n++ {
		ls[n] = foo.Name
	}
	return ls
}
func testValueMemberFunc(sz int) interface{} {
	var ls []func()string = make([]func()string, sz)
	var foo = ValueFoo{}
	for n:=0; n<sz; n++ {
		ls[n] = foo.Name
	}
	return ls
}


func testPureMemberFunc(sz int) interface{} {
	var ls []func(*Foo)string = make([]func(*Foo)string, sz)
	for n:=0; n<sz; n++ {
		ls[n] = (*Foo).Name
	}
	return ls
}

// result / M
// mem 1.1 9.1 89.3
// delta 0 8 80.2
// conclusion: a ptr consume 8 bytes in 64bits box
func testPtr(sz int) interface{} {
	src := &Foo{x: 1}
	ls := expandPtr(src, sz)
	return ls
}

// result / M
// mem 1.1 17.1 177.4
// delta 0 16 160.3
// conclusion: a interface (wrapping a ptr) consume 16 bytes in 64bits box
func testPtrInterface(sz int) interface{} {
	src := &Foo{x: 1}
	ls := expandInterface(src, sz)
	return ls
}

// result / M
// mem 1.1 17.1 177.5
// delta 0 16 160.3
// conclusion: a interface (wrapping a value) consume 16 bytes in 64bits box
func testValueInterface(sz int) interface{} {
	src := ValueFoo{x: 1}
	ls := expandInterface(src, sz)
	return ls
}

// result / M
// mem 1.1 1015.9
// delta 0 1014.8
// conclusion: a interface (wrapping a value) initialized with value consume size(Struct) + overhead
func testValueInterfaceValueExpansion(sz int) interface{} {
	src := ValueFoo{x: 1}
	ls := expandValueInterfaceWithValue(src, sz)
	return ls
}

// result / M
// mem 1.1 17.1 177.4
// delta 0 16 160.3
// conclusion: a interface (wrapping a ptr) initialized with ptr consume 16 bytes in 64 bits box
func testPtrInterfacePtrExpansion(sz int) interface{} {
	src := &Foo{x: 1}
	ls := expandPtrInterfaceWithPtr(src, 1024*1024*10)
	return ls
}

// result / M
// mem 1.1 25.1 265.6
// delta 0 24 240.5
// conclusion: a slice consume 24 bytes in 64bits box
func testSlice(sz int) interface{} {
	var src []int = make([]int, 100, 100)
	ls := expandSlice(src, sz)
	return ls
}

// result / M
// mem 1.1 9.1 89.3
// delta 0 8 80.2
// conclusion: a map consume 8 bytes in 64bits box
func testMap(sz int) interface{} {
	var src map[int]string = make(map[int]string)
	str := "0"
	for n := 0; n < 100; n++ {
		src[n] = str
		str += "0"
	}
	ls := expandMap(src, sz)
	return ls
}

// result / M
// mem 1.1 9.1 89.3
// delta 0 8 80.2
// conclusion: a chan consume 8 bytes in 64bits box
func testChan(sz int) interface{} {
	var src chan int = make(chan int)
	ls := expandChan(src, 1024*1024*10)
	return ls
}

// results of string (len=1000) expansion: memory
// num 0 1e6 1e7
// mem 1.1 16.5 169.4
// d(mem) 0 15.4 154
// conclusion: a string occupy 16 bytes on 64bit machine

func testString(sz int) interface{} {
	seed := "1234567890"
	src := ""
	for n := 0; n < 100; n++ {
		src += seed
	}
	return expandString(src, sz)
}

func testArray(sz int) interface{} {
	var arr [10]int64 = [10]int64{0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
	var arrSlice = make([][10]int64, sz)
	for n:=0; n<sz; n++ {
		arrSlice[n] = arr
	}
	return arrSlice
}

func main() {
	var sz int = 1024*1024*10
	var foo ValueFoo
	fmt.Println("ValueFoo size", unsafe.Sizeof(foo))
	// conclusion: a func consume 8 bytes in 64bits box
	// a func bound to a pointer, consuming 24 bytes
	testMemory("func", testFunc, sz)
	testMemory("pure-member-func", testPureMemberFunc, sz)
	testMemory("ptr-member-func", testMemberFunc, sz)
	testMemory("value-member-func", testValueMemberFunc, sz/10)

	// conclusion: a interface (wrapping a ptr) consume 16 bytes in 64bits box
	testMemory("ptr-interface", testPtrInterface, sz)
	// conclusion: a interface (wrapping a value) consume 16 bytes in 64bits box
	testMemory("value-interface", testValueInterface, sz)
	// conclusion: a interface (wrapping a ptr) initialized with ptr consume 16 bytes in 64 bits box
	testMemory("ptr to interface", testPtrInterfacePtrExpansion, sz)
	// conclusion: a interface (wrapping a value) initialized with value consume size(Struct) + overhead
	testMemory("value to interface", testValueInterfaceValueExpansion, sz/10)

	// conclusion: a ptr consume 8 bytes in 64bits box
	testMemory("ptr", testPtr, sz)

	// conclusion: a slice consume 24 bytes in 64bits box
	testMemory("slice", testSlice, sz)
	// conclusion: a map consume 8 bytes in 64bits box
	testMemory("map", testMap, sz)
	// conclusion: a chan consume 8 bytes in 64bits box
	testMemory("chan", testChan, sz)
	// conclusion: a string consume 16 bytes in 64bits box
	testMemory("string", testString, sz)
	testMemory("array", testArray, sz/10)
}
